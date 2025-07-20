class AnalyticsDashboard {
    constructor() {
        this.charts = {};
        this.currentTimeRange = 7;
        this.colors = {
            primary: '#3B82F6',
            secondary: '#6B7280',
            success: '#10B981',
            warning: '#F59E0B',
            danger: '#EF4444',
            purple: '#8B5CF6',
            indigo: '#6366F1'
        };
    }

    async init() {
        this.showLoading();
        try {
            await this.loadAllData();
            this.setupEventListeners();
        } catch (error) {
            console.error('Error initializing analytics dashboard:', error);
            this.showError('Failed to load analytics data');
        } finally {
            this.hideLoading();
        }
    }

    async loadAllData() {
        const promises = [
            this.loadTicketsByCategory(),
            this.loadResolutionTime(),
            this.loadTimeSeriesData(),
            this.loadPriorityDistribution(),
            this.loadStatusDistribution(),
            this.loadAgentPerformance()
        ];

        await Promise.all(promises);
    }

    async loadTicketsByCategory() {
        try {
            const response = await fetch('/analytics/api/tickets-by-category');
            const data = await response.json();
            this.renderCategoryChart(data);
        } catch (error) {
            console.error('Error loading category data:', error);
        }
    }

    async loadResolutionTime() {
        try {
            const response = await fetch('/analytics/api/resolution-time');
            const data = await response.json();
            this.updateResolutionTimeMetrics(data.overall);
            this.renderResolutionTimeChart(data.by_category);
        } catch (error) {
            console.error('Error loading resolution time data:', error);
        }
    }

    async loadTimeSeriesData(days = 7) {
        try {
            const response = await fetch(`/analytics/api/time-series?days=${days}`);
            const data = await response.json();
            this.renderTimeSeriesChart(data);
            this.updateTimeSeriesMetrics(data);
        } catch (error) {
            console.error('Error loading time series data:', error);
        }
    }

    async loadPriorityDistribution() {
        try {
            const response = await fetch('/analytics/api/priority-distribution');
            const data = await response.json();
            this.renderPriorityChart(data);
        } catch (error) {
            console.error('Error loading priority data:', error);
        }
    }

    async loadStatusDistribution() {
        try {
            const response = await fetch('/analytics/api/status-distribution');
            const data = await response.json();
            this.renderStatusChart(data);
            this.updateStatusMetrics(data);
        } catch (error) {
            console.error('Error loading status data:', error);
        }
    }

    async loadAgentPerformance() {
        try {
            const response = await fetch('/analytics/api/agent-performance');
            const data = await response.json();
            this.renderAgentPerformanceTable(data);
        } catch (error) {
            console.error('Error loading agent performance data:', error);
        }
    }

    renderCategoryChart(data) {
        const ctx = document.getElementById('categoryChart').getContext('2d');
        
        if (this.charts.category) {
            this.charts.category.destroy();
        }

        this.charts.category = new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: data.map(item => item.name),
                datasets: [{
                    data: data.map(item => item.count),
                    backgroundColor: data.map(item => item.color),
                    borderWidth: 2,
                    borderColor: '#ffffff'
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'bottom',
                        labels: {
                            padding: 20,
                            usePointStyle: true
                        }
                    },
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                const total = context.dataset.data.reduce((a, b) => a + b, 0);
                                const percentage = ((context.parsed / total) * 100).toFixed(1);
                                return `${context.label}: ${context.parsed} (${percentage}%)`;
                            }
                        }
                    }
                }
            }
        });
    }

    renderPriorityChart(data) {
        const ctx = document.getElementById('priorityChart').getContext('2d');
        
        if (this.charts.priority) {
            this.charts.priority.destroy();
        }

        this.charts.priority = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: data.map(item => item.priority.charAt(0).toUpperCase() + item.priority.slice(1)),
                datasets: [{
                    label: 'Tickets',
                    data: data.map(item => item.count),
                    backgroundColor: data.map(item => item.color),
                    borderRadius: 4
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: false
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        ticks: {
                            stepSize: 1
                        }
                    }
                }
            }
        });
    }

    renderTimeSeriesChart(data) {
        const ctx = document.getElementById('timeSeriesChart').getContext('2d');
        
        if (this.charts.timeSeries) {
            this.charts.timeSeries.destroy();
        }

        this.charts.timeSeries = new Chart(ctx, {
            type: 'line',
            data: {
                labels: data.map(item => {
                    const date = new Date(item.date);
                    return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
                }),
                datasets: [
                    {
                        label: 'Created',
                        data: data.map(item => item.created),
                        borderColor: this.colors.primary,
                        backgroundColor: this.colors.primary + '20',
                        fill: true,
                        tension: 0.4
                    },
                    {
                        label: 'Resolved',
                        data: data.map(item => item.resolved),
                        borderColor: this.colors.success,
                        backgroundColor: this.colors.success + '20',
                        fill: true,
                        tension: 0.4
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                interaction: {
                    intersect: false,
                    mode: 'index'
                },
                plugins: {
                    legend: {
                        position: 'top'
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        ticks: {
                            stepSize: 1
                        }
                    }
                }
            }
        });
    }

    renderStatusChart(data) {
        const ctx = document.getElementById('statusChart').getContext('2d');
        
        if (this.charts.status) {
            this.charts.status.destroy();
        }

        this.charts.status = new Chart(ctx, {
            type: 'pie',
            data: {
                labels: data.map(item => item.status.replace('_', ' ').toUpperCase()),
                datasets: [{
                    data: data.map(item => item.count),
                    backgroundColor: data.map(item => item.color),
                    borderWidth: 2,
                    borderColor: '#ffffff'
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'bottom',
                        labels: {
                            padding: 15,
                            usePointStyle: true
                        }
                    }
                }
            }
        });
    }

    renderResolutionTimeChart(data) {
        const ctx = document.getElementById('resolutionTimeChart').getContext('2d');
        
        if (this.charts.resolutionTime) {
            this.charts.resolutionTime.destroy();
        }

        this.charts.resolutionTime = new Chart(ctx, {
            type: 'horizontalBar',
            data: {
                labels: data.map(item => item.category),
                datasets: [{
                    label: 'Hours',
                    data: data.map(item => item.avg_hours),
                    backgroundColor: data.map(item => item.color),
                    borderRadius: 4
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                indexAxis: 'y',
                plugins: {
                    legend: {
                        display: false
                    },
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                return `${context.parsed.x.toFixed(1)} hours`;
                            }
                        }
                    }
                },
                scales: {
                    x: {
                        beginAtZero: true
                    }
                }
            }
        });
    }

    renderAgentPerformanceTable(data) {
        const container = document.getElementById('agentPerformanceTable');
        
        if (data.length === 0) {
            container.innerHTML = '<p class="text-gray-500 text-center py-4">No agent data available</p>';
            return;
        }

        const table = `
            <div class="overflow-x-auto">
                <table class="min-w-full divide-y divide-gray-200">
                    <thead class="bg-gray-50">
                        <tr>
                            <th class="px-3 py-2 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Agent</th>
                            <th class="px-3 py-2 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Total</th>
                            <th class="px-3 py-2 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Resolved</th>
                            <th class="px-3 py-2 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Rate</th>
                        </tr>
                    </thead>
                    <tbody class="bg-white divide-y divide-gray-200">
                        ${data.map(agent => `
                            <tr>
                                <td class="px-3 py-2 whitespace-nowrap text-sm font-medium text-gray-900">${agent.agent}</td>
                                <td class="px-3 py-2 whitespace-nowrap text-sm text-gray-500">${agent.total_tickets}</td>
                                <td class="px-3 py-2 whitespace-nowrap text-sm text-gray-500">${agent.resolved_tickets}</td>
                                <td class="px-3 py-2 whitespace-nowrap text-sm text-gray-500">
                                    <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                                        agent.resolution_rate >= 80 ? 'bg-green-100 text-green-800' :
                                        agent.resolution_rate >= 60 ? 'bg-yellow-100 text-yellow-800' :
                                        'bg-red-100 text-red-800'
                                    }">
                                        ${agent.resolution_rate}%
                                    </span>
                                </td>
                            </tr>
                        `).join('')}
                    </tbody>
                </table>
            </div>
        `;
        
        container.innerHTML = table;
    }

    updateResolutionTimeMetrics(data) {
        document.getElementById('avgResolutionTime').textContent = 
            data.average_hours > 0 ? `${data.average_hours}h` : 'N/A';
        document.getElementById('totalResolved').textContent = data.resolved_count;
    }

    updateStatusMetrics(data) {
        const total = data.reduce((sum, item) => sum + item.count, 0);
        const resolved = data.find(item => item.status === 'resolved')?.count || 0;
        const resolutionRate = total > 0 ? ((resolved / total) * 100).toFixed(1) : 0;
        
        document.getElementById('resolutionRate').textContent = `${resolutionRate}%`;
    }

    updateTimeSeriesMetrics(data) {
        const thisWeek = data.slice(-7).reduce((sum, item) => sum + item.created, 0);
        document.getElementById('thisWeekTickets').textContent = thisWeek;
    }

    setupEventListeners() {
        // Time range buttons
        document.querySelectorAll('.time-range-btn').forEach(btn => {
            btn.addEventListener('click', async (e) => {
                const days = parseInt(e.target.dataset.days);
                this.currentTimeRange = days;
                
                // Update button states
                document.querySelectorAll('.time-range-btn').forEach(b => {
                    b.className = 'time-range-btn px-3 py-1 text-xs font-medium rounded-md text-gray-600 hover:bg-gray-100';
                });
                e.target.className = 'time-range-btn px-3 py-1 text-xs font-medium rounded-md bg-blue-100 text-blue-800';
                
                await this.loadTimeSeriesData(days);
            });
        });

        // Refresh button
        document.getElementById('refreshData').addEventListener('click', async () => {
            this.showLoading();
            try {
                await this.loadAllData();
            } finally {
                this.hideLoading();
            }
        });
    }

    showLoading() {
        document.getElementById('loadingOverlay').classList.remove('hidden');
    }

    hideLoading() {
        document.getElementById('loadingOverlay').classList.add('hidden');
    }

    showError(message) {
        // You can implement a toast notification system here
        console.error(message);
        alert(message);
    }
}

// Export for use in other scripts
window.AnalyticsDashboard = AnalyticsDashboard;
