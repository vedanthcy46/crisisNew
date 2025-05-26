/**
 * Crisis Management System - Live Map Implementation
 * Handles interactive maps for incident visualization
 */

let map = null;
let markers = [];
let incidentData = [];

/**
 * Initialize map with OpenStreetMap (free alternative to Google Maps)
 */
function initializeMap(containerId, options = {}) {
    const defaultOptions = {
        center: [40.7128, -74.0060], // Default to NYC
        zoom: 10,
        incidents: [],
        resources: [],
        showControls: true
    };
    
    const config = { ...defaultOptions, ...options };
    
    // Check if Leaflet is loaded
    if (typeof L === 'undefined') {
        console.error('Leaflet library not loaded. Please include Leaflet CSS and JS.');
        return;
    }
    
    // Initialize map
    map = L.map(containerId).setView(config.center, config.zoom);
    
    // Add OpenStreetMap tiles (free)
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '© OpenStreetMap contributors',
        maxZoom: 18
    }).addTo(map);
    
    // Add incidents to map
    if (config.incidents && config.incidents.length > 0) {
        addIncidentsToMap(config.incidents);
    }
    
    // Add resources to map
    if (config.resources && config.resources.length > 0) {
        addResourcesToMap(config.resources);
    }
    
    // Add map controls
    if (config.showControls) {
        addMapControls();
    }
    
    return map;
}

/**
 * Add incidents as markers on the map
 */
function addIncidentsToMap(incidents) {
    incidentData = incidents;
    
    incidents.forEach(incident => {
        if (incident.latitude && incident.longitude) {
            const marker = createIncidentMarker(incident);
            markers.push(marker);
            marker.addTo(map);
        }
    });
    
    // Fit map to show all markers if there are any
    if (markers.length > 0) {
        const group = new L.featureGroup(markers);
        map.fitBounds(group.getBounds().pad(0.1));
    }
}

/**
 * Create marker for incident
 */
function createIncidentMarker(incident) {
    const icon = getIncidentIcon(incident.incident_type, incident.priority);
    
    const marker = L.marker([incident.latitude, incident.longitude], { icon })
        .bindPopup(createIncidentPopup(incident));
    
    return marker;
}

/**
 * Get appropriate icon for incident type and priority
 */
function getIncidentIcon(type, priority) {
    const iconConfig = {
        iconSize: [32, 32],
        iconAnchor: [16, 32],
        popupAnchor: [0, -32]
    };
    
    // Icon colors based on priority
    const priorityColors = {
        'critical': 'red',
        'high': 'orange',
        'medium': 'yellow',
        'low': 'green'
    };
    
    // Icon symbols based on incident type
    const typeIcons = {
        'fire': '🔥',
        'medical': '🚑',
        'accident': '🚗',
        'natural_disaster': '🌪️',
        'crime': '🚔',
        'utility': '⚡',
        'other': '❗'
    };
    
    const color = priorityColors[priority] || 'blue';
    const emoji = typeIcons[type] || '📍';
    
    // Create custom div icon
    return L.divIcon({
        ...iconConfig,
        className: 'custom-incident-icon',
        html: `<div style="
            background-color: ${color};
            width: 32px;
            height: 32px;
            border-radius: 50%;
            border: 3px solid white;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 16px;
            box-shadow: 0 2px 6px rgba(0,0,0,0.3);
        ">${emoji}</div>`
    });
}

/**
 * Create popup content for incident
 */
function createIncidentPopup(incident) {
    const statusClass = getStatusClass(incident.status);
    const priorityClass = getPriorityClass(incident.priority);
    
    return `
        <div class="incident-popup">
            <h6 class="mb-2"><strong>${incident.title}</strong></h6>
            <p class="mb-2 small">${incident.description}</p>
            <div class="mb-2">
                <span class="badge ${statusClass} me-1">${incident.status}</span>
                <span class="badge ${priorityClass}">${incident.priority}</span>
            </div>
            <p class="mb-2 small"><strong>Type:</strong> ${incident.incident_type}</p>
            <p class="mb-2 small"><strong>Reported:</strong> ${formatDateTime(incident.created_at)}</p>
            ${incident.assigned_team ? `<p class="mb-2 small"><strong>Team:</strong> ${incident.assigned_team}</p>` : ''}
            <div class="text-center mt-2">
                <a href="/user/incident/${incident.id}" class="btn btn-sm btn-primary">View Details</a>
            </div>
        </div>
    `;
}

/**
 * Add resources as markers on the map
 */
function addResourcesToMap(resources) {
    resources.forEach(resource => {
        if (resource.latitude && resource.longitude) {
            const marker = createResourceMarker(resource);
            markers.push(marker);
            marker.addTo(map);
        }
    });
}

/**
 * Create marker for resource
 */
function createResourceMarker(resource) {
    const icon = getResourceIcon(resource.resource_type, resource.availability_status);
    
    const marker = L.marker([resource.latitude, resource.longitude], { icon })
        .bindPopup(createResourcePopup(resource));
    
    return marker;
}

/**
 * Get appropriate icon for resource
 */
function getResourceIcon(type, status) {
    const iconConfig = {
        iconSize: [28, 28],
        iconAnchor: [14, 28],
        popupAnchor: [0, -28]
    };
    
    const statusColors = {
        'available': 'green',
        'in_use': 'orange',
        'maintenance': 'red'
    };
    
    const typeIcons = {
        'vehicle': '🚐',
        'equipment': '🔧',
        'personnel': '👨‍🚒'
    };
    
    const color = statusColors[status] || 'gray';
    const emoji = typeIcons[type] || '📦';
    
    return L.divIcon({
        ...iconConfig,
        className: 'custom-resource-icon',
        html: `<div style="
            background-color: ${color};
            width: 28px;
            height: 28px;
            border-radius: 4px;
            border: 2px solid white;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 14px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.3);
        ">${emoji}</div>`
    });
}

