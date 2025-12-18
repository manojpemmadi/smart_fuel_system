# app/services/vehicle_service.py
"""
Vehicle verification service for fuel station ANPR system.
Handles blacklist checking, age estimation, and restriction logic.
"""
import re
from datetime import datetime
from app.models import Blacklist, db

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


def check_vehicle_status(plate_text, max_age_years=None):
    """
    Check vehicle status against blacklist and age restrictions.
    
    Args:
        plate_text: Extracted number plate text
        max_age_years: Maximum allowed vehicle age (from config)
    
    Returns:
        dict: {
            'status': 'safe' | 'blacklisted' | 'age_restricted',
            'is_blacklisted': bool,
            'is_age_restricted': bool,
            'age_info': dict from estimate_vehicle_age(),
            'message': str
        }
    """
    if not plate_text:
        return {
            'status': 'safe',
            'is_blacklisted': False,
            'is_age_restricted': False,
            'age_info': {'estimated_year': None, 'estimated_age': None},
            'message': 'No plate text provided'
        }
    
    plate_upper = plate_text.upper().strip()
    
    # Check blacklist
    is_blacklisted = Blacklist.query.filter_by(plate_text=plate_upper).first() is not None
    
    if is_blacklisted:
        return {
            'status': 'blacklisted',
            'is_blacklisted': True,
            'is_age_restricted': False,
            'age_info': {'estimated_year': None, 'estimated_age': None},
            'message': '⚠️ VEHICLE BLACKLISTED - Fuel dispensing denied!'
        }
    
    # Check age restrictions
    age_info = estimate_vehicle_age(plate_upper)
    is_age_restricted = False
    
    if max_age_years and age_info['estimated_age'] is not None:
        if age_info['estimated_age'] > max_age_years:
            is_age_restricted = True
            return {
                'status': 'age_restricted',
                'is_blacklisted': False,
                'is_age_restricted': True,
                'age_info': age_info,
                'message': f'⚠️ VEHICLE AGE RESTRICTED - Vehicle age ({age_info["estimated_age"]} years) exceeds limit ({max_age_years} years). Fuel dispensing denied!'
            }
    
    # Safe vehicle
    age_msg = ""
    if age_info['estimated_age'] is not None:
        age_msg = f" (Estimated age: {age_info['estimated_age']} years)"
    
    return {
        'status': 'safe',
        'is_blacklisted': False,
        'is_age_restricted': False,
        'age_info': age_info,
        'message': f'✅ Vehicle verified - Safe to refuel{age_msg}'
    }
