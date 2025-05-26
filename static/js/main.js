/**
 * Crisis Management System - Main JavaScript
 * Handles common functionality across all pages
 */

document.addEventListener('DOMContentLoaded', function() {
    
    // Initialize tooltips
    initializeTooltips();
    
    // Initialize form validation
    initializeFormValidation();
    
    // Initialize auto-refresh for real-time updates
    initializeAutoRefresh();
    
    // Initialize image preview
    initializeImagePreview();
    
    // Initialize confirmation dialogs
    initializeConfirmationDialogs();
    
    // Initialize loading states
    initializeLoadingStates();
    
    // Initialize notification system
    initializeNotifications();
});

/**
 * Initialize Bootstrap tooltips
 */
function initializeTooltips() {
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
}

/**
 * Initialize form validation
 */
function initializeFormValidation() {
    const forms = document.querySelectorAll('.needs-validation');
    
    Array.prototype.slice.call(forms).forEach(function(form) {
        form.addEventListener('submit', function(event) {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
            }
            form.classList.add('was-validated');
        }, false);
    });
    
    // Real-time validation for specific fields
    const requiredFields = document.querySelectorAll('input[required], textarea[required], select[required]');
    requiredFields.forEach(function(field) {
        field.addEventListener('blur', function() {
            if (this.value.trim() === '') {
                this.classList.add('is-invalid');
            } else {
                this.classList.remove('is-invalid');
                this.classList.add('is-valid');
            }
        });
    });
}

/**
 * Initialize auto-refresh for real-time updates
 */
function initializeAutoRefresh() {
    const autoRefreshElements = document.querySelectorAll('[data-auto-refresh]');
    
    autoRefreshElements.forEach(function(element) {
        const interval = parseInt(element.dataset.autoRefresh) || 30000; // Default 30 seconds
        
        setInterval(function() {
            // Only refresh if the page is visible and user is not interacting with forms
            if (document.visibilityState === 'visible' && !isUserInteracting()) {
                refreshElement(element);
            }
        }, interval);
    });
}

/**
 * Check if user is currently interacting with forms
 */
function isUserInteracting() {
    const activeElement = document.activeElement;
    return activeElement && (
        activeElement.tagName === 'INPUT' ||
        activeElement.tagName === 'TEXTAREA' ||
        activeElement.tagName === 'SELECT' ||
        activeElement.isContentEditable
    );
}

/**
 * Refresh specific element content
 */
function refreshElement(element) {
    const url = element.dataset.refreshUrl || window.location.href;
    
    fetch(url, {
        headers: {
            'X-Requested-With': 'XMLHttpRequest'
        }
    })
    .then(response => response.text())
    .then(html => {
        const parser = new DOMParser();
        const doc = parser.parseFromString(html, 'text/html');
        const newElement = doc.querySelector(`[data-auto-refresh="${element.dataset.autoRefresh}"]`);
        
        if (newElement) {
            element.innerHTML = newElement.innerHTML;
            // Re-initialize components for the refreshed content
            initializeTooltips();
            initializeConfirmationDialogs();
        }
    })
    .catch(error => {
        console.error('Auto-refresh failed:', error);
    });
}

/**
 * Initialize image preview functionality
 */
function initializeImagePreview() {
    const imageInputs = document.querySelectorAll('input[type="file"][accept*="image"]');
    
    imageInputs.forEach(function(input) {
        input.addEventListener('change', function(event) {
            const file = event.target.files[0];
            const previewContainer = document.getElementById(input.id + '-preview');
            
            if (file && previewContainer) {
                const reader = new FileReader();
                reader.onload = function(e) {
                    previewContainer.innerHTML = `
                        <div class="mt-2">
                            <img src="${e.target.result}" alt="Preview" class="img-thumbnail" style="max-width: 200px; max-height: 200px;">
                            <button type="button" class="btn btn-sm btn-outline-danger ms-2" onclick="clearImagePreview('${input.id}')">
                                <i class="fas fa-times"></i> Remove
                            </button>
                        </div>
                    `;
                };
                reader.readAsDataURL(file);
            }
        });
    });
}

/**
 * Clear image preview
 */
function clearImagePreview(inputId) {
    const input = document.getElementById(inputId);
    const previewContainer = document.getElementById(inputId + '-preview');
    
    if (input) {
        input.value = '';
    }
    if (previewContainer) {
        previewContainer.innerHTML = '';
    }
}

/**
 * Initialize confirmation dialogs
 */
function initializeConfirmationDialogs() {
    const confirmElements = document.querySelectorAll('[data-confirm]');
    
    confirmElements.forEach(function(element) {
        element.addEventListener('click', function(event) {
            const message = this.dataset.confirm;
            if (!confirm(message)) {
                event.preventDefault();
                return false;
            }
        });
    });
}

/**
 * Initialize loading states
 */
function initializeLoadingStates() {
    const forms = document.querySelectorAll('form');
    
    forms.forEach(function(form) {
        form.addEventListener('submit', function() {
            const submitButton = form.querySelector('button[type="submit"]');
            if (submitButton) {
                const originalText = submitButton.innerHTML;
                submitButton.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Processing...';
                submitButton.disabled = true;
                
                // Re-enable button after 10 seconds as fallback
                setTimeout(function() {
                    submitButton.innerHTML = originalText;
                    submitButton.disabled = false;
                }, 10000);
            }
        });
    });
}

/**
 * Initialize notification system
 */
