// User Interface JavaScript
// Enhanced interactions and animations

document.addEventListener('DOMContentLoaded', function() {
    // Smooth scroll for anchor links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });

    // Add fade-in animation to cards on scroll
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    };

    const observer = new IntersectionObserver(function(entries) {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.style.opacity = '1';
                entry.target.style.transform = 'translateY(0)';
            }
        });
    }, observerOptions);

    // Observe all cards
    document.querySelectorAll('.card, .glass-card, .results-card').forEach(card => {
        card.style.opacity = '0';
        card.style.transform = 'translateY(20px)';
        card.style.transition = 'opacity 0.6s ease, transform 0.6s ease';
        observer.observe(card);
    });

    // Enhanced file input preview
    const fileInput = document.getElementById('fileInput');
    const uploadArea = document.getElementById('uploadArea');
    const uploadText = document.querySelector('.upload-text');
    const submitBtn = document.getElementById('submitBtn');

    if (fileInput && uploadArea && uploadText) {
        // Click to upload
        uploadArea.addEventListener('click', () => fileInput.click());

        // Drag and drop handlers
        uploadArea.addEventListener('dragover', (e) => {
            e.preventDefault();
            uploadArea.classList.add('dragover');
        });

        uploadArea.addEventListener('dragleave', () => {
            uploadArea.classList.remove('dragover');
        });

        uploadArea.addEventListener('drop', (e) => {
            e.preventDefault();
            uploadArea.classList.remove('dragover');
            const files = e.dataTransfer.files;
            if (files.length > 0) {
                fileInput.files = files;
                updateUploadText(files[0]);
            }
        });

        // File input change
        fileInput.addEventListener('change', (e) => {
            if (e.target.files.length > 0) {
                updateUploadText(e.target.files[0]);
            }
        });

        function updateUploadText(file) {
            const fileSize = (file.size / 1024 / 1024).toFixed(2);
            uploadText.innerHTML = `
                <div class="upload-main">✅ File selected: ${file.name}</div>
                <div class="upload-sub">${fileSize} MB • Ready to process</div>
            `;
            if (submitBtn) {
                submitBtn.disabled = false;
                submitBtn.style.opacity = '1';
            }
        }
    }

    // Form submission loading state
    const uploadForm = document.getElementById('uploadForm');
    if (uploadForm && submitBtn) {
        uploadForm.addEventListener('submit', function(e) {
            submitBtn.innerHTML = '<span>⏳</span> Processing...';
            submitBtn.disabled = true;
            submitBtn.style.opacity = '0.7';
            
            // Add loading animation
            uploadArea.style.opacity = '0.6';
            uploadArea.style.pointerEvents = 'none';
        });
    }

    // Copy to clipboard with feedback
    window.copyResults = function() {
        const results = document.querySelectorAll('.plate-text-display');
        let text = '🚗 AI Number Plate Detection Results\n\n';
        results.forEach((result, index) => {
            text += `Plate ${index + 1}: ${result.textContent}\n`;
        });
        text += `\nProcessed in ${document.querySelector('.summary-content p')?.textContent || 'N/A'}`;

        navigator.clipboard.writeText(text).then(() => {
            const btn = event.target.closest('button');
            if (btn) {
                const originalText = btn.innerHTML;
                btn.innerHTML = '<span>✅</span> Copied!';
                btn.style.background = 'linear-gradient(135deg, #10b981 0%, #059669 100%)';
                btn.style.transform = 'scale(1.05)';
                
                setTimeout(() => {
                    btn.innerHTML = originalText;
                    btn.style.background = '';
                    btn.style.transform = '';
                }, 2000);
            }
        }).catch(err => {
            console.error('Failed to copy:', err);
            alert('Failed to copy results. Please try again.');
        });
    };

    // Add ripple effect to buttons
    document.querySelectorAll('.btn').forEach(button => {
        button.addEventListener('click', function(e) {
            const ripple = document.createElement('span');
            const rect = this.getBoundingClientRect();
            const size = Math.max(rect.width, rect.height);
            const x = e.clientX - rect.left - size / 2;
            const y = e.clientY - rect.top - size / 2;
            
            ripple.style.width = ripple.style.height = size + 'px';
            ripple.style.left = x + 'px';
            ripple.style.top = y + 'px';
            ripple.classList.add('ripple');
            
            this.appendChild(ripple);
            
            setTimeout(() => {
                ripple.remove();
            }, 600);
        });
    });

    // Add print styles dynamically
    const printStyles = `
        <style>
        @media print {
            .navbar, .action-section, .footer, .btn { display: none !important; }
            .container { padding: 0 !important; }
            .results-section { margin-top: 0 !important; }
            .results-header-section { text-align: center; margin-bottom: 40px; }
            body { background: white !important; color: black !important; }
            .results-card, .glass-card { 
                box-shadow: none !important; 
                border: 1px solid #ccc !important;
                background: white !important;
            }
            .confidence-fill { background: #333 !important; }
        }
        </style>
    `;
    document.head.insertAdjacentHTML('beforeend', printStyles);
});

// Add ripple effect CSS
const rippleStyle = document.createElement('style');
rippleStyle.textContent = `
    .btn {
        position: relative;
        overflow: hidden;
    }
    .ripple {
        position: absolute;
        border-radius: 50%;
        background: rgba(255, 255, 255, 0.6);
        transform: scale(0);
        animation: ripple-animation 0.6s ease-out;
        pointer-events: none;
    }
    @keyframes ripple-animation {
        to {
            transform: scale(4);
            opacity: 0;
        }
    }
`;
document.head.appendChild(rippleStyle);
