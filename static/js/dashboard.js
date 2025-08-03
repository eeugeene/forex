// ===== static/js/dashboard.js =====
// Global variables
let chart;
let currentTimeframe = '7d';
let alerts = [];
let currentRate = null;
let previousRate = null;

// API endpoints
const API_BASE = '/api';
const RATES_API = `${API_BASE}/rates/`;
const ALERTS_API = `${API_BASE}/alerts/`;

// Initialize dashboard
document.addEventListener('DOMContentLoaded', function() {
    initChart();
    loadCurrentRate();
    loadAlerts();
    setupEventListeners();
    
    // Update data every 30 seconds
    setInterval(() => {
        loadCurrentRate();
        updateChart();
    }, 30000);
});

// Setup event listeners
function setupEventListeners() {
    // Timeframe buttons
    document.querySelectorAll('.timeframe-btn').forEach(btn => {
        btn.addEventListener('click', function() {
            document.querySelectorAll('.timeframe-btn').forEach(b => b.classList.remove('active'));
            this.classList.add('active');
            currentTimeframe = this.dataset.timeframe;
            updateChart();
        });
    });

    // Alert form
    const alertForm = document.getElementById('alertForm');
    if (alertForm) {
        alertForm.addEventListener('submit', function(e) {
            e.preventDefault();
            createAlert();
        });
    }
}

// Initialize Chart.js
function initChart() {
    const ctx = document.getElementById('rateChart');
    if (!ctx) return;

    chart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: [],
            datasets: [{
                label: 'UGX/USD Rate',
                data: [],
                borderColor: '#00d4aa',
                backgroundColor: 'rgba(0, 212, 170, 0.1)',
                borderWidth: 2,
                fill: true,
                tension: 0.4,
                pointBackgroundColor: '#00d4aa',
                pointBorderColor: '#00d4aa',
                pointRadius: 2,
                pointHoverRadius: 6
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    labels: {
                        color: '#f0f0f0'
                    }
                },
                tooltip: {
                    backgroundColor: 'rgba(43, 47, 54, 0.9)',
                    titleColor: '#f0f0f0',
                    bodyColor: '#f0f0f0',
                    borderColor: '#2b2f36',
                    borderWidth: 1
                }
            },
            scales: {
                x: {
                    ticks: {
                        color: '#848e9c'
                    },
                    grid: {
                        color: 'rgba(43, 47, 54, 0.5)'
                    }
                },
                y: {
                    ticks: {
                        color: '#848e9c',
                        callback: function(value) {
                            return 'UGX ' + value.toFixed(2);
                        }
                    },
                    grid: {
                        color: 'rgba(43, 47, 54, 0.5)'
                    }
                }
            },
            animation: {
                duration: 1000,
                easing: 'easeOutQuart'
            }
        }
    });
    
    // Load initial chart data
    updateChart();
}

// Load current exchange rate
async function loadCurrentRate() {
    try {
        const response = await fetch(`${RATES_API}current/`);
        if (!response.ok) {
            throw new Error('Failed to fetch current rate');
        }
        
        const data = await response.json();
        previousRate = currentRate;
        currentRate = data;
        
        updateRateDisplay(data);
        updateStats(data);
        
    } catch (error) {
        console.error('Error loading current rate:', error);
        showError('Failed to load current exchange rate');
    }
}

// Update rate display
function updateRateDisplay(data) {
    const rateElement = document.getElementById('currentRate');
    const lastUpdateElement = document.getElementById('lastUpdate');
    
    if (!rateElement) return;
    
    const rate = parseFloat(data.rate);
    const changeClass = getChangeClass(previousRate, data);
    const changeIcon = getChangeIcon(previousRate, data);
    
    rateElement.innerHTML = `
        <span class="${changeClass}">
            UGX ${rate.toFixed(2)}
            <span class="change-indicator">${changeIcon}</span>
        </span>
    `;
    
    if (lastUpdateElement) {
        const timestamp = new Date(data.timestamp);
        lastUpdateElement.textContent = `Last updated: ${timestamp.toLocaleString()}`;
    }
    
    // Add animation effect
    rateElement.style.transform = 'scale(1.05)';
    setTimeout(() => {
        rateElement.style.transform = 'scale(1)';
    }, 200);
}

// Update statistics
function updateStats(data) {
    const buyRateElement = document.getElementById('buyRate');
    const sellRateElement = document.getElementById('sellRate');
    
    if (buyRateElement) {
        buyRateElement.textContent = `UGX ${parseFloat(data.buy_rate).toFixed(2)}`;
    }
    
    if (sellRateElement) {
        sellRateElement.textContent = `UGX ${parseFloat(data.sell_rate).toFixed(2)}`;
    }
    
    // Load 24h high/low from historical data
    load24hStats();
}

// Load 24h statistics
async function load24hStats() {
    try {
        const response = await fetch(`${RATES_API}history/?timeframe=1d`);
        if (!response.ok) return;
        
        const data = await response.json();
        
        if (data.length > 0) {
            const rates = data.map(item => parseFloat(item.rate));
            const high24h = Math.max(...rates);
            const low24h = Math.min(...rates);
            
            const high24hElement = document.getElementById('high24h');
            const low24hElement = document.getElementById('low24h');
            
            if (high24hElement) {
                high24hElement.textContent = `UGX ${high24h.toFixed(2)}`;
            }
            
            if (low24hElement) {
                low24hElement.textContent = `UGX ${low24h.toFixed(2)}`;
            }
        }
    } catch (error) {
        console.error('Error loading 24h stats:', error);
    }
}

