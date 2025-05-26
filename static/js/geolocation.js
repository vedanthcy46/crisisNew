/**
 * Crisis Management System - Geolocation Helper
 * Handles geolocation functionality for incident reporting
 */

/**
 * Get current user location
 */
function getCurrentLocation(successCallback, errorCallback) {
    if (!navigator.geolocation) {
        const error = new Error('Geolocation is not supported by this browser');
        if (errorCallback) errorCallback(error);
        return;
    }
    
    const options = {
        enableHighAccuracy: true,
        timeout: 10000,
        maximumAge: 60000 // Cache for 1 minute
    };
    
    navigator.geolocation.getCurrentPosition(
        successCallback,
        errorCallback,
        options
    );
}

/**
 * Watch user location for continuous tracking
 */
function watchLocation(successCallback, errorCallback) {
    if (!navigator.geolocation) {
        const error = new Error('Geolocation is not supported by this browser');
        if (errorCallback) errorCallback(error);
        return null;
    }
    
    const options = {
        enableHighAccuracy: true,
        timeout: 10000,
        maximumAge: 30000
    };
    
    return navigator.geolocation.watchPosition(
        successCallback,
        errorCallback,
        options
    );
}

/**
 * Stop watching user location
 */
function stopWatchingLocation(watchId) {
    if (watchId && navigator.geolocation) {
        navigator.geolocation.clearWatch(watchId);
    }
}

/**
 * Reverse geocode coordinates to address
 */
function reverseGeocode(latitude, longitude, callback) {
    // Using a simple reverse geocoding service
    // In production, you might want to use Google Maps API, Mapbox, or similar
    const url = `https://api.bigdatacloud.net/data/reverse-geocode-client?latitude=${latitude}&longitude=${longitude}&localityLanguage=en`;
    
    fetch(url)
        .then(response => response.json())
        .then(data => {
            let address = '';
            
            if (data.locality || data.city) {
                address += (data.locality || data.city) + ', ';
            }
            
            if (data.principalSubdivision) {
                address += data.principalSubdivision + ', ';
            }
            
            if (data.countryName) {
                address += data.countryName;
            }
            
            // Fallback to displaying coordinates if address is empty
            if (!address.trim()) {
                address = `${latitude.toFixed(6)}, ${longitude.toFixed(6)}`;
            }
            
            callback(address.trim().replace(/,$/, ''));
        })
        .catch(error => {
            console.error('Reverse geocoding failed:', error);
            // Fallback to coordinates
            callback(`${latitude.toFixed(6)}, ${longitude.toFixed(6)}`);
        });
}

/**
 * Calculate distance between two coordinates (in kilometers)
 */
function calculateDistance(lat1, lon1, lat2, lon2) {
    const R = 6371; // Earth's radius in kilometers
    const dLat = toRadians(lat2 - lat1);
    const dLon = toRadians(lon2 - lon1);
    
    const a = Math.sin(dLat / 2) * Math.sin(dLat / 2) +
              Math.cos(toRadians(lat1)) * Math.cos(toRadians(lat2)) *
              Math.sin(dLon / 2) * Math.sin(dLon / 2);
    
    const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
    const distance = R * c;
    
    return distance;
}

/**
 * Convert degrees to radians
 */
function toRadians(degrees) {
    return degrees * (Math.PI / 180);
}

/**
 * Format coordinates for display
 */
function formatCoordinates(latitude, longitude, precision = 6) {
    return `${latitude.toFixed(precision)}, ${longitude.toFixed(precision)}`;
}

/**
 * Validate coordinates
 */
function validateCoordinates(latitude, longitude) {
    const lat = parseFloat(latitude);
    const lon = parseFloat(longitude);
    
    return !isNaN(lat) && !isNaN(lon) &&
           lat >= -90 && lat <= 90 &&
           lon >= -180 && lon <= 180;
}

/**
 * Get user-friendly error message for geolocation errors
 */
function getGeolocationErrorMessage(error) {
    switch (error.code) {
        case error.PERMISSION_DENIED:
            return "Location access denied. Please enable location permissions in your browser settings.";
        case error.POSITION_UNAVAILABLE:
            return "Location information is unavailable. Please try again or enter your location manually.";
        case error.TIMEOUT:
            return "Location request timed out. Please try again or enter your location manually.";
        default:
            return "An unknown error occurred while retrieving your location. Please enter your location manually.";
    }
}

/**
 * Auto-fill location fields when geolocation is available
 */
