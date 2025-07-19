// Main JavaScript file for Tech Support Dashboard

// Global variables
let currentUser = null;
let dashboardData = {};

// Initialize the application
document.addEventListener('DOMContentLoaded', function() {
    initializeApp();
});

function initializeApp() {
    // Initialize common functionality
    initializeAlerts();
    initializeTooltips();
    initializeModals();
    initializeFormValidation();
    initializeDashboard();
    
    console.log('Tech Support Dashboard initialized successfully');
}

// Alert system
function initializeAlerts() {
    // Auto-hide alerts after 5 seconds
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(function(alert) {
        setTimeout(function() {
            fadeOut(alert);
        }, 5000);
        
        // Add close button functionality
        const closeBtn = alert.querySelector('.alert-close');
        if (closeBtn) {
            closeBtn.addEventListener('click', function() {
                fadeOut(alert);
            });
        }
    });
}

// Tooltip initialization
function initializeTooltips() {
    const tooltipElements = document.querySelectorAll('[data-tooltip]');
    tooltipElements.forEach(function(element) {
        element.addEventListener('mouseenter', showTooltip);
        element.addEventListener('mouseleave', hideTooltip);
    });
}

function showTooltip(event) {
    const element = event.target;
    const tooltipText = element.getAttribute('data-tooltip');
    
    const tooltip = document.createElement('div');
    tooltip.className = 'tooltip absolute z-50 bg-gray-900 text-white text-xs rounded py-1 px-2 pointer-events-none';
    tooltip.textContent = tooltipText;
    tooltip.id = 'tooltip';
    
    document.body.appendChild(tooltip);
    
    const rect = element.getBoundingClientRect();
    tooltip.style.left = rect.left + (rect.width / 2) - (tooltip.offsetWidth / 2) + 'px';
    tooltip.style.top = rect.top - tooltip.offsetHeight - 5 + 'px';
}

function hideTooltip() {
    const tooltip = document.getElementById('tooltip');
    if (tooltip) {
        tooltip.remove();
    }
}

// Modal functionality
function initializeModals() {
    const modalTriggers = document.querySelectorAll('[data-modal-target]');
    const modalCloses = document.querySelectorAll('[data-modal-close]');
    
    modalTriggers.forEach(function(trigger) {
        trigger.addEventListener('click', function() {
            const targetId = this.getAttribute('data-modal-target');
            const modal = document.getElementById(targetId);
            if (modal) {
                showModal(modal);
            }
        });
    });
    
    modalCloses.forEach(function(closeBtn) {
        closeBtn.addEventListener('click', function() {
            const modal = this.closest('.modal');
            if (modal) {
                hideModal(modal);
            }
        });
    });
    
    // Close modal on backdrop click
    document.addEventListener('click', function(event) {
        if (event.target.classList.contains('modal-backdrop')) {
            const modal = event.target.closest('.modal');
            if (modal) {
                hideModal(modal);
            }
        }
    });
}

function showModal(modal) {
    modal.classList.remove('hidden');
    modal.classList.add('flex');
    document.body.style.overflow = 'hidden';
}

function hideModal(modal) {
    modal.classList.add('hidden');
    modal.classList.remove('flex');
    document.body.style.overflow = 'auto';
}

// Form validation
function initializeFormValidation() {
    const forms = document.querySelectorAll('form[data-validate]');
    forms.forEach(function(form) {
        form.addEventListener('submit', function(event) {
            if (!validateForm(form)) {
                event.preventDefault();
            }
        });
        
        // Real-time validation
        const inputs = form.querySelectorAll('input, textarea, select');
        inputs.forEach(function(input) {
            input.addEventListener('blur', function() {
                validateField(input);
            });
        });
    });
}

function validateForm(form) {
    let isValid = true;
    const inputs = form.querySelectorAll('input[required], textarea[required], select[required]');
    
    inputs.forEach(function(input) {
        if (!validateField(input)) {
            isValid = false;
        }
    });
    
    return isValid;
}

function validateField(field) {
    const value = field.value.trim();
    const type = field.type;
    let isValid = true;
    let errorMessage = '';
    
    // Required field validation
    if (field.hasAttribute('required') && !value) {
        isValid = false;
        errorMessage = 'This field is required';
    }
    
    // Email validation
    if (type === 'email' && value) {
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        if (!emailRegex.test(value)) {
            isValid = false;
            errorMessage = 'Please enter a valid email address';
        }
    }
    
    // Password validation
    if (type === 'password' && value) {
        if (value.length < 6) {
            isValid = false;
            errorMessage = 'Password must be at least 6 characters long';
        }
    }
    
    // Show/hide error message
    showFieldError(field, isValid ? '' : errorMessage);
    
    return isValid;
}

function showFieldError(field, message) {
    // Remove existing error
    const existingError = field.parentNode.querySelector('.field-error');
    if (existingError) {
        existingError.remove();
    }
    
    if (message) {
        field.classList.add('border-red-500');
        const errorDiv = document.createElement('div');
        errorDiv.className = 'field-error text-red-500 text-xs mt-1';
        errorDiv.textContent = message;
        field.parentNode.appendChild(errorDiv);
    } else {
        field.classList.remove('border-red-500');
    }
}

