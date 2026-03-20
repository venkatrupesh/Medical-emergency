// Enhanced Location Detection and Display
// Provides accurate location detection and reverse geocoding

(function() {
    'use strict';
    
    let currentLocation = null;
    let locationName = null;
    
    // Get accurate location with multiple fallback methods
    function getAccurateLocation() {
        return new Promise((resolve, reject) => {
            if (!navigator.geolocation) {
                reject(new Error('Geolocation is not supported by your browser'));
                return;
            }
            
            const options = {
                enableHighAccuracy: true,
                timeout: 10000,
                maximumAge: 0
            };
            
            navigator.geolocation.getCurrentPosition(
                async (position) => {
                    const coords = {
                        latitude: position.coords.latitude,
                        longitude: position.coords.longitude,
                        accuracy: position.coords.accuracy || null
                    };
                    
                    currentLocation = coords;
                    
                    // Get location name
                    try {
                        const name = await getLocationName(coords.latitude, coords.longitude);
                        locationName = name;
                        resolve({
                            coords: coords,
                            name: name,
                            full: `${name} (${coords.latitude.toFixed(6)}, ${coords.longitude.toFixed(6)})`
                        });
                    } catch (error) {
                        // Return coordinates even if name lookup fails
                        resolve({
                            coords: coords,
                            name: 'Location',
                            full: `${coords.latitude.toFixed(6)}, ${coords.longitude.toFixed(6)}`
                        });
                    }
                },
                (error) => {
                    let errorMessage = 'Unable to get location';
                    switch(error.code) {
                        case error.PERMISSION_DENIED:
                            errorMessage = 'Location permission denied. Please enable location access.';
                            break;
                        case error.POSITION_UNAVAILABLE:
                            errorMessage = 'Location information unavailable.';
                            break;
                        case error.TIMEOUT:
                            errorMessage = 'Location request timed out.';
                            break;
                    }
                    reject(new Error(errorMessage));
                },
                options
            );
        });
    }
    
    // Get location name from coordinates (reverse geocoding)
    async function getLocationName(lat, lng) {
        // Try multiple geocoding services for better accuracy
        
        // Method 1: OpenStreetMap Nominatim
        try {
            const response = await fetch(
                `https://nominatim.openstreetmap.org/reverse?format=json&lat=${lat}&lon=${lng}&zoom=14&addressdetails=1`,
                {
                    headers: {
                        'User-Agent': 'RailwayEmergencySystem/1.0'
                    }
                }
            );
            
            if (response.ok) {
                const data = await response.json();
                if (data && data.address) {
                    const addr = data.address;
                    const parts = [];
                    
                    // Build location name from address components
                    if (addr.village) parts.push(addr.village);
                    else if (addr.town) parts.push(addr.town);
                    else if (addr.city) parts.push(addr.city);
                    else if (addr.municipality) parts.push(addr.municipality);
                    
                    if (addr.county && !parts.includes(addr.county)) parts.push(addr.county);
                    if (addr.state) parts.push(addr.state);
                    
                    if (parts.length > 0) {
                        return parts.join(', ');
                    }
                    
                    // Fallback to display_name
                    if (data.display_name) {
                        return data.display_name.split(',').slice(0, 3).join(', ');
                    }
                }
            }
        } catch (e) {
            console.log('Nominatim geocoding failed, trying alternative...');
        }
        
        // Method 2: BigDataCloud API
        try {
            const response = await fetch(
                `https://api.bigdatacloud.net/data/reverse-geocode-client?latitude=${lat}&longitude=${lng}&localityLanguage=en`
            );
            
            if (response.ok) {
                const data = await response.json();
                if (data) {
                    const parts = [];
                    if (data.locality) parts.push(data.locality);
                    if (data.city && data.city !== data.locality) parts.push(data.city);
                    if (data.principalSubdivision) parts.push(data.principalSubdivision);
                    if (data.countryName) parts.push(data.countryName);
                    
                    if (parts.length > 0) {
                        return parts.join(', ');
                    }
                }
            }
        } catch (e) {
            console.log('BigDataCloud geocoding failed');
        }
        
        // Method 3: Mapbox (if API key available)
        // This would require API key configuration
        
        // Fallback: Return coordinates as location
        return `Lat: ${lat.toFixed(4)}, Lng: ${lng.toFixed(4)}`;
    }
    
    // Display location in an element
    function displayLocation(elementId, locationData) {
        const element = document.getElementById(elementId);
        if (!element) return;
        
        if (locationData.name) {
            element.innerHTML = `
                <strong>📍 Location:</strong> ${locationData.name}<br>
                <small style="color: var(--text-muted);">
                    Coordinates: ${locationData.coords.latitude.toFixed(6)}, ${locationData.coords.longitude.toFixed(6)}
                    ${locationData.coords.accuracy ? `(Accuracy: ±${Math.round(locationData.coords.accuracy)}m)` : ''}
                </small>
            `;
        } else {
            element.textContent = `Location: ${locationData.full}`;
        }
        
        element.style.display = 'block';
    }
    
    // Watch location continuously
    function watchLocation(callback) {
        if (!navigator.geolocation) {
            callback(null, new Error('Geolocation not supported'));
            return null;
        }
        
        const watchId = navigator.geolocation.watchPosition(
            async (position) => {
                const coords = {
                    latitude: position.coords.latitude,
                    longitude: position.coords.longitude,
                    accuracy: position.coords.accuracy || null
                };
                
                try {
                    const name = await getLocationName(coords.latitude, coords.longitude);
                    callback({
                        coords: coords,
                        name: name,
                        full: `${name} (${coords.latitude.toFixed(6)}, ${coords.longitude.toFixed(6)})`
                    }, null);
                } catch (error) {
                    callback({
                        coords: coords,
                        name: 'Location',
                        full: `${coords.latitude.toFixed(6)}, ${coords.longitude.toFixed(6)}`
                    }, null);
                }
            },
            (error) => {
                callback(null, error);
            },
            {
                enableHighAccuracy: true,
                timeout: 10000,
                maximumAge: 5000
            }
        );
        
        return watchId;
    }
    
    // Stop watching location
    function stopWatchingLocation(watchId) {
        if (watchId && navigator.geolocation) {
            navigator.geolocation.clearWatch(watchId);
        }
    }
    
    // Export functions
    window.locationService = {
        getAccurateLocation: getAccurateLocation,
        getLocationName: getLocationName,
        displayLocation: displayLocation,
        watchLocation: watchLocation,
        stopWatchingLocation: stopWatchingLocation,
        getCurrentLocation: () => currentLocation,
        getCurrentLocationName: () => locationName
    };
})();