function initializeNotifications() {
    // Auto-dismiss alerts after 5 seconds
    const alerts = document.querySelectorAll('.alert:not(.alert-permanent)');
    alerts.forEach(function(alert) {
        setTimeout(function() {
            const bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        }, 5000);
    });
}

/**
 * Show notification
 */
function showNotification(message, type = 'info', duration = 5000) {
    const alertContainer = document.getElementById('alert-container') || createAlertContainer();
    
    const alertId = 'alert-' + Date.now();
    const alertHTML = `
        <div id="${alertId}" class="alert alert-${type} alert-dismissible fade show" role="alert">
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        </div>
    `;
    
    alertContainer.insertAdjacentHTML('beforeend', alertHTML);
    
    // Auto-dismiss after duration
    setTimeout(function() {
        const alert = document.getElementById(alertId);
        if (alert) {
            const bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        }
    }, duration);
}

/**
 * Create alert container if it doesn't exist
 */
function createAlertContainer() {
    const container = document.createElement('div');
    container.id = 'alert-container';
    container.className = 'position-fixed top-0 end-0 p-3';
    container.style.zIndex = '1055';
    document.body.appendChild(container);
    return container;
}

/**
 * Format datetime for display
 */
function formatDateTime(dateString) {
    const date = new Date(dateString);
    return date.toLocaleString();
}

/**
 * Format relative time (e.g., "2 hours ago")
 */
function formatRelativeTime(dateString) {
    const date = new Date(dateString);
    const now = new Date();
    const diffMs = now - date;
    const diffSecs = Math.round(diffMs / 1000);
    const diffMins = Math.round(diffSecs / 60);
    const diffHours = Math.round(diffMins / 60);
    const diffDays = Math.round(diffHours / 24);
    
    if (diffSecs < 60) {
        return 'Just now';
    } else if (diffMins < 60) {
        return `${diffMins} minute${diffMins > 1 ? 's' : ''} ago`;
    } else if (diffHours < 24) {
        return `${diffHours} hour${diffHours > 1 ? 's' : ''} ago`;
    } else {
        return `${diffDays} day${diffDays > 1 ? 's' : ''} ago`;
    }
}

/**
 * Debounce function for search inputs
 */
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

/**
 * Copy text to clipboard
 */
function copyToClipboard(text) {
    if (navigator.clipboard) {
        navigator.clipboard.writeText(text).then(function() {
            showNotification('Copied to clipboard!', 'success', 2000);
        }).catch(function() {
            fallbackCopyToClipboard(text);
        });
    } else {
        fallbackCopyToClipboard(text);
    }
}

/**
 * Fallback copy to clipboard for older browsers
 */
function fallbackCopyToClipboard(text) {
    const textArea = document.createElement('textarea');
    textArea.value = text;
    textArea.style.top = '0';
    textArea.style.left = '0';
    textArea.style.position = 'fixed';
    
    document.body.appendChild(textArea);
    textArea.focus();
    textArea.select();
    
    try {
        document.execCommand('copy');
        showNotification('Copied to clipboard!', 'success', 2000);
    } catch (err) {
        showNotification('Failed to copy to clipboard', 'error', 3000);
    }
    
    document.body.removeChild(textArea);
}

/**
 * Print current page
 */
function printPage() {
    window.print();
}

/**
 * Export table data as CSV
 */
function exportTableAsCSV(tableId, filename = 'export.csv') {
    const table = document.getElementById(tableId);
    if (!table) return;
    
    const rows = table.querySelectorAll('tr');
    const csvContent = [];
    
    rows.forEach(function(row) {
        const cols = row.querySelectorAll('td, th');
        const rowData = [];
        cols.forEach(function(col) {
            rowData.push('"' + col.textContent.trim().replace(/"/g, '""') + '"');
        });
        csvContent.push(rowData.join(','));
    });
    
    const csvString = csvContent.join('\n');
    const blob = new Blob([csvString], { type: 'text/csv' });
    const url = window.URL.createObjectURL(blob);
    
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    a.click();
    
    window.URL.revokeObjectURL(url);
}

/**
 * Validate file upload
 */
function validateFileUpload(input, maxSize = 5 * 1024 * 1024, allowedTypes = ['image/jpeg', 'image/png', 'image/gif']) {
    const file = input.files[0];
    if (!file) return true;
    
    // Check file size
    if (file.size > maxSize) {
        showNotification(`File size too large. Maximum allowed: ${Math.round(maxSize / 1024 / 1024)}MB`, 'error');
        input.value = '';
        return false;
    }
    
    // Check file type
    if (!allowedTypes.includes(file.type)) {
        showNotification(`Invalid file type. Allowed types: ${allowedTypes.join(', ')}`, 'error');
        input.value = '';
        return false;
    }
    
    return true;
}

// Global error handler
window.addEventListener('error', function(event) {
    console.error('Global error:', event.error);
    // Don't show error notifications for minor issues
    if (event.error && event.error.message && !event.error.message.includes('ResizeObserver')) {
        showNotification('An unexpected error occurred. Please refresh the page.', 'error');
    }
});

// Handle network errors
window.addEventListener('online', function() {
    showNotification('Connection restored', 'success', 3000);
});

window.addEventListener('offline', function() {
    showNotification('Connection lost. Some features may not work.', 'warning', 5000);
});

// Export functions for global use
window.CrisisMS = {
    showNotification,
    copyToClipboard,
    printPage,
    exportTableAsCSV,
    validateFileUpload,
    formatDateTime,
    formatRelativeTime,
    clearImagePreview
};