// Update chart with historical data
async function updateChart() {
    if (!chart) return;
    
    try {
        const response = await fetch(`${RATES_API}history/?timeframe=${currentTimeframe}`);
        if (!response.ok) {
            throw new Error('Failed to fetch historical data');
        }
        
        const data = await response.json();
        
        // Prepare chart data
        const labels = data.map(item => {
            const date = new Date(item.timestamp);
            return formatChartLabel(date, currentTimeframe);
        }).reverse();
        
        const rates = data.map(item => parseFloat(item.rate)).reverse();
        
        // Update chart
        chart.data.labels = labels;
        chart.data.datasets[0].data = rates;
        chart.update('none'); // No animation for real-time updates
        
    } catch (error) {
        console.error('Error updating chart:', error);
        showError('Failed to update chart data');
    }
}

// Format chart labels based on timeframe
function formatChartLabel(date, timeframe) {
    switch (timeframe) {
        case '1d':
            return date.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' });
        case '7d':
            return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
        case '30d':
        case '90d':
            return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
        default:
            return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
    }
}

// Get change class for rate display
function getChangeClass(previousRate, currentRate) {
    if (!previousRate) return 'rate-neutral';
    
    const prev = parseFloat(previousRate.rate);
    const curr = parseFloat(currentRate.rate);
    
    if (curr > prev) return 'rate-up';
    if (curr < prev) return 'rate-down';
    return 'rate-neutral';
}

// Get change icon
function getChangeIcon(previousRate, currentRate) {
    if (!previousRate) return '';
    
    const prev = parseFloat(previousRate.rate);
    const curr = parseFloat(currentRate.rate);
    
    if (curr > prev) return '<i class="fas fa-arrow-up"></i>';
    if (curr < prev) return '<i class="fas fa-arrow-down"></i>';
    return '<i class="fas fa-minus"></i>';
}

// Load user alerts
async function loadAlerts() {
    try {
        const response = await fetch(ALERTS_API);
        if (!response.ok) {
            throw new Error('Failed to fetch alerts');
        }
        
        const data = await response.json();
        alerts = data.results || data;
        renderAlerts();
        
    } catch (error) {
        console.error('Error loading alerts:', error);
        const alertsList = document.getElementById('alertsList');
        if (alertsList) {
            alertsList.innerHTML = '<div class="text-center text-muted">Failed to load alerts</div>';
        }
    }
}

// Render alerts list
function renderAlerts() {
    const alertsList = document.getElementById('alertsList');
    if (!alertsList) return;
    
    if (alerts.length === 0) {
        alertsList.innerHTML = '<div class="text-center text-muted">No alerts created yet</div>';
        return;
    }
    
    const alertsHTML = alerts.map(alert => `
        <div class="alert-item">
            <div>
                <strong>${alert.alert_type.charAt(0).toUpperCase() + alert.alert_type.slice(1)}</strong>
                UGX ${parseFloat(alert.threshold_rate).toFixed(2)}
                <br>
                <small class="text-muted">
                    Created: ${new Date(alert.created_at).toLocaleDateString()}
                </small>
            </div>
            <div>
                <button class="btn btn-sm btn-danger" onclick="deleteAlert(${alert.id})">
                    <i class="fas fa-trash"></i>
                </button>
            </div>
        </div>
    `).join('');
    
    alertsList.innerHTML = alertsHTML;
}

// Create new alert
async function createAlert() {
    const thresholdRate = document.getElementById('thresholdRate').value;
    const alertType = document.getElementById('alertType').value;
    
    if (!thresholdRate || !alertType) {
        showError('Please fill in all fields');
        return;
    }
    
    try {
        const response = await fetch(ALERTS_API, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCSRFToken()
            },
            body: JSON.stringify({
                threshold_rate: parseFloat(thresholdRate),
                alert_type: alertType
            })
        });
        
        if (!response.ok) {
            throw new Error('Failed to create alert');
        }
        
        // Reset form
        document.getElementById('alertForm').reset();
        
        // Reload alerts
        loadAlerts();
        
        showSuccess('Alert created successfully!');
        
    } catch (error) {
        console.error('Error creating alert:', error);
        showError('Failed to create alert');
    }
}

// Delete alert
async function deleteAlert(alertId) {
    if (!confirm('Are you sure you want to delete this alert?')) {
        return;
    }
    
    try {
        const response = await fetch(`${ALERTS_API}${alertId}/`, {
            method: 'DELETE',
            headers: {
                'X-CSRFToken': getCSRFToken()
            }
        });
        
        if (!response.ok) {
            throw new Error('Failed to delete alert');
        }
        
        // Reload alerts
        loadAlerts();
        
        showSuccess('Alert deleted successfully!');
        
    } catch (error) {
        console.error('Error deleting alert:', error);
        showError('Failed to delete alert');
    }
}

// Utility functions
function getCSRFToken() {
    const cookies = document.cookie.split(';');
    for (let cookie of cookies) {
        const [name, value] = cookie.trim().split('=');
        if (name === 'csrftoken') {
            return value;
        }
    }
    return '';
}

function showError(message) {
    showNotification(message, 'danger');
}

function showSuccess(message) {
    showNotification(message, 'success');
}

function showNotification(message, type) {
    // Create notification element
    const notification = document.createElement('div');
    notification.className = `alert alert-${type} alert-dismissible fade show position-fixed`;
    notification.style.cssText = 'top: 20px; right: 20px; z-index: 9999; min-width: 300px;';
    notification.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    // Add to page
    document.body.appendChild(notification);
    
    // Auto remove after 5 seconds
    setTimeout(() => {
        if (notification.parentNode) {
            notification.parentNode.removeChild(notification);
        }
    }, 5000);
}

// Export for global access
window.dashboard = {
    loadCurrentRate,
    updateChart,
    loadAlerts,
    createAlert,
    deleteAlert
};