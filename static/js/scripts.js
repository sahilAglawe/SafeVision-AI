// SafeVisionAI scripts.js
// Theme toggle, mobile nav, alert popup, alert sound

document.addEventListener('DOMContentLoaded', function() {
  // Theme toggle
  const themeToggle = document.getElementById('theme-toggle');
  if (themeToggle) {
    themeToggle.addEventListener('click', function() {
      document.body.classList.toggle('dark');
      localStorage.setItem('theme', document.body.classList.contains('dark') ? 'dark' : 'light');
    });
    // Load theme from storage
    if (localStorage.getItem('theme') === 'dark') {
      document.body.classList.add('dark');
    }
  }

  // Hamburger menu
  const hamburger = document.querySelector('.hamburger');
  const navLinks = document.querySelector('.nav-links');
  if (hamburger && navLinks) {
    hamburger.addEventListener('click', function() {
      navLinks.classList.toggle('open');
    });
  }

  // Alert popup
  window.showAlertPopup = function(message) {
    let popup = document.createElement('div');
    popup.className = 'alert-banner active';
    popup.innerHTML = `<i class="fa fa-exclamation-triangle"></i> ${message}`;
    document.body.appendChild(popup);
    setTimeout(() => { popup.classList.remove('active'); }, 3000);
    setTimeout(() => { popup.remove(); }, 3500);
    // Play alert sound
    let audio = new Audio('/static/images/alert.mp3');
    audio.play();
  }
});

// Real-time camera feed and detection controls
class SafeVisionController {
    constructor() {
        this.isRecording = true;
        this.detectionActive = true;
        this.threatLevel = 'LOW';
        this.updateInterval = null;
        this.statsInterval = null;
        this.alertsInterval = null;
        
        this.init();
    }

    init() {
        this.setupEventListeners();
        this.startPeriodicUpdates();
        this.loadInitialData();
    }

    setupEventListeners() {
        // Recording control
        const recordBtn = document.getElementById('record-btn');
        if (recordBtn) {
            recordBtn.addEventListener('click', () => this.toggleRecording());
        }

        // Detection control
        const detectionBtn = document.getElementById('detection-btn');
        if (detectionBtn) {
            detectionBtn.addEventListener('click', () => this.toggleDetection());
        }

        // Snapshot button
        const snapshotBtn = document.getElementById('snapshot-btn');
        if (snapshotBtn) {
            snapshotBtn.addEventListener('click', () => this.takeSnapshot());
        }

        // Clear alerts button
        const clearAlertsBtn = document.getElementById('clear-alerts-btn');
        if (clearAlertsBtn) {
            clearAlertsBtn.addEventListener('click', () => this.clearAlerts());
        }

        // Search and filter
        const searchInput = document.getElementById('search-alerts');
        if (searchInput) {
            searchInput.addEventListener('input', () => this.fetchAlerts());
        }

        const severityFilter = document.getElementById('severity-filter');
        if (severityFilter) {
            severityFilter.addEventListener('change', () => this.fetchAlerts());
        }

        // Acknowledge danger banner
        const acknowledgeBtn = document.getElementById('acknowledge-btn');
        if (acknowledgeBtn) {
            acknowledgeBtn.addEventListener('click', () => {
                document.getElementById('danger-banner').style.display = 'none';
            });
        }
    }

