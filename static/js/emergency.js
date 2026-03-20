document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('emergencyForm');
    const getLocationBtn = document.getElementById('getLocation');
    const locationStatus = document.getElementById('locationStatus');
    const successMessage = document.getElementById('successMessage');
    
    let currentLocation = null;

    // Get current location
    getLocationBtn.addEventListener('click', function() {
        if (navigator.geolocation) {
            locationStatus.textContent = 'Getting your location...';
            getLocationBtn.disabled = true;
            
            navigator.geolocation.getCurrentPosition(
                function(position) {
                    currentLocation = {
                        latitude: position.coords.latitude,
                        longitude: position.coords.longitude
                    };
                    
                    // Get readable location name
                    locationStatus.innerHTML = 'Getting location name...';
                    getLocationName(position.coords.latitude, position.coords.longitude)
                        .then(locationName => {
                            locationStatus.innerHTML = `✅ Location: ${locationName}`;
                            currentLocation.name = locationName;
                            getLocationBtn.textContent = '✅ Location Captured';
                            getLocationBtn.style.background = '#28a745';
                        })
                        .catch(error => {
                            console.error('Geocoding error:', error);
                            locationStatus.innerHTML = `✅ Location: ${currentLocation.latitude.toFixed(4)}, ${currentLocation.longitude.toFixed(4)}`;
                            getLocationBtn.textContent = '✅ Location Captured';
                            getLocationBtn.style.background = '#28a745';
                        });
                },
                function(error) {
                    locationStatus.innerHTML = '❌ Could not get location. Please enable location services.';
                    getLocationBtn.disabled = false;
                    console.error('Location error:', error);
                }
            );
        } else {
            locationStatus.innerHTML = '❌ Geolocation is not supported by this browser.';
        }
    });

    // Handle form submission
    form.addEventListener('submit', function(e) {
        e.preventDefault();
        
        const formData = new FormData(form);
        const data = {};
        
        for (let [key, value] of formData.entries()) {
            data[key] = value;
        }
        
        // Add location if available
        if (currentLocation) {
            if (currentLocation.name) {
                data.location = `${currentLocation.name} (${currentLocation.latitude.toFixed(4)}, ${currentLocation.longitude.toFixed(4)})`;
            } else {
                data.location = `${currentLocation.latitude.toFixed(4)}, ${currentLocation.longitude.toFixed(4)}`;
            }
        }
        
        // Validate required fields
        const requiredFields = ['passenger_name', 'phone', 'train_number', 'coach', 'seat', 'emergency_type', 'description'];
        let isValid = true;
        
        requiredFields.forEach(field => {
            if (!data[field] || data[field].trim() === '') {
                isValid = false;
                document.getElementById(field).style.borderColor = '#dc3545';
            } else {
                document.getElementById(field).style.borderColor = '#ddd';
            }
        });
        
        if (!isValid) {
            alert('Please fill in all required fields.');
            return;
        }
        
        // Submit the form
        const submitBtn = form.querySelector('button[type="submit"]');
        submitBtn.disabled = true;
        submitBtn.textContent = 'Submitting...';
        
        fetch('/submit_emergency', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(data)
        })
        .then(response => response.json())
        .then(result => {
            if (result.success) {
                form.style.display = 'none';
                successMessage.style.display = 'block';
                document.getElementById('reportId').textContent = result.report_id;
                
                // Show tracking information
                if (result.train_location && result.nearest_stations) {
                    const trackingInfo = document.createElement('div');
                    trackingInfo.className = 'tracking-info';
                    trackingInfo.innerHTML = `
                        <h4>📍 Train Tracked Successfully!</h4>
                        <p><strong>Current Location:</strong> ${result.train_location.latitude.toFixed(4)}, ${result.train_location.longitude.toFixed(4)}</p>
                        <p><strong>Speed:</strong> ${result.train_location.speed} km/h</p>
                        <p><strong>Route:</strong> ${result.train_location.last_station} → ${result.train_location.next_station}</p>
                        <h4>🏥 Nearest Medical Stations Alerted:</h4>
                        ${result.nearest_stations.map(station => 
                            `<p>• ${station.name} (${station.distance_km} km) - ${station.contact}</p>`
                        ).join('')}
                        <a href="/emergency_map/${result.report_id}" class="btn" style="background: #007bff; margin-top: 10px;">
                            🗺️ View Live Tracking Map
                        </a>
                    `;
                    successMessage.appendChild(trackingInfo);
                }
                
                showNotification('Emergency submitted! Train tracked and nearby stations alerted.', 'success');
            } else {
                throw new Error(result.message || 'Failed to submit report');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            showNotification('Failed to submit emergency report. Please try again.', 'error');
            submitBtn.disabled = false;
            submitBtn.textContent = '🚨 Submit Emergency Report';
        });
    });
    
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
    
    function showNotification(message, type) {
        const notification = document.createElement('div');
        notification.className = `notification ${type}`;
        notification.textContent = message;
        notification.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            padding: 15px 20px;
            border-radius: 5px;
            color: white;
            font-weight: bold;
            z-index: 1000;
            max-width: 300px;
            ${type === 'success' ? 'background: #28a745;' : 'background: #dc3545;'}
        `;
        
        document.body.appendChild(notification);
        
        setTimeout(() => {
            notification.remove();
        }, 5000);
    }
});