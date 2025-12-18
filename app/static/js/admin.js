// Admin Interface JavaScript
// Enhanced admin panel interactions

document.addEventListener('DOMContentLoaded', function() {
    // Smooth animations for admin cards
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    };

    const observer = new IntersectionObserver(function(entries) {
        entries.forEach((entry, index) => {
            if (entry.isIntersecting) {
                setTimeout(() => {
                    entry.target.style.opacity = '1';
                    entry.target.style.transform = 'translateY(0)';
                }, index * 100);
            }
        });
    }, observerOptions);

    // Observe admin cards
    document.querySelectorAll('.stat-card, .action-card, .glass-card').forEach(card => {
        card.style.opacity = '0';
        card.style.transform = 'translateY(20px)';
        card.style.transition = 'opacity 0.6s ease, transform 0.6s ease';
        observer.observe(card);
    });

    // Enhanced form validation
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        form.addEventListener('submit', function(e) {
            const inputs = form.querySelectorAll('input[required]');
            let isValid = true;
            
            inputs.forEach(input => {
                if (!input.value.trim()) {
                    isValid = false;
                    input.style.borderColor = 'var(--accent-red)';
                    input.style.boxShadow = '0 0 0 3px rgba(239, 68, 68, 0.1)';
                    
                    setTimeout(() => {
                        input.style.borderColor = '';
                        input.style.boxShadow = '';
                    }, 3000);
                }
            });
            
            if (!isValid) {
                e.preventDefault();
                showNotification('Please fill in all required fields', 'error');
            }
        });
    });

    // Auto-uppercase for plate inputs
    const plateInputs = document.querySelectorAll('input[name="plate"], input[id="plate"]');
    plateInputs.forEach(input => {
        input.addEventListener('input', function(e) {
            e.target.value = e.target.value.toUpperCase();
        });
    });

    // Confirmation dialogs with better styling
    const deleteForms = document.querySelectorAll('.delete-form');
    deleteForms.forEach(form => {
        form.addEventListener('submit', function(e) {
            if (!confirm('Are you sure you want to remove this plate from blacklist?')) {
                e.preventDefault();
            }
        });
    });

    // Real-time search for detection history
    const searchInput = document.getElementById('searchInput');
    if (searchInput) {
        let searchTimeout;
        searchInput.addEventListener('input', function(e) {
            clearTimeout(searchTimeout);
            const searchTerm = e.target.value.toLowerCase().trim();
            
            searchTimeout = setTimeout(() => {
                const table = document.getElementById('detectionsTable');
                if (table) {
                    const rows = table.querySelectorAll('tbody tr');
                    let visibleCount = 0;
                    
                    rows.forEach(row => {
                        const plateText = row.querySelector('.plate-text')?.textContent.toLowerCase() || '';
                        if (plateText.includes(searchTerm)) {
                            row.style.display = '';
                            visibleCount++;
                        } else {
                            row.style.display = 'none';
                        }
                    });
                    
                    // Show "no results" message if needed
                    let noResultsMsg = table.parentElement.querySelector('.no-results-msg');
                    if (searchTerm && visibleCount === 0) {
                        if (!noResultsMsg) {
                            noResultsMsg = document.createElement('div');
                            noResultsMsg.className = 'no-results-msg';
                            noResultsMsg.innerHTML = `
                                <div style="text-align: center; padding: 2rem; color: var(--text-tertiary);">
                                    <span style="font-size: 2rem; display: block; margin-bottom: 0.5rem;">🔍</span>
                                    <p>No detections found matching "${searchTerm}"</p>
                                </div>
                            `;
                            table.parentElement.appendChild(noResultsMsg);
                        }
                    } else if (noResultsMsg) {
                        noResultsMsg.remove();
                    }
                }
            }, 300);
        });
    }

    // Notification system
    window.showNotification = function(message, type = 'info') {
        const notification = document.createElement('div');
        notification.className = `notification notification-${type}`;
        notification.innerHTML = `
            <span class="notification-icon">${type === 'error' ? '⚠️' : type === 'success' ? '✅' : 'ℹ️'}</span>
            <span class="notification-message">${message}</span>
        `;
        
        document.body.appendChild(notification);
        
        setTimeout(() => {
            notification.classList.add('show');
        }, 10);
        
        setTimeout(() => {
            notification.classList.remove('show');
            setTimeout(() => {
                notification.remove();
            }, 300);
        }, 3000);
    };

    // Add notification styles
    const notificationStyle = document.createElement('style');
    notificationStyle.textContent = `
        .notification {
            position: fixed;
            top: 100px;
            right: 20px;
            background: var(--bg-glass);
            backdrop-filter: blur(20px);
            border: 1px solid var(--border-color);
            border-radius: var(--radius-md);
            padding: 1rem 1.5rem;
            display: flex;
            align-items: center;
            gap: 0.75rem;
            box-shadow: var(--shadow-xl);
            z-index: 10000;
            opacity: 0;
            transform: translateX(400px);
            transition: all 0.3s ease;
            max-width: 400px;
        }
        .notification.show {
            opacity: 1;
            transform: translateX(0);
        }
        .notification-error {
            border-color: rgba(239, 68, 68, 0.3);
            background: rgba(239, 68, 68, 0.1);
        }
        .notification-success {
            border-color: rgba(16, 185, 129, 0.3);
            background: rgba(16, 185, 129, 0.1);
        }
        .notification-icon {
            font-size: 1.25rem;
        }
        .notification-message {
            color: var(--text-primary);
            font-weight: 500;
        }
    `;
    document.head.appendChild(notificationStyle);

    // Flash message handling
    const flashMessages = document.querySelectorAll('.alert, [class*="flash"]');
    flashMessages.forEach(msg => {
        setTimeout(() => {
            msg.style.opacity = '0';
            msg.style.transform = 'translateY(-10px)';
            setTimeout(() => {
                msg.remove();
            }, 300);
        }, 5000);
    });

    // Add loading states to buttons
    document.querySelectorAll('form').forEach(form => {
        form.addEventListener('submit', function(e) {
            const submitBtn = form.querySelector('button[type="submit"]');
            if (submitBtn && !submitBtn.disabled) {
                const originalText = submitBtn.innerHTML;
                submitBtn.innerHTML = '<span>⏳</span> Processing...';
                submitBtn.disabled = true;
                
                // Re-enable after 10 seconds as fallback
                setTimeout(() => {
                    submitBtn.innerHTML = originalText;
                    submitBtn.disabled = false;
                }, 10000);
            }
        });
    });
});