function autoFillLocation(options = {}) {
    const {
        latitudeField = 'latitude',
        longitudeField = 'longitude',
        addressField = 'address',
        button = null,
        onSuccess = null,
        onError = null
    } = options;
    
    const latField = document.getElementById(latitudeField);
    const lonField = document.getElementById(longitudeField);
    const addrField = document.getElementById(addressField);
    const btn = button || document.getElementById('getLocationBtn');
    
    if (!latField || !lonField) {
        console.error('Latitude and longitude fields are required');
        return;
    }
    
    if (btn) {
        btn.disabled = true;
        btn.innerHTML = '<i class="fas fa-spinner fa-spin me-1"></i>Getting Location...';
    }
    
    getCurrentLocation(
        function(position) {
            const lat = position.coords.latitude;
            const lon = position.coords.longitude;
            
            latField.value = lat;
            lonField.value = lon;
            
            if (addrField) {
                reverseGeocode(lat, lon, function(address) {
                    addrField.value = address;
                    
                    if (btn) {
                        btn.innerHTML = '<i class="fas fa-check me-1"></i>Location Found';
                        btn.classList.remove('btn-outline-secondary');
                        btn.classList.add('btn-success');
                        
                        setTimeout(() => {
                            btn.innerHTML = '<i class="fas fa-map-marker-alt me-1"></i>Get Current Location';
                            btn.classList.remove('btn-success');
                            btn.classList.add('btn-outline-secondary');
                            btn.disabled = false;
                        }, 2000);
                    }
                    
                    if (onSuccess) onSuccess(lat, lon, address);
                });
            } else {
                if (btn) {
                    btn.innerHTML = '<i class="fas fa-check me-1"></i>Location Found';
                    btn.classList.remove('btn-outline-secondary');
                    btn.classList.add('btn-success');
                    btn.disabled = false;
                }
                
                if (onSuccess) onSuccess(lat, lon, null);
            }
        },
        function(error) {
            console.error('Geolocation error:', error);
            
            if (btn) {
                btn.innerHTML = '<i class="fas fa-exclamation-triangle me-1"></i>Location Error';
                btn.classList.remove('btn-outline-secondary');
                btn.classList.add('btn-warning');
                
                setTimeout(() => {
                    btn.innerHTML = '<i class="fas fa-map-marker-alt me-1"></i>Get Current Location';
                    btn.classList.remove('btn-warning');
                    btn.classList.add('btn-outline-secondary');
                    btn.disabled = false;
                }, 3000);
            }
            
            // Show user-friendly error message
            const message = getGeolocationErrorMessage(error);
            if (window.CrisisMS && window.CrisisMS.showNotification) {
                window.CrisisMS.showNotification(message, 'warning', 5000);
            } else {
                alert(message);
            }
            
            if (onError) onError(error, message);
        }
    );
}

/**
 * Create a simple map display for coordinates
 * This is a basic implementation - in production you might want to use
 * Google Maps, OpenStreetMap, or similar mapping service
 */
function displayLocationMap(latitude, longitude, containerId) {
    const container = document.getElementById(containerId);
    if (!container) return;
    
    // Create a simple map placeholder
    // In production, replace this with actual map integration
    container.innerHTML = `
        <div class="location-map-placeholder" style="
            width: 100%;
            height: 200px;
            background: linear-gradient(45deg, #f8f9fa, #e9ecef);
            border: 2px dashed #6c757d;
            border-radius: 8px;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            text-align: center;
            color: #6c757d;
        ">
            <i class="fas fa-map-marker-alt fa-2x mb-2"></i>
            <strong>Location Coordinates</strong><br>
            <small>${formatCoordinates(latitude, longitude)}</small><br>
            <small class="mt-1">
                <a href="https://www.google.com/maps?q=${latitude},${longitude}" 
                   target="_blank" class="text-decoration-none">
                    <i class="fas fa-external-link-alt me-1"></i>View on Google Maps
                </a>
            </small>
        </div>
    `;
}

/**
 * Get address suggestions based on partial input
 * This is a basic implementation - in production you might want to use
 * Google Places API, Mapbox Geocoding, or similar service
 */
function getAddressSuggestions(query, callback) {
    if (query.length < 3) {
        callback([]);
        return;
    }
    
    // This is a placeholder implementation
    // In production, integrate with a proper geocoding service
    const suggestions = [
        `${query} Street, City, Country`,
        `${query} Avenue, City, Country`,
        `${query} Road, City, Country`
    ];
    
    setTimeout(() => callback(suggestions), 300);
}

/**
 * Initialize location functionality for a form
 */
function initializeLocationForm(formId, options = {}) {
    const form = document.getElementById(formId);
    if (!form) return;
    
    const getLocationBtn = form.querySelector('#getLocationBtn, [data-action="get-location"]');
    if (getLocationBtn) {
        getLocationBtn.addEventListener('click', function(e) {
            e.preventDefault();
            autoFillLocation(options);
        });
    }
    
    // Add location validation
    const latField = form.querySelector('#latitude, input[name="latitude"]');
    const lonField = form.querySelector('#longitude, input[name="longitude"]');
    
    if (latField && lonField) {
        [latField, lonField].forEach(field => {
            field.addEventListener('blur', function() {
                const lat = parseFloat(latField.value);
                const lon = parseFloat(lonField.value);
                
                if (latField.value && lonField.value && !validateCoordinates(lat, lon)) {
                    field.classList.add('is-invalid');
                    
                    // Add or update error message
                    let feedback = field.parentNode.querySelector('.invalid-feedback');
                    if (!feedback) {
                        feedback = document.createElement('div');
                        feedback.className = 'invalid-feedback';
                        field.parentNode.appendChild(feedback);
                    }
                    feedback.textContent = 'Invalid coordinates';
                } else {
                    field.classList.remove('is-invalid');
                }
            });
        });
    }
}

// Export functions for global use
if (typeof window !== 'undefined') {
    window.Geolocation = {
        getCurrentLocation,
        watchLocation,
        stopWatchingLocation,
        reverseGeocode,
        calculateDistance,
        formatCoordinates,
        validateCoordinates,
        getGeolocationErrorMessage,
        autoFillLocation,
        displayLocationMap,
        getAddressSuggestions,
        initializeLocationForm
    };
}