/**
 * Create popup content for resource
 */
function createResourcePopup(resource) {
    const statusClass = getResourceStatusClass(resource.availability_status);
    
    return `
        <div class="resource-popup">
            <h6 class="mb-2"><strong>${resource.name}</strong></h6>
            <div class="mb-2">
                <span class="badge ${statusClass}">${resource.availability_status}</span>
            </div>
            <p class="mb-2 small"><strong>Type:</strong> ${resource.resource_type}</p>
            ${resource.description ? `<p class="mb-2 small">${resource.description}</p>` : ''}
            ${resource.location ? `<p class="mb-2 small"><strong>Location:</strong> ${resource.location}</p>` : ''}
        </div>
    `;
}

/**
 * Add map controls and legends
 */
function addMapControls() {
    // Add legend control
    const legend = L.control({ position: 'bottomright' });
    
    legend.onAdd = function(map) {
        const div = L.DomUtil.create('div', 'map-legend');
        div.innerHTML = `
            <div class="legend-content p-2 bg-dark text-light rounded">
                <h6 class="mb-2">Legend</h6>
                <div class="legend-item mb-1">
                    <span style="color: red;">🔥</span> Fire Emergency
                </div>
                <div class="legend-item mb-1">
                    <span style="color: orange;">🚑</span> Medical Emergency
                </div>
                <div class="legend-item mb-1">
                    <span style="color: yellow;">🚗</span> Traffic Accident
                </div>
                <div class="legend-item mb-1">
                    <span style="color: green;">🚐</span> Available Resource
                </div>
            </div>
        `;
        return div;
    };
    
    legend.addTo(map);
    
    // Add refresh button
    const refreshControl = L.control({ position: 'topleft' });
    
    refreshControl.onAdd = function(map) {
        const div = L.DomUtil.create('div', 'map-refresh-control');
        div.innerHTML = `
            <button class="btn btn-sm btn-primary" onclick="refreshMapData()" title="Refresh Map">
                <i class="fas fa-sync-alt"></i>
            </button>
        `;
        return div;
    };
    
    refreshControl.addTo(map);
}

/**
 * Refresh map data
 */
function refreshMapData() {
    // Clear existing markers
    markers.forEach(marker => {
        map.removeLayer(marker);
    });
    markers = [];
    
    // Reload incidents data
    fetch('/api/incidents')
        .then(response => response.json())
        .then(data => {
            if (data.incidents) {
                addIncidentsToMap(data.incidents);
            }
        })
        .catch(error => {
            console.error('Error refreshing map data:', error);
        });
}

/**
 * Filter incidents on map by type or status
 */
function filterMapIncidents(filterType, filterValue) {
    // Clear existing markers
    markers.forEach(marker => {
        map.removeLayer(marker);
    });
    markers = [];
    
    // Filter incidents based on criteria
    const filteredIncidents = incidentData.filter(incident => {
        if (filterType === 'all') return true;
        if (filterType === 'type') return incident.incident_type === filterValue;
        if (filterType === 'status') return incident.status === filterValue;
        if (filterType === 'priority') return incident.priority === filterValue;
        return true;
    });
    
    // Add filtered incidents to map
    addIncidentsToMap(filteredIncidents);
}

/**
 * Utility functions for styling
 */
function getStatusClass(status) {
    const statusClasses = {
        'pending': 'bg-warning',
        'in_progress': 'bg-info',
        'resolved': 'bg-success',
        'closed': 'bg-secondary'
    };
    return statusClasses[status] || 'bg-secondary';
}

function getPriorityClass(priority) {
    const priorityClasses = {
        'low': 'bg-success',
        'medium': 'bg-warning',
        'high': 'bg-danger',
        'critical': 'bg-dark'
    };
    return priorityClasses[priority] || 'bg-secondary';
}

function getResourceStatusClass(status) {
    const statusClasses = {
        'available': 'bg-success',
        'in_use': 'bg-warning',
        'maintenance': 'bg-danger'
    };
    return statusClasses[status] || 'bg-secondary';
}

function formatDateTime(dateString) {
    const date = new Date(dateString);
    return date.toLocaleString();
}

/**
 * Auto-refresh map data every 30 seconds
 */
function startMapAutoRefresh(interval = 30000) {
    setInterval(() => {
        if (map && !document.hidden) {
            refreshMapData();
        }
    }, interval);
}

/**
 * Initialize map with current user location
 */
function initializeMapWithUserLocation(containerId, options = {}) {
    if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(
            (position) => {
                const userLocation = [position.coords.latitude, position.coords.longitude];
                const mapOptions = {
                    ...options,
                    center: userLocation,
                    zoom: 13
                };
                initializeMap(containerId, mapOptions);
                
                // Add user location marker
                L.marker(userLocation, {
                    icon: L.divIcon({
                        className: 'user-location-icon',
                        html: '<div style="background-color: blue; width: 20px; height: 20px; border-radius: 50%; border: 3px solid white;"></div>',
                        iconSize: [20, 20],
                        iconAnchor: [10, 10]
                    })
                }).addTo(map).bindPopup('Your Location');
            },
            () => {
                // Fallback to default location
                initializeMap(containerId, options);
            }
        );
    } else {
        initializeMap(containerId, options);
    }
}