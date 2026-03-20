document.addEventListener('DOMContentLoaded', function() {
    const sosButton = document.getElementById('sosButton');
    const sosModal = document.getElementById('sosModal');
    const confirmSOS = document.getElementById('confirmSOS');
    const cancelSOS = document.getElementById('cancelSOS');

    // SOS Button functionality
    sosButton.addEventListener('click', function() {
        sosModal.style.display = 'block';
    });

    cancelSOS.addEventListener('click', function() {
        sosModal.style.display = 'none';
    });

    confirmSOS.addEventListener('click', function() {
        sendSOSAlert();
    });

    // Close modal when clicking outside
    window.addEventListener('click', function(event) {
        if (event.target === sosModal) {
            sosModal.style.display = 'none';
        }
    });

    function sendSOSAlert() {
        // Get location first
        if (navigator.geolocation) {
            navigator.geolocation.getCurrentPosition(
                function(position) {
                    // Get readable location name first
                    getLocationName(position.coords.latitude, position.coords.longitude)
                        .then(locationName => {
                            const sosData = {
                                emergency_type: 'sos',
                                passenger_name: 'SOS Alert',
                                phone: 'Emergency',
                                train_number: prompt('Enter Train Number:') || 'Unknown',
                                coach: prompt('Enter Coach:') || 'Unknown',
                                seat: prompt('Enter Seat:') || 'Unknown',
                                description: 'SOS EMERGENCY ALERT - Immediate assistance required',
                                location: `${locationName} (${position.coords.latitude.toFixed(4)}, ${position.coords.longitude.toFixed(4)})`
                            };

                            // Send SOS alert
                            fetch('/submit_emergency', {
                                method: 'POST',
                                headers: {
                                    'Content-Type': 'application/json',
                                },
                                body: JSON.stringify(sosData)
                            })
                            .then(response => response.json())
                            .then(result => {
                                if (result.success) {
                                    sosModal.style.display = 'none';
                                    showAlert('🚨 SOS ALERT SENT! Railway authorities have been notified immediately. Help is on the way!', 'success');
                                    
                                    // Play alert sound (if available)
                                    playAlertSound();
                                } else {
                                    showAlert('Failed to send SOS alert. Please try again or call 139.', 'error');
                                }
                            })
                            .catch(error => {
                                console.error('Error:', error);
                                showAlert('Failed to send SOS alert. Please call 139 immediately.', 'error');
                            });
                        })
                        .catch(error => {
                            // Fallback to coordinates if geocoding fails
                            const sosData = {
                                emergency_type: 'sos',
                                passenger_name: 'SOS Alert',
                                phone: 'Emergency',
                                train_number: prompt('Enter Train Number:') || 'Unknown',
                                coach: prompt('Enter Coach:') || 'Unknown',
                                seat: prompt('Enter Seat:') || 'Unknown',
                                description: 'SOS EMERGENCY ALERT - Immediate assistance required',
                                location: `${position.coords.latitude.toFixed(4)}, ${position.coords.longitude.toFixed(4)}`
                            };
                            
                            fetch('/submit_emergency', {
                                method: 'POST',
                                headers: {
                                    'Content-Type': 'application/json',
                                },
                                body: JSON.stringify(sosData)
                            })
                            .then(response => response.json())
                            .then(result => {
                                if (result.success) {
                                    sosModal.style.display = 'none';
                                    showAlert('🚨 SOS ALERT SENT! Railway authorities have been notified.', 'success');
                                }
                            });
                        });
                },
                function(error) {
                    // Send SOS without location
                    const sosData = {
                        emergency_type: 'sos',
                        passenger_name: 'SOS Alert',
                        phone: 'Emergency',
                        train_number: prompt('Enter Train Number:') || 'Unknown',
                        coach: prompt('Enter Coach:') || 'Unknown',
                        seat: prompt('Enter Seat:') || 'Unknown',
                        description: 'SOS EMERGENCY ALERT - Immediate assistance required',
                        location: 'Location unavailable'
                    };

                    fetch('/submit_emergency', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                        },
                        body: JSON.stringify(sosData)
                    })
                    .then(response => response.json())
                    .then(result => {
                        if (result.success) {
                            sosModal.style.display = 'none';
                            showAlert('🚨 SOS ALERT SENT! Railway authorities have been notified.', 'success');
                        }
                    });
                }
            );
        }
    }

    function playAlertSound() {
        // Create audio context for alert sound
        try {
            const audioContext = new (window.AudioContext || window.webkitAudioContext)();
            const oscillator = audioContext.createOscillator();
            const gainNode = audioContext.createGain();
            
            oscillator.connect(gainNode);
            gainNode.connect(audioContext.destination);
            
            oscillator.frequency.setValueAtTime(800, audioContext.currentTime);
            gainNode.gain.setValueAtTime(0.3, audioContext.currentTime);
            
            oscillator.start();
            oscillator.stop(audioContext.currentTime + 0.5);
        } catch (e) {
            console.log('Audio not supported');
        }
    }

    function showAlert(message, type) {
        const alert = document.createElement('div');
        alert.className = `alert alert-${type}`;
        alert.innerHTML = message;
        alert.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            padding: 1rem 2rem;
            border-radius: 5px;
            color: white;
            font-weight: bold;
            z-index: 2000;
            max-width: 400px;
            ${type === 'success' ? 'background: #28a745;' : 'background: #dc3545;'}
        `;
        
        document.body.appendChild(alert);
        
        setTimeout(() => {
            alert.remove();
        }, 5000);
    }
});

function showContacts() {
    alert(`🚨 EMERGENCY CONTACTS 🚨\n\nRailway Emergency: 139\nMedical Emergency: 1072\nFire Emergency: 101\nPolice: 100\n\nFor immediate assistance, call these numbers directly.`);
}

function trackTrain() {
    const trainNumber = prompt('Enter your train number:');
    if (trainNumber) {
        fetch(`/track_train/${trainNumber}`)
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    const location = data.train_location;
                    alert(`🚂 TRAIN TRACKING\n\nTrain: ${location.train_name}\nCurrent Speed: ${location.speed} km/h\nLocation: ${location.latitude}, ${location.longitude}\nRoute: ${location.last_station} → ${location.next_station}`);
                } else {
                    alert('Train not found. Please check the train number.');
                }
            })
            .catch(error => {
                alert('Unable to track train at the moment.');
            });
    }
}

function getLocationName(lat, lng) {
    return new Promise((resolve, reject) => {
        // Method 1: OpenStreetMap Nominatim (Free)
        fetch(`https://nominatim.openstreetmap.org/reverse?format=json&lat=${lat}&lon=${lng}&zoom=14&addressdetails=1`)
            .then(response => response.json())
            .then(data => {
                if (data && data.display_name) {
                    const address = data.address || {};
                    const locationParts = [];
                    
                    if (address.village) locationParts.push(address.village);
                    else if (address.town) locationParts.push(address.town);
                    else if (address.city) locationParts.push(address.city);
                    else if (address.county) locationParts.push(address.county);
                    
                    if (address.state) locationParts.push(address.state);
                    
                    const locationName = locationParts.length > 0 ? locationParts.join(', ') : data.display_name.split(',').slice(0, 3).join(', ');
                    resolve(locationName);
                } else {
                    throw new Error('No location found');
                }
            })
            .catch(error => {
                // Method 2: Backup geocoding service
                fetch(`https://api.bigdatacloud.net/data/reverse-geocode-client?latitude=${lat}&longitude=${lng}&localityLanguage=en`)
                    .then(response => response.json())
                    .then(data => {
                        if (data && (data.locality || data.city)) {
                            const locationParts = [];
                            if (data.locality) locationParts.push(data.locality);
                            if (data.city && data.city !== data.locality) locationParts.push(data.city);
                            if (data.principalSubdivision) locationParts.push(data.principalSubdivision);
                            
                            resolve(locationParts.join(', ') || 'Unknown Location');
                        } else {
                            reject(new Error('No location data available'));
                        }
                    })
                    .catch(err => {
                        reject(new Error('All geocoding services failed'));
                    });
            });
    });
}

function viewReports() {
    alert('Feature coming soon! You will be able to view all your submitted emergency reports here.');
}