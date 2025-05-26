/**
 * Google Maps Integration for Crisis Management System
 * Provides Google Maps links and basic map functionality
 */

/**
 * Generate Google Maps link for coordinates
 */
function generateGoogleMapsLink(latitude, longitude, label = 'Incident Location') {
    const baseUrl = 'https://www.google.com/maps';
    const params = new URLSearchParams({
        q: `${latitude},${longitude}`,
        ll: `${latitude},${longitude}`,
        z: '15'
    });
    
    return `${baseUrl}?${params.toString()}`;
}

/**
 * Generate Google Maps directions link
 */
function generateDirectionsLink(fromLat, fromLng, toLat, toLng) {
    const baseUrl = 'https://www.google.com/maps/dir';
    return `${baseUrl}/${fromLat},${fromLng}/${toLat},${toLng}`;
}

/**
 * Open Google Maps in new tab
 */
function openGoogleMaps(latitude, longitude, label = 'Location') {
    if (latitude && longitude) {
        const url = generateGoogleMapsLink(latitude, longitude, label);
        window.open(url, '_blank');
    } else {
        alert('Location coordinates not available');
    }
}

/**
 * Get directions to location
 */
function getDirections(latitude, longitude) {
    if (!latitude || !longitude) {
        alert('Location coordinates not available');
        return;
    }
    
    if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(
            (position) => {
                const userLat = position.coords.latitude;
                const userLng = position.coords.longitude;
                const url = generateDirectionsLink(userLat, userLng, latitude, longitude);
                window.open(url, '_blank');
            },
            () => {
                // Fallback: just open location without directions
                openGoogleMaps(latitude, longitude);
            }
        );
    } else {
        // Fallback: just open location
        openGoogleMaps(latitude, longitude);
    }
}

/**
 * Create Google Maps location display card
 */
function createLocationCard(incident) {
    if (!incident.latitude || !incident.longitude) {
        return '<p class="text-muted">No location data available</p>';
    }
    
    const mapsUrl = generateGoogleMapsLink(incident.latitude, incident.longitude, incident.title);
    
    return `
        <div class="location-card p-3 border rounded mb-3">
            <h6 class="mb-2">
                <i class="fas fa-map-marker-alt text-danger me-2"></i>Incident Location
            </h6>
            <p class="mb-2">
                <strong>Coordinates:</strong> ${incident.latitude.toFixed(6)}, ${incident.longitude.toFixed(6)}
            </p>
            <p class="mb-3">
                <strong>Address:</strong> ${incident.address || 'Address not provided'}
            </p>
            <div class="d-flex gap-2 flex-wrap">
                <a href="${mapsUrl}" target="_blank" class="btn btn-primary btn-sm">
                    <i class="fab fa-google me-1"></i>View on Google Maps
                </a>
                <button onclick="getDirections(${incident.latitude}, ${incident.longitude})" 
                        class="btn btn-success btn-sm">
                    <i class="fas fa-route me-1"></i>Get Directions
                </button>
                <button onclick="copyCoordinates(${incident.latitude}, ${incident.longitude})" 
                        class="btn btn-outline-secondary btn-sm">
                    <i class="fas fa-copy me-1"></i>Copy Coordinates
                </button>
            </div>
        </div>
    `;
}

/**
 * Copy coordinates to clipboard
 */
function copyCoordinates(latitude, longitude) {
    const coordinates = `${latitude}, ${longitude}`;
    navigator.clipboard.writeText(coordinates).then(() => {
        showNotification('Coordinates copied to clipboard!', 'success');
    }).catch(() => {
        // Fallback for older browsers
        const textArea = document.createElement('textarea');
        textArea.value = coordinates;
        document.body.appendChild(textArea);
        textArea.select();
        document.execCommand('copy');
        document.body.removeChild(textArea);
        showNotification('Coordinates copied to clipboard!', 'success');
    });
}

/**
 * Create live incidents overview with Google Maps links
 */
