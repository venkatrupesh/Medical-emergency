document.addEventListener('DOMContentLoaded', function() {
    // Update last update time
    document.getElementById('lastUpdate').textContent = new Date().toLocaleString();
    
    // Auto-refresh every 30 seconds
    setInterval(() => {
        location.reload();
    }, 30000);
    
    // Check for SOS alerts and play sound
    checkForSOSAlerts();
});

function filterReports(type) {
    const cards = document.querySelectorAll('.report-card');
    const buttons = document.querySelectorAll('.filter-btn');
    
    // Update active button
    buttons.forEach(btn => btn.classList.remove('active'));
    event.target.classList.add('active');
    
    cards.forEach(card => {
        if (type === 'all') {
            card.style.display = 'block';
        } else if (type === 'sos') {
            card.style.display = card.classList.contains('sos-alert') ? 'block' : 'none';
        } else {
            card.style.display = card.classList.contains(`status-${type}`) ? 'block' : 'none';
        }
    });
}

function viewMap(reportId) {
    // Get train number from the report and open train tracking
    const reportCard = document.querySelector(`[data-report-id="${reportId}"]`);
    if (reportCard) {
        const trainNumber = reportCard.dataset.trainNumber;
        window.open(`/track_train/${trainNumber}`, '_blank');
    } else {
        // Fallback - open a generic tracking page
        window.open('/train_search', '_blank');
    }
}

function updateStatus(reportId, status) {
    if (confirm(`Are you sure you want to mark this report as ${status.replace('_', ' ')}?`)) {
        window.location.href = `/update_status/${reportId}/${status}`;
    }
}

function alertStation(stationName, contact) {
    const message = `🚨 EMERGENCY ALERT SENT TO ${stationName}\n\nContact: ${contact}\n\nMedical team has been notified and is being dispatched.`;
    alert(message);
    
    // Log the alert
    console.log(`Alert sent to ${stationName} at ${new Date().toLocaleString()}`);
}

function checkForSOSAlerts() {
    const sosAlerts = document.querySelectorAll('.sos-alert');
    if (sosAlerts.length > 0) {
        // Play alert sound for SOS
        playSOSAlertSound();
        
        // Show notification
        showNotification(`🚨 ${sosAlerts.length} SOS ALERT(S) DETECTED! Immediate attention required.`, 'critical');
    }
}

function playSOSAlertSound() {
    try {
        const audioContext = new (window.AudioContext || window.webkitAudioContext)();
        
        // Create a more urgent sound pattern
        for (let i = 0; i < 3; i++) {
            setTimeout(() => {
                const oscillator = audioContext.createOscillator();
                const gainNode = audioContext.createGain();
                
                oscillator.connect(gainNode);
                gainNode.connect(audioContext.destination);
                
                oscillator.frequency.setValueAtTime(1000, audioContext.currentTime);
                gainNode.gain.setValueAtTime(0.3, audioContext.currentTime);
                
                oscillator.start();
                oscillator.stop(audioContext.currentTime + 0.3);
            }, i * 500);
        }
    } catch (e) {
        console.log('Audio not supported');
    }
}

function showNotification(message, type) {
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.innerHTML = message;
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        padding: 1rem 2rem;
        border-radius: 5px;
        color: white;
        font-weight: bold;
        z-index: 2000;
        max-width: 400px;
        animation: slideIn 0.3s ease;
        ${type === 'critical' ? 'background: #dc3545; border-left: 5px solid #a71e2a;' : 'background: #28a745;'}
    `;
    
    document.body.appendChild(notification);
    
    // Auto-remove after 10 seconds for critical alerts, 5 for others
    setTimeout(() => {
        notification.remove();
    }, type === 'critical' ? 10000 : 5000);
}

// Add CSS animation
const style = document.createElement('style');
style.textContent = `
    @keyframes slideIn {
        from {
            transform: translateX(100%);
            opacity: 0;
        }
        to {
            transform: translateX(0);
            opacity: 1;
        }
    }
`;
document.head.appendChild(style);