// Dashboard functionality
function initializeDashboard() {
    // Initialize dashboard-specific features
    initializeStats();
    initializeCharts();
    initializeRealTimeUpdates();
}

function initializeStats() {
    // Animate stat numbers
    const statNumbers = document.querySelectorAll('.stat-number');
    statNumbers.forEach(function(stat) {
        animateNumber(stat);
    });
}

function animateNumber(element) {
    const finalNumber = parseInt(element.textContent) || 0;
    const duration = 1000;
    const steps = 20;
    const increment = finalNumber / steps;
    let current = 0;
    
    const timer = setInterval(function() {
        current += increment;
        if (current >= finalNumber) {
            current = finalNumber;
            clearInterval(timer);
        }
        element.textContent = Math.floor(current);
    }, duration / steps);
}

function initializeCharts() {
    // Initialize Chart.js charts (placeholder for future implementation)
    const chartElements = document.querySelectorAll('.chart-container');
    chartElements.forEach(function(container) {
        // Chart initialization will be implemented when Chart.js is added
        console.log('Chart container found:', container.id);
    });
}

function initializeRealTimeUpdates() {
    // Simulate real-time updates (placeholder for WebSocket implementation)
    setInterval(function() {
        updateDashboardData();
    }, 30000); // Update every 30 seconds
}

function updateDashboardData() {
    // This would typically fetch data from the server
    console.log('Updating dashboard data...');
}

// Utility functions
function fadeOut(element) {
    element.style.transition = 'opacity 0.5s ease-in-out';
    element.style.opacity = '0';
    setTimeout(function() {
        element.remove();
    }, 500);
}

function fadeIn(element) {
    element.style.opacity = '0';
    element.style.transition = 'opacity 0.5s ease-in-out';
    setTimeout(function() {
        element.style.opacity = '1';
    }, 10);
}

function showLoading(element) {
    const spinner = document.createElement('div');
    spinner.className = 'spinner inline-block mr-2';
    spinner.id = 'loading-spinner';
    element.insertBefore(spinner, element.firstChild);
    element.disabled = true;
}

function hideLoading(element) {
    const spinner = element.querySelector('#loading-spinner');
    if (spinner) {
        spinner.remove();
    }
    element.disabled = false;
}

// API helper functions
async function apiRequest(url, options = {}) {
    const defaultOptions = {
        headers: {
            'Content-Type': 'application/json',
        },
    };
    
    const config = { ...defaultOptions, ...options };
    
    try {
        const response = await fetch(url, config);
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        return await response.json();
    } catch (error) {
        console.error('API request failed:', error);
        showNotification('An error occurred. Please try again.', 'error');
        throw error;
    }
}

// Notification system
function showNotification(message, type = 'info', duration = 5000) {
    const notification = document.createElement('div');
    notification.className = `notification fixed top-4 right-4 z-50 p-4 rounded-md shadow-lg max-w-sm ${getNotificationClasses(type)}`;
    
    notification.innerHTML = `
        <div class="flex items-center">
            <div class="flex-shrink-0">
                ${getNotificationIcon(type)}
            </div>
            <div class="ml-3">
                <p class="text-sm font-medium">${message}</p>
            </div>
            <div class="ml-4 flex-shrink-0">
                <button class="notification-close text-sm font-medium underline">
                    ×
                </button>
            </div>
        </div>
    `;
    
    document.body.appendChild(notification);
    
    // Auto-remove after duration
    setTimeout(function() {
        fadeOut(notification);
    }, duration);
    
    // Close button functionality
    notification.querySelector('.notification-close').addEventListener('click', function() {
        fadeOut(notification);
    });
}

function getNotificationClasses(type) {
    const classes = {
        success: 'bg-green-50 border border-green-200 text-green-800',
        error: 'bg-red-50 border border-red-200 text-red-800',
        warning: 'bg-yellow-50 border border-yellow-200 text-yellow-800',
        info: 'bg-blue-50 border border-blue-200 text-blue-800'
    };
    return classes[type] || classes.info;
}

function getNotificationIcon(type) {
    const icons = {
        success: '<i class="fas fa-check-circle text-green-400"></i>',
        error: '<i class="fas fa-exclamation-circle text-red-400"></i>',
        warning: '<i class="fas fa-exclamation-triangle text-yellow-400"></i>',
        info: '<i class="fas fa-info-circle text-blue-400"></i>'
    };
    return icons[type] || icons.info;
}

// Search functionality
function initializeSearch() {
    const searchInputs = document.querySelectorAll('.search-input');
    searchInputs.forEach(function(input) {
        input.addEventListener('input', debounce(function() {
            performSearch(input.value, input.dataset.searchTarget);
        }, 300));
    });
}

function performSearch(query, target) {
    // Implement search functionality based on target
    console.log(`Searching for "${query}" in ${target}`);
}

// Debounce utility
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

// Export functions for global access
window.TechSupportDashboard = {
    showNotification,
    showModal,
    hideModal,
    apiRequest,
    validateForm,
    showLoading,
    hideLoading
};

// Service Worker registration (for future PWA implementation)
if ('serviceWorker' in navigator) {
    window.addEventListener('load', function() {
        // Service worker registration will be implemented later
        console.log('Service Worker support detected');
    });
}