function createIncidentsMapOverview(incidents) {
    if (!incidents || incidents.length === 0) {
        return `
            <div class="text-center py-4">
                <i class="fas fa-map-marked-alt fa-3x text-muted mb-3"></i>
                <h5 class="text-muted">No Active Incidents</h5>
                <p class="text-muted">No incidents with location data to display</p>
            </div>
        `;
    }
    
    const incidentsWithLocation = incidents.filter(i => i.latitude && i.longitude);
    
    if (incidentsWithLocation.length === 0) {
        return `
            <div class="text-center py-4">
                <i class="fas fa-map-marked-alt fa-3x text-muted mb-3"></i>
                <h5 class="text-muted">No Location Data</h5>
                <p class="text-muted">No incidents have location coordinates</p>
            </div>
        `;
    }
    
    // Create multi-destination Google Maps link
    const destinations = incidentsWithLocation.map(i => `${i.latitude},${i.longitude}`).join('/');
    const multiMapUrl = `https://www.google.com/maps/dir/${destinations}`;
    
    let html = `
        <div class="mb-3">
            <div class="d-flex justify-content-between align-items-center mb-3">
                <h6 class="mb-0">Live Incident Locations (${incidentsWithLocation.length})</h6>
                <a href="${multiMapUrl}" target="_blank" class="btn btn-primary btn-sm">
                    <i class="fab fa-google me-1"></i>View All on Map
                </a>
            </div>
        </div>
        <div class="incident-list" style="max-height: 400px; overflow-y: auto;">
    `;
    
    incidentsWithLocation.forEach(incident => {
        const priorityClass = getPriorityClass(incident.priority);
        const statusClass = getStatusClass(incident.status);
        const mapsUrl = generateGoogleMapsLink(incident.latitude, incident.longitude, incident.title);
        
        html += `
            <div class="card mb-2">
                <div class="card-body py-2">
                    <div class="row align-items-center">
                        <div class="col-md-6">
                            <h6 class="mb-1">${incident.title}</h6>
                            <div class="mb-1">
                                <span class="badge ${priorityClass} me-1">${incident.priority}</span>
                                <span class="badge ${statusClass}">${incident.status}</span>
                            </div>
                            <small class="text-muted">${incident.incident_type.replace('_', ' ')}</small>
                        </div>
                        <div class="col-md-6 text-end">
                            <div class="btn-group btn-group-sm">
                                <a href="${mapsUrl}" target="_blank" class="btn btn-outline-primary btn-sm">
                                    <i class="fas fa-map-marker-alt me-1"></i>View
                                </a>
                                <button onclick="getDirections(${incident.latitude}, ${incident.longitude})" 
                                        class="btn btn-outline-success btn-sm">
                                    <i class="fas fa-route me-1"></i>Directions
                                </button>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        `;
    });
    
    html += '</div>';
    return html;
}

/**
 * Initialize Google Maps integration on page load
 */
function initializeGoogleMapsIntegration() {
    // Load incidents data and create map overview
    fetch('/api/incidents')
        .then(response => response.json())
        .then(data => {
            const mapContainer = document.getElementById('googleMapsOverview');
            if (mapContainer) {
                mapContainer.innerHTML = createIncidentsMapOverview(data.incidents || []);
            }
        })
        .catch(error => {
            console.error('Error loading incidents for map overview:', error);
            const mapContainer = document.getElementById('googleMapsOverview');
            if (mapContainer) {
                mapContainer.innerHTML = `
                    <div class="text-center py-4">
                        <i class="fas fa-exclamation-triangle fa-2x text-warning mb-2"></i>
                        <p class="text-muted">Unable to load incident locations</p>
                    </div>
                `;
            }
        });
}

/**
 * Auto-refresh map overview every 30 seconds
 */
function startMapOverviewRefresh() {
    setInterval(() => {
        if (!document.hidden) {
            initializeGoogleMapsIntegration();
        }
    }, 30000);
}

// Initialize when page loads
document.addEventListener('DOMContentLoaded', function() {
    initializeGoogleMapsIntegration();
    startMapOverviewRefresh();
});

// Utility functions for styling (if not already defined)
function getPriorityClass(priority) {
    const classes = {
        'low': 'bg-success',
        'medium': 'bg-warning',
        'high': 'bg-danger',
        'critical': 'bg-dark'
    };
    return classes[priority] || 'bg-secondary';
}

function getStatusClass(status) {
    const classes = {
        'pending': 'bg-warning',
        'in_progress': 'bg-info',
        'resolved': 'bg-success',
        'closed': 'bg-secondary'
    };
    return classes[status] || 'bg-secondary';
}

function showNotification(message, type) {
    // Create notification if function doesn't exist
    if (typeof showNotification === 'undefined') {
        alert(message);
    }
}