# app/services/vehicle_service.py
"""
Vehicle verification service for fuel station ANPR system.
Handles blacklist checking, age calculation from database, and restriction logic.
"""
import re
from datetime import datetime
from app.models import Blacklist, Vehicle, db

def estimate_vehicle_age(plate_text):
    """
    Estimate vehicle age from registration number.
    
    Indian number plate formats:
    - Old format: XX##XX#### (e.g., MH12AB1234) - 2 digits after state code indicate year
    - New format: XX##XX#### (e.g., MH12AB1234) - First 2 digits after state code
    - Some states use single digit or different formats
    
    Returns:
        dict: {
            'estimated_year': int or None,
            'estimated_age': int or None,
            'extraction_method': str
        }
    """
    if not plate_text:
        return {'estimated_year': None, 'estimated_age': None, 'extraction_method': 'none'}
    
    plate_clean = plate_text.upper().replace(' ', '').replace('-', '')
    current_year = datetime.now().year
    
    # Method 1: Extract year from standard Indian format (XX##XX####)
    # Pattern: 2 letters (state) + 2 digits (year code) + 2 letters + 4 digits
    pattern1 = r'^[A-Z]{2}(\d{2})[A-Z]{1,2}\d{1,4}$'
    match1 = re.match(pattern1, plate_clean)
    
    if match1:
        year_code = int(match1.group(1))
        # Indian RTO year codes: 00-99 map to 2000-2099
        # But older vehicles might use 00-99 for 1900-1999
        # We'll assume 00-30 = 2000-2030, 31-99 = 1931-1999
        if year_code <= 30:
            estimated_year = 2000 + year_code
        else:
            estimated_year = 1900 + year_code
        
        age = current_year - estimated_year
        return {
            'estimated_year': estimated_year,
            'estimated_age': max(0, age),  # Ensure non-negative
            'extraction_method': 'rto_year_code'
        }
    
    # Method 2: Look for 4-digit year in the plate (less common)
    pattern2 = r'(\d{4})'
    matches2 = re.findall(pattern2, plate_clean)
    for match in matches2:
        year = int(match)
        if 1950 <= year <= current_year:
            age = current_year - year
            return {
                'estimated_year': year,
                'estimated_age': max(0, age),
                'extraction_method': 'embedded_year'
            }
    
    # Method 3: Extract first 2 digits after letters (fallback)
    pattern3 = r'^[A-Z]+(\d{2})'
    match3 = re.match(pattern3, plate_clean)
    if match3:
        year_code = int(match3.group(1))
        if year_code <= 30:
            estimated_year = 2000 + year_code
        else:
            estimated_year = 1900 + year_code
        
        if 1950 <= estimated_year <= current_year:
            age = current_year - estimated_year
            return {
                'estimated_year': estimated_year,
                'estimated_age': max(0, age),
                'extraction_method': 'fallback_year_code'
            }
    
    return {'estimated_year': None, 'estimated_age': None, 'extraction_method': 'none'}


def get_vehicle_by_plate(plate_text):
    """
    Query vehicle from database by registration number.
    Handles both formats: "SN66 XMZ" and "SN66XMZ"
    
    Args:
        plate_text: Extracted number plate text
    
    Returns:
        Vehicle object or None if not found
    """
    if not plate_text:
        return None
    
    plate_upper = plate_text.upper().strip()
    plate_no_spaces = plate_upper.replace(' ', '').replace('-', '')
    
    # Try exact match (no spaces)
    vehicle = Vehicle.query.filter_by(registration_number=plate_no_spaces).first()
    if vehicle:
        return vehicle
    
    # Try exact match (with spaces)
    vehicle = Vehicle.query.filter_by(registration_number=plate_upper).first()
    if vehicle:
        return vehicle
    
    # Try case-insensitive search without spaces
    from sqlalchemy import func
    vehicle = Vehicle.query.filter(
        func.replace(Vehicle.registration_number, ' ', '').ilike(f'%{plate_no_spaces}%')
    ).first()
    
    return vehicle


def check_vehicle_status(plate_text, max_age_years=10):
    """
    Check vehicle status against database, blacklist, and age restrictions.
    
    Args:
        plate_text: Extracted number plate text
        max_age_years: Maximum allowed vehicle age (default: 10 years)
    
    Returns:
        dict: {
            'status': 'safe' | 'blacklisted' | 'age_restricted' | 'not_found',
            'is_blacklisted': bool,
            'is_age_restricted': bool,
            'vehicle': Vehicle object or None,
            'vehicle_age': int or None,
            'message': str
        }
    """
    if not plate_text:
        return {
            'status': 'not_found',
            'is_blacklisted': False,
            'is_age_restricted': False,
            'vehicle': None,
            'vehicle_age': None,
            'message': 'No plate text provided'
        }
    
    plate_upper = plate_text.upper().strip()
    
    # Check blacklist table first
    is_blacklisted_in_table = Blacklist.query.filter_by(plate_text=plate_upper).first() is not None
    
    # Query vehicle from database
    vehicle = get_vehicle_by_plate(plate_upper)
    
    # Check if vehicle is blacklisted (either in blacklist table or vehicle record)
    is_blacklisted = is_blacklisted_in_table
    if vehicle and vehicle.is_blacklisted():
        is_blacklisted = True
    
    if is_blacklisted:
        return {
            'status': 'blacklisted',
            'is_blacklisted': True,
            'is_age_restricted': False,
            'vehicle': vehicle,
            'vehicle_age': vehicle.calculate_age() if vehicle else None,
            'message': '⚠️ VEHICLE BLACKLISTED - Fuel dispensing denied!'
        }
    
    # If vehicle not found in database
    if not vehicle:
        return {
            'status': 'not_found',
            'is_blacklisted': False,
            'is_age_restricted': False,
            'vehicle': None,
            'vehicle_age': None,
            'message': '⚠️ Vehicle not found in database. Please verify registration number.'
        }
    
    # Check age restrictions using actual registration year from database
    vehicle_age = vehicle.calculate_age()
    is_age_restricted = vehicle.is_old_vehicle(max_age_years)
    
    if is_age_restricted:
        return {
            'status': 'age_restricted',
            'is_blacklisted': False,
            'is_age_restricted': True,
            'vehicle': vehicle,
            'vehicle_age': vehicle_age,
            'message': f'⚠️ Vehicle is old – Do not pour petrol (Age: {vehicle_age} years, Limit: {max_age_years} years)'
        }
    
    # Safe vehicle - within age limit and not blacklisted
    return {
        'status': 'safe',
        'is_blacklisted': False,
        'is_age_restricted': False,
        'vehicle': vehicle,
        'vehicle_age': vehicle_age,
        'message': f'✅ Vehicle verified - Safe to refuel (Age: {vehicle_age} years)'
    }