    async toggleRecording() {
        try {
            const response = await fetch('/api/control', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ action: 'toggle_recording' })
            });
            const data = await response.json();
            
            this.isRecording = data.recording_active;
            const recordBtn = document.getElementById('record-btn');
            const recordStatus = document.getElementById('record-status');
            
            if (recordBtn && recordStatus) {
                recordBtn.textContent = this.isRecording ? 'Stop Recording' : 'Start Recording';
                recordBtn.classList.toggle('destructive', this.isRecording);
                recordStatus.textContent = this.isRecording ? 'Recording' : 'Stopped';
            }
        } catch (error) {
            console.error('Error toggling recording:', error);
        }
    }

    async toggleDetection() {
        try {
            const response = await fetch('/api/control', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ action: 'toggle_detection' })
            });
            const data = await response.json();
            
            this.detectionActive = data.detection_active;
            const detectionBtn = document.getElementById('detection-btn');
            const aiDetectionBadge = document.getElementById('ai-detection-badge');
            
            if (detectionBtn && aiDetectionBadge) {
                detectionBtn.textContent = this.detectionActive ? 'Pause Detection' : 'Resume Detection';
                aiDetectionBadge.textContent = `AI Detection: ${this.detectionActive ? 'ACTIVE' : 'INACTIVE'}`;
                aiDetectionBadge.className = this.detectionActive ? 'badge green' : 'badge outline';
            }
        } catch (error) {
            console.error('Error toggling detection:', error);
        }
    }

    async takeSnapshot() {
        try {
            const response = await fetch('/api/snapshot');
            const data = await response.json();
            
            if (data.success) {
                alert(`Snapshot saved: ${data.filename}`);
            } else {
                alert('Failed to take snapshot');
            }
        } catch (error) {
            console.error('Error taking snapshot:', error);
            alert('Error taking snapshot');
        }
    }

    async clearAlerts() {
        if (confirm('Are you sure you want to clear all alerts? This action cannot be undone.')) {
            try {
                const response = await fetch('/api/clear_alerts', { method: 'POST' });
                const data = await response.json();
                
                if (data.success) {
                    alert('All alerts cleared successfully');
                    this.fetchAlerts();
                    this.fetchStats();
                }
            } catch (error) {
                console.error('Error clearing alerts:', error);
                alert('Error clearing alerts');
            }
        }
    }

    async fetchStats() {
        try {
            const response = await fetch('/api/stats');
            const stats = await response.json();
            
            // Update dashboard stats
            this.updateStatElement('total-alerts', stats.total_alerts);
            this.updateStatElement('last-detection', stats.last_detection);
            this.updateStatElement('active-cameras', `${stats.active_cameras}/1`);
            this.updateStatElement('threat-level', stats.threat_level);
            this.updateStatElement('detection-accuracy', `${stats.detection_accuracy}%`);
            this.updateStatElement('objects-detected', stats.total_alerts);
            
            // Update threat level color
            this.updateThreatLevelColor(stats.threat_level);
            
            // Update descriptions
            this.updateStatDescription('alerts-desc', stats.total_alerts > 0 ? `+${stats.threat_detections} high priority` : 'No alerts yet');
            this.updateStatDescription('detection-desc', stats.last_detection !== 'No detections yet' ? 'Recent activity detected' : 'System ready');
            this.updateStatDescription('camera-status', stats.active_cameras > 0 ? 'All systems operational' : 'Camera offline');
            
            // Update threat alert visibility
            this.updateThreatAlert(stats.threat_level);
            
        } catch (error) {
            console.error('Error fetching stats:', error);
        }
    }

    async fetchAlerts() {
        try {
            const response = await fetch('/api/alerts');
            const alerts = await response.json();
            
            // Update recent alerts in dashboard
            this.updateRecentAlerts(alerts.slice(0, 3));
            
            // Update alert history table
            this.renderAlertHistory(alerts);
            
        } catch (error) {
            console.error('Error fetching alerts:', error);
        }
    }

    updateStatElement(id, value) {
        const element = document.getElementById(id);
        if (element) {
            element.textContent = value;
        }
    }

    updateStatDescription(id, text) {
        const element = document.getElementById(id);
        if (element) {
            element.textContent = text;
        }
    }

    updateThreatLevelColor(threatLevel) {
        const threatLevelEl = document.getElementById('threat-level');
        if (threatLevelEl) {
            threatLevelEl.className = 'stat-value ' + 
                (threatLevel === 'HIGH' ? 'red' : 
                 threatLevel === 'MEDIUM' ? 'orange' : 'green');
        }
    }

    updateThreatAlert(threatLevel) {
        const threatAlert = document.getElementById('threat-alert');
        if (threatAlert) {
            threatAlert.style.display = threatLevel === 'HIGH' ? '' : 'none';
        }
    }

    updateRecentAlerts(alerts) {
        const recentAlertsContainer = document.getElementById('recent-alerts');
        if (!recentAlertsContainer) return;
        
        recentAlertsContainer.innerHTML = '';
        
        alerts.forEach(alert => {
            const div = document.createElement('div');
            div.className = `alert ${alert.severity.toLowerCase()}`;
            div.innerHTML = `
                <div class="alert-icon"></div>
                <div>
                    <div class="alert-title">${alert.detectedClass}</div>
                    <div class="alert-desc">${alert.description}</div>
                    <div class="alert-meta">${alert.timestamp} • ${alert.zone}</div>
                </div>
            `;
            recentAlertsContainer.appendChild(div);
        });
    }

    renderAlertHistory(alerts) {
        const list = document.getElementById('alert-history-list');
        if (!list) return;
        
        const search = document.getElementById('search-alerts')?.value.toLowerCase() || '';
        const severity = document.getElementById('severity-filter')?.value || 'all';
        
        list.innerHTML = '';
        
        if (alerts.length === 0) {
            list.innerHTML = '<p style="text-align: center; color: #64748b; padding: 2rem;">No alerts found</p>';
            return;
        }
        
        // Table header
        const table = document.createElement('table');
        table.className = 'alert-table';
        table.innerHTML = `
            <thead>
                <tr>
                    <th>Alert ID</th>
                    <th>Timestamp</th>
                    <th>Detection Type</th>
                    <th>Severity</th>
                    <th>Zone</th>
                    <th>Description</th>
                    <th>Confidence</th>
                </tr>
            </thead>
            <tbody></tbody>
        `;
        
        const tbody = table.querySelector('tbody');
        alerts.filter(alert => {
            const matchesSearch = alert.detectedClass.toLowerCase().includes(search) || 
                                 alert.description.toLowerCase().includes(search) || 
                                 alert.id.toLowerCase().includes(search);
            const matchesSeverity = severity === 'all' || alert.severity === severity;
            return matchesSearch && matchesSeverity;
        }).forEach(alert => {
            const tr = document.createElement('tr');
            tr.innerHTML = `
                <td>${alert.id}</td>
                <td>${alert.timestamp}</td>
                <td>${alert.detectedClass}</td>
                <td><span class="alert-severity ${alert.severity.toLowerCase()}">${alert.severity}</span></td>
                <td>${alert.zone}</td>
                <td>${alert.description}</td>
                <td>${alert.confidence}</td>
            `;
            tbody.appendChild(tr);
        });
        
        list.appendChild(table);
    }

    startPeriodicUpdates() {
        // Update stats every 5 seconds
        this.statsInterval = setInterval(() => this.fetchStats(), 5000);
        
        // Update alerts every 10 seconds
        this.alertsInterval = setInterval(() => this.fetchAlerts(), 10000);
    }

    loadInitialData() {
        this.fetchStats();
        this.fetchAlerts();
    }

    destroy() {
        if (this.statsInterval) clearInterval(this.statsInterval);
        if (this.alertsInterval) clearInterval(this.alertsInterval);
    }
}

// Initialize the controller when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    window.safeVisionController = new SafeVisionController();
}); 