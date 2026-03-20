// Interactive Features and Animations

document.addEventListener('DOMContentLoaded', function() {
    initializeInteractiveFeatures();
});

function initializeInteractiveFeatures() {
    createParticleBackground();
    addFloatingHelpButton();
    enhanceButtons();
    addProgressBars();
    initializeToastNotifications();
    addTypingAnimation();
    addScrollAnimations();
    addRippleEffects();
}

// Particle Background Animation
function createParticleBackground() {
    const particlesContainer = document.createElement('div');
    particlesContainer.className = 'particles-bg';
    document.body.appendChild(particlesContainer);

    for (let i = 0; i < 50; i++) {
        createParticle(particlesContainer);
    }
}

function createParticle(container) {
    const particle = document.createElement('div');
    particle.className = 'particle';
    particle.style.left = Math.random() * 100 + '%';
    particle.style.animationDelay = Math.random() * 20 + 's';
    particle.style.animationDuration = (Math.random() * 10 + 10) + 's';
    container.appendChild(particle);
}

// Floating Help Button
function addFloatingHelpButton() {
    const floatingBtn = document.createElement('div');
    floatingBtn.className = 'floating-help';
    floatingBtn.innerHTML = '💬';
    floatingBtn.title = 'Need Help?';
    
    floatingBtn.addEventListener('click', function() {
        showHelpModal();
    });
    
    document.body.appendChild(floatingBtn);
}

function showHelpModal() {
    const helpContent = `
        <div style="text-align: left;">
            <h3 style="color: #2c5aa0; margin-bottom: 15px;">🆘 Quick Help Guide</h3>
            <div style="margin-bottom: 15px;">
                <strong>🚨 For Emergencies:</strong>
                <ul style="margin: 5px 0 0 20px;">
                    <li>Click the red SOS button for immediate help</li>
                    <li>Fill emergency form with accurate details</li>
                    <li>Enable location services for faster response</li>
                </ul>
            </div>
            <div style="margin-bottom: 15px;">
                <strong>📞 Emergency Numbers:</strong>
                <ul style="margin: 5px 0 0 20px;">
                    <li>Railway Emergency: 139</li>
                    <li>Medical Emergency: 1072</li>
                    <li>Fire Emergency: 101</li>
                </ul>
            </div>
            <div>
                <strong>📍 Track Your Train:</strong>
                <ul style="margin: 5px 0 0 20px;">
                    <li>Use Train Tracker for live location</li>
                    <li>View current speed and route</li>
                    <li>Get nearest station information</li>
                </ul>
            </div>
        </div>
    `;
    
    showCustomModal('Help & Support', helpContent);
}

// Enhanced Button Effects
function enhanceButtons() {
    const buttons = document.querySelectorAll('.btn-gov, .btn-gov-secondary, .sos-button');
    buttons.forEach(button => {
        button.classList.add('btn-enhanced', 'ripple');
        
        // Add hover sound effect (optional)
        button.addEventListener('mouseenter', function() {
            this.style.transform = 'translateY(-2px)';
        });
        
        button.addEventListener('mouseleave', function() {
            this.style.transform = 'translateY(0)';
        });
    });
}

// Progress Bars for Statistics
function addProgressBars() {
    const statItems = document.querySelectorAll('.stat-item');
    statItems.forEach((item, index) => {
        const number = item.querySelector('.stat-number');
        if (number) {
            const value = parseInt(number.textContent);
            const maxValue = Math.max(100, value * 1.5);
            const percentage = (value / maxValue) * 100;
            
            const progressBar = document.createElement('div');
            progressBar.className = 'progress-bar';
            progressBar.innerHTML = `<div class="progress-fill" style="--progress-width: ${percentage}%"></div>`;
            
            item.appendChild(progressBar);
        }
    });
}

// Toast Notifications
function initializeToastNotifications() {
    const toastContainer = document.createElement('div');
    toastContainer.className = 'toast-container';
    document.body.appendChild(toastContainer);
    
    // Show welcome toast
    setTimeout(() => {
        showToast('🚂 Railway Emergency System Active', 'success');
    }, 1000);
}

function showToast(message, type = 'info') {
    const toastContainer = document.querySelector('.toast-container');
    const toast = document.createElement('div');
    toast.className = 'toast';
    
    const colors = {
        success: '#28a745',
        error: '#dc3545',
        warning: '#ffc107',
        info: '#17a2b8'
    };
    
    toast.style.borderLeftColor = colors[type] || colors.info;
    toast.innerHTML = `
        <div style="display: flex; align-items: center; gap: 10px;">
            <span style="font-size: 18px;">${getToastIcon(type)}</span>
            <span>${message}</span>
            <button onclick="this.parentElement.parentElement.remove()" style="background: none; border: none; font-size: 18px; cursor: pointer; margin-left: auto;">×</button>
        </div>
    `;
    
    toastContainer.appendChild(toast);
    
    // Auto remove after 5 seconds
    setTimeout(() => {
        if (toast.parentElement) {
            toast.remove();
        }
    }, 5000);
}

function getToastIcon(type) {
    const icons = {
        success: '✅',
        error: '❌',
        warning: '⚠️',
        info: 'ℹ️'
    };
    return icons[type] || icons.info;
}

// Typing Animation for Headers
function addTypingAnimation() {
    const headers = document.querySelectorAll('h1, .page-title h2');
    headers.forEach(header => {
        const text = header.textContent;
        header.textContent = '';
        header.classList.add('typing-text');
        
        let i = 0;
        const typeWriter = () => {
            if (i < text.length) {
                header.textContent += text.charAt(i);
                i++;
                setTimeout(typeWriter, 100);
            } else {
                header.style.borderRight = 'none';
            }
        };
        
        // Start typing animation when element is visible
        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    setTimeout(typeWriter, 500);
                    observer.unobserve(entry.target);
                }
            });
        });
        
        observer.observe(header);
    });
}

// Scroll Animations
function addScrollAnimations() {
    const animatedElements = document.querySelectorAll('.dashboard-card, .stats-section, .report-item');
    
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('fade-in');
                observer.unobserve(entry.target);
            }
        });
    }, { threshold: 0.1 });
    
    animatedElements.forEach(el => {
        observer.observe(el);
    });
}

// Ripple Effects
function addRippleEffects() {
    document.addEventListener('click', function(e) {
        if (e.target.classList.contains('ripple')) {
            const ripple = document.createElement('span');
            const rect = e.target.getBoundingClientRect();
            const size = Math.max(rect.width, rect.height);
            const x = e.clientX - rect.left - size / 2;
            const y = e.clientY - rect.top - size / 2;
            
            ripple.style.cssText = `
                position: absolute;
                width: ${size}px;
                height: ${size}px;
                left: ${x}px;
                top: ${y}px;
                background: rgba(255,255,255,0.3);
                border-radius: 50%;
                transform: scale(0);
                animation: rippleEffect 0.6s ease-out;
                pointer-events: none;
            `;
            
            e.target.appendChild(ripple);
            
            setTimeout(() => {
                ripple.remove();
            }, 600);
        }
    });
    
    // Add ripple animation CSS
    const style = document.createElement('style');
    style.textContent = `
        @keyframes rippleEffect {
            to {
                transform: scale(2);
                opacity: 0;
            }
        }
    `;
    document.head.appendChild(style);
}

// Custom Modal Function
function showCustomModal(title, content) {
    const modal = document.createElement('div');
    modal.className = 'modal';
    modal.style.display = 'flex';
    modal.innerHTML = `
        <div class="modal-content" style="max-width: 600px;">
            <h3 style="margin-bottom: 20px;">${title}</h3>
            ${content}
            <div style="text-align: center; margin-top: 25px;">
                <button class="btn-gov" onclick="this.closest('.modal').remove()">Close</button>
            </div>
        </div>
    `;
    
    document.body.appendChild(modal);
    
    // Close on outside click
    modal.addEventListener('click', function(e) {
        if (e.target === modal) {
            modal.remove();
        }
    });
}

// Live Clock
function addLiveClock() {
    const clockElement = document.createElement('div');
    clockElement.style.cssText = `
        position: fixed;
        top: 10px;
        right: 10px;
        background: rgba(44, 90, 160, 0.9);
        color: white;
        padding: 5px 10px;
        border-radius: 15px;
        font-size: 12px;
        font-weight: bold;
        z-index: 1000;
    `;
    
    function updateClock() {
        const now = new Date();
        clockElement.textContent = now.toLocaleTimeString();
    }
    
    updateClock();
    setInterval(updateClock, 1000);
    document.body.appendChild(clockElement);
}

// Initialize live clock
addLiveClock();

// Emergency Alert Animation
function triggerEmergencyAlert() {
    const sosButton = document.querySelector('.sos-button');
    if (sosButton) {
        sosButton.classList.add('emergency-pulse', 'glow-effect');
    }
}

// Auto-refresh with visual indicator
function addAutoRefreshIndicator() {
    const indicator = document.createElement('div');
    indicator.style.cssText = `
        position: fixed;
        bottom: 10px;
        left: 10px;
        background: rgba(40, 167, 69, 0.9);
        color: white;
        padding: 5px 10px;
        border-radius: 15px;
        font-size: 11px;
        z-index: 1000;
        display: flex;
        align-items: center;
        gap: 5px;
    `;
    
    indicator.innerHTML = '<div class="loading-spinner" style="width: 12px; height: 12px; border-width: 2px;"></div> Auto-refresh active';
    document.body.appendChild(indicator);
}

// Initialize auto-refresh indicator
addAutoRefreshIndicator();

// Smooth page transitions
function addPageTransitions() {
    document.body.style.opacity = '0';
    document.body.style.transition = 'opacity 0.5s ease-in-out';
    
    window.addEventListener('load', function() {
        document.body.style.opacity = '1';
    });
}

addPageTransitions();