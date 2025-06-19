// app/static/js/modern-features.js

/**
 * Modern AI Research Platform Frontend
 * Complete feature-rich JavaScript library with HTML compatibility fixes
 */

class ModernPlatform {
    constructor() {
        this.themes = [
            { id: 'dark', name: '🌙 Dark', description: 'Default Dark Theme' },
            { id: 'light', name: '☀️ Light', description: 'Clean Light Theme' },
            { id: 'cyberpunk', name: '🌈 Cyberpunk', description: 'Neon Cyberpunk Style' },
            { id: 'nature', name: '🌿 Nature', description: 'Green Nature Theme' },
            { id: 'ocean', name: '🌊 Ocean', description: 'Deep Ocean Blue' },
            { id: 'fire', name: '🔥 Fire', description: 'Hot Fire Theme' }
        ];
        
        this.currentTheme = localStorage.getItem('platform-theme') || 'dark';
        this.notifications = [];
        this.modals = new Map();
        this.charts = new Map();
        
        this.init();
    }
    
    init() {
        this.applyTheme(this.currentTheme);
        this.initThemeSwatcher();
        this.initNotifications();
        this.initModals();
        this.initDragDrop();
        this.initCharts();
        this.initSearch();
        this.initLazyLoading();
        this.initKeyboardShortcuts();
        this.initProgressBars();
        this.bindEvents();
        
        // Add new initialization methods
        this.initSidebarState();
        this.initMobileHandlers();
        this.initPerformanceMonitoring();
        this.initAccessibility();
        
        console.log('🚀 Modern Platform initialized with enhanced features!');
        
        // Welcome notification
        setTimeout(() => {
            this.notify(
                'Platform Ready!', 
                'Tutte le funzionalità sono attive. Premi Ctrl+K per cercare.', 
                'success', 
                4000
            );
        }, 1000);
    }
    
    // ===== HTML COMPATIBILITY METHODS =====
    
    toggleSidebar() {
        const layout = document.getElementById('app-layout');
        const sidebar = document.getElementById('app-sidebar');
        const overlay = document.getElementById('sidebar-overlay');
        
        if (window.innerWidth <= 1024) {
            // Mobile: sliding sidebar
            sidebar.classList.toggle('open');
            overlay.classList.toggle('open');
            
            // Prevent body scroll when sidebar is open
            if (sidebar.classList.contains('open')) {
                document.body.style.overflow = 'hidden';
            } else {
                document.body.style.overflow = '';
            }
        } else {
            // Desktop: collapsible sidebar
            layout.classList.toggle('sidebar-collapsed');
            
            // Save state
            const isCollapsed = layout.classList.contains('sidebar-collapsed');
            localStorage.setItem('sidebar-collapsed', isCollapsed);
        }
        
        this.emit('sidebarToggled', { 
            isMobile: window.innerWidth <= 1024,
            isOpen: sidebar.classList.contains('open'),
            isCollapsed: layout.classList.contains('sidebar-collapsed')
        });
    }

    toggleTheme() {
        const currentIndex = this.themes.findIndex(t => t.id === this.currentTheme);
        const nextTheme = this.themes[(currentIndex + 1) % this.themes.length];
        
        this.applyTheme(nextTheme.id);
        
        // Show toast notification
        this.notify(
            'Tema Cambiato', 
            `Attivato tema ${nextTheme.name}`, 
            'success', 
            2000
        );
        
        console.log(`🎨 Theme changed to: ${nextTheme.id}`);
    }

    showNotifications() {
        // Check if dropdown already exists
        const existingDropdown = document.getElementById('notifications-dropdown');
        if (existingDropdown) {
            existingDropdown.remove();
            return;
        }
        
        // Create notifications dropdown
        const dropdown = document.createElement('div');
        dropdown.id = 'notifications-dropdown';
        dropdown.className = 'notifications-dropdown';
        dropdown.style.cssText = `
            position: fixed;
            top: 60px;
            right: 20px;
            width: 380px;
            max-height: 500px;
            background: var(--bg-elevated);
            border: 1px solid var(--border-default);
            border-radius: var(--radius-lg);
            box-shadow: var(--shadow-2xl);
            z-index: var(--z-modal);
            overflow: hidden;
            animation: slideDown 0.3s ease-out;
        `;
        
        // Generate mock notifications
        const notifications = this.generateMockNotifications();
        
        dropdown.innerHTML = `
            <div class="notifications-header" style="padding: var(--space-4); border-bottom: 1px solid var(--border-subtle); display: flex; justify-content: space-between; align-items: center;">
                <div>
                    <h3 style="color: var(--text-primary); font-size: var(--text-lg); margin: 0;">Notifiche</h3>
                    <small style="color: var(--text-tertiary);">${notifications.length} nuove</small>
                </div>
                <button onclick="document.getElementById('notifications-dropdown').remove()" 
                        style="background: none; border: none; color: var(--text-secondary); cursor: pointer; padding: 4px; border-radius: var(--radius-sm);">
                    <i class="fas fa-times"></i>
                </button>
            </div>
            <div class="notifications-body" style="max-height: 350px; overflow-y: auto;">
                ${notifications.map(notification => this.createNotificationItem(notification)).join('')}
            </div>
            <div class="notifications-footer" style="padding: var(--space-3); text-align: center; border-top: 1px solid var(--border-subtle);">
                <button onclick="platform.markAllNotificationsRead()" 
                        style="background: none; border: none; color: var(--accent-blue); cursor: pointer; font-size: var(--text-sm); padding: var(--space-2);">
                    Segna tutte come lette
                </button>
            </div>
        `;
        
        // Add animation styles
        this.addNotificationStyles();
        
        document.body.appendChild(dropdown);
        
        // Close on click outside
        setTimeout(() => {
            document.addEventListener('click', this.closeNotificationsOnOutsideClick.bind(this), { once: true });
        }, 100);
        
        this.emit('notificationsOpened');
    }

    performSearch(query) {
        if (!query || query.trim().length < 2) {
            this.notify('Ricerca', 'Inserisci almeno 2 caratteri per cercare', 'warning', 3000);
            return;
        }
        
        query = query.trim();
        
        // Show loading toast
        const loadingToast = this.notify('Ricerca', `Cercando "${query}"...`, 'info', 0);
        
        // Simulate search delay
        setTimeout(() => {
            this.removeToast(loadingToast);
            
            // Redirect to search page with query
            const searchUrl = `/search/view?q=${encodeURIComponent(query)}`;
            window.location.href = searchUrl;
        }, 500);
        
        // Log search
        console.log(`🔍 Search performed: "${query}"`);
        
        // Emit search event
        this.emit('searchPerformed', { query, timestamp: new Date() });
    }

    showToast(title, message, type = 'info', duration = 3000) {
        return this.notify(title, message, type, duration);
    }

    // ===== NOTIFICATION HELPERS =====
    
    generateMockNotifications() {
        return [
            {
                id: 1,
                title: 'Sistema Aggiornato',
                message: 'Nuove funzionalità disponibili nella dashboard',
                type: 'info',
                time: '2 minuti fa',
                read: false,
                icon: 'fas fa-info-circle'
            },
            {
                id: 2,
                title: 'Import Completato',
                message: '25 nuove fonti aggiunte al progetto "Ricerca AI"',
                type: 'success',
                time: '15 minuti fa',
                read: false,
                icon: 'fas fa-check-circle'
            },
            {
                id: 3,
                title: 'Elaborazione in Corso',
                message: 'Processando contenuti del progetto "Deep Learning"',
                type: 'warning',
                time: '1 ora fa',
                read: false,
                icon: 'fas fa-cog fa-spin'
            },
            {
                id: 4,
                title: 'Backup Completato',
                message: 'Tutti i dati sono stati salvati correttamente',
                type: 'success',
                time: '3 ore fa',
                read: true,
                icon: 'fas fa-cloud-upload-alt'
            }
        ];
    }

    createNotificationItem(notification) {
        const typeColors = {
            info: 'var(--accent-blue)',
            success: 'var(--accent-green)',
            warning: 'var(--accent-orange)',
            error: 'var(--accent-red)'
        };

        return `
            <div class="notification-item ${notification.read ? 'read' : 'unread'}" 
                 style="padding: var(--space-4); border-bottom: 1px solid var(--border-subtle); cursor: pointer; transition: background 0.2s;"
                 onclick="platform.markNotificationRead(${notification.id})">
                <div style="display: flex; align-items: flex-start; gap: var(--space-3);">
                    <div style="color: ${typeColors[notification.type]}; font-size: var(--text-lg); margin-top: 2px;">
                        <i class="${notification.icon}"></i>
                    </div>
                    <div style="flex: 1;">
                        <div style="color: var(--text-primary); font-weight: ${notification.read ? '400' : '600'}; margin-bottom: var(--space-1);">
                            ${notification.title}
                        </div>
                        <div style="color: var(--text-secondary); font-size: var(--text-sm); margin-bottom: var(--space-1); line-height: 1.4;">
                            ${notification.message}
                        </div>
                        <div style="color: var(--text-tertiary); font-size: var(--text-xs);">
                            ${notification.time}
                        </div>
                    </div>
                    ${!notification.read ? '<div style="width: 8px; height: 8px; background: var(--accent-blue); border-radius: 50%; margin-top: 6px;"></div>' : ''}
                </div>
            </div>
        `;
    }

    addNotificationStyles() {
        if (document.getElementById('notification-styles')) return;
        
        const style = document.createElement('style');
        style.id = 'notification-styles';
        style.textContent = `
            @keyframes slideDown {
                from { 
                    opacity: 0; 
                    transform: translateY(-10px) scale(0.95); 
                }
                to { 
                    opacity: 1; 
                    transform: translateY(0) scale(1); 
                }
            }
            
            .notification-item:hover {
                background: var(--bg-tertiary) !important;
            }
            
            .notification-item.unread {
                background: rgba(59, 130, 246, 0.05);
            }
            
            .notifications-dropdown {
                backdrop-filter: blur(10px);
            }
        `;
        document.head.appendChild(style);
    }

    closeNotificationsOnOutsideClick(e) {
        const dropdown = document.getElementById('notifications-dropdown');
        if (dropdown && !dropdown.contains(e.target)) {
            dropdown.remove();
        }
    }

    markNotificationRead(id) {
        console.log(`📧 Notification ${id} marked as read`);
        this.notify('Notifica', 'Notifica contrassegnata come letta', 'success', 1500);
    }

    markAllNotificationsRead() {
        const dropdown = document.getElementById('notifications-dropdown');
        if (dropdown) {
            dropdown.remove();
        }
        this.notify('Notifiche', 'Tutte le notifiche sono state contrassegnate come lette', 'success');
    }

    initSidebarState() {
        // Restore sidebar state on desktop
        if (window.innerWidth > 1024) {
            const isCollapsed = localStorage.getItem('sidebar-collapsed') === 'true';
            const layout = document.getElementById('app-layout');
            
            if (isCollapsed && layout) {
                layout.classList.add('sidebar-collapsed');
            }
        }
    }

    initMobileHandlers() {
        // Close sidebar when clicking overlay
        const overlay = document.getElementById('sidebar-overlay');
        if (overlay) {
            overlay.addEventListener('click', () => {
                const sidebar = document.getElementById('app-sidebar');
                if (sidebar) {
                    sidebar.classList.remove('open');
                    overlay.classList.remove('open');
                    document.body.style.overflow = '';
                }
            });
        }

        // Handle window resize
        window.addEventListener('resize', () => {
            if (window.innerWidth > 1024) {
                // Desktop: close mobile sidebar if open
                const sidebar = document.getElementById('app-sidebar');
                const overlay = document.getElementById('sidebar-overlay');
                
                if (sidebar && sidebar.classList.contains('open')) {
                    sidebar.classList.remove('open');
                    overlay?.classList.remove('open');
                    document.body.style.overflow = '';
                }
            }
        });
    }
    
    // ===== THEME SYSTEM =====
    applyTheme(themeId) {
        document.body.setAttribute('data-theme', themeId);
        this.currentTheme = themeId;
        localStorage.setItem('platform-theme', themeId);
        
        // Update theme button
        const btn = document.getElementById('theme-btn');
        if (btn) {
            const theme = this.themes.find(t => t.id === themeId);
            btn.innerHTML = `${theme.name} ▼`;
        }
        
        // Emit theme change event
        this.emit('themeChanged', { theme: themeId });
    }
    
    initThemeSwatcher() {
        // The theme button is already in HTML, we just need to handle clicks
        const themeBtn = document.getElementById('theme-btn');
        if (themeBtn) {
            themeBtn.addEventListener('click', (e) => {
                e.preventDefault();
                e.stopPropagation();
                this.toggleTheme();
            });
        }
    }
    
    // ===== NOTIFICATION SYSTEM =====
    initNotifications() {
        // Create toast container
        const container = document.createElement('div');
        container.id = 'toast-container';
        container.className = 'toast-container';
        container.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            z-index: var(--z-toast);
            display: flex;
            flex-direction: column;
            gap: var(--space-2);
        `;
        document.body.appendChild(container);

        // Setup notifications button
        const notificationBtn = document.getElementById('notifications-btn');
        if (notificationBtn) {
            notificationBtn.addEventListener('click', (e) => {
                e.preventDefault();
                e.stopPropagation();
                this.showNotifications();
            });
        }
    }
    
    notify(title, message, type = 'info', duration = 5000) {
        const toast = document.createElement('div');
        toast.className = `toast ${type}`;
        toast.style.cssText = `
            background: var(--bg-elevated);
            border: 1px solid var(--border-default);
            border-radius: var(--radius-lg);
            padding: var(--space-4);
            min-width: 300px;
            max-width: 400px;
            box-shadow: var(--shadow-lg);
            display: flex;
            align-items: flex-start;
            gap: var(--space-3);
            transform: translateX(100%);
            transition: all 0.3s ease;
            opacity: 0;
        `;
        
        const icons = {
            success: '✅',
            error: '❌',
            warning: '⚠️',
            info: 'ℹ️'
        };
        
        toast.innerHTML = `
            <div class="toast-icon" style="font-size: var(--text-lg);">${icons[type] || icons.info}</div>
            <div class="toast-content" style="flex: 1;">
                <div class="toast-title" style="color: var(--text-primary); font-weight: 600; margin-bottom: var(--space-1);">${title}</div>
                <div class="toast-message" style="color: var(--text-secondary); font-size: var(--text-sm); line-height: 1.4;">${message}</div>
            </div>
            <button class="toast-close" style="background: none; border: none; color: var(--text-secondary); cursor: pointer; padding: 0; font-size: var(--text-lg);">×</button>
        `;
        
        const container = document.getElementById('toast-container');
        container.appendChild(toast);
        
        // Show animation
        setTimeout(() => {
            toast.style.transform = 'translateX(0)';
            toast.style.opacity = '1';
        }, 100);
        
        // Auto remove
        if (duration > 0) {
            setTimeout(() => this.removeToast(toast), duration);
        }
        
        // Close button
        toast.querySelector('.toast-close').onclick = () => this.removeToast(toast);
        
        return toast;
    }
    
    removeToast(toast) {
        toast.style.transform = 'translateX(100%)';
        toast.style.opacity = '0';
        setTimeout(() => {
            if (toast.parentNode) {
                toast.parentNode.removeChild(toast);
            }
        }, 300);
    }
    
    // ===== MODAL SYSTEM =====
    initModals() {
        // Close modals with Escape key
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape') {
                this.closeAllModals();
            }
        });
    }
    
    showModal(id, options = {}) {
        const modal = document.getElementById(id);
        if (!modal) {
            console.warn(`Modal with id "${id}" not found`);
            return;
        }
        
        modal.classList.add('active');
        document.body.style.overflow = 'hidden';
        
        // Focus first input
        const firstInput = modal.querySelector('input, textarea, select');
        if (firstInput) {
            setTimeout(() => firstInput.focus(), 100);
        }
        
        this.modals.set(id, modal);
        this.emit('modalOpened', { id, modal });
    }
    
    closeModal(id) {
        const modal = document.getElementById(id);
        if (modal) {
            modal.classList.remove('active');
            document.body.style.overflow = '';
            this.modals.delete(id);
            this.emit('modalClosed', { id, modal });
        }
    }
    
    closeAllModals() {
        this.modals.forEach((modal, id) => {
            this.closeModal(id);
        });
    }
    
    createModal(id, title, content, options = {}) {
        const overlay = document.createElement('div');
        overlay.className = 'modal-overlay';
        overlay.id = id;
        
        overlay.innerHTML = `
            <div class="modal">
                <div class="modal-header">
                    <h3 class="modal-title">${title}</h3>
                    <button class="modal-close" onclick="platform.closeModal('${id}')">×</button>
                </div>
                <div class="modal-body">
                    ${content}
                </div>
                ${options.footer ? `<div class="modal-footer">${options.footer}</div>` : ''}
            </div>
        `;
        
        // Close on backdrop click
        overlay.addEventListener('click', (e) => {
            if (e.target === overlay) {
                this.closeModal(id);
            }
        });
        
        document.body.appendChild(overlay);
        return overlay;
    }
    
    // ===== DRAG & DROP =====
    initDragDrop() {
        const dropZones = document.querySelectorAll('[data-drop-zone]');
        
        dropZones.forEach(zone => {
            zone.addEventListener('dragover', this.handleDragOver.bind(this));
            zone.addEventListener('drop', this.handleDrop.bind(this));
            zone.addEventListener('dragenter', this.handleDragEnter.bind(this));
            zone.addEventListener('dragleave', this.handleDragLeave.bind(this));
        });
    }
    
    handleDragOver(e) {
        e.preventDefault();
        e.currentTarget.classList.add('drag-over');
    }
    
    handleDragEnter(e) {
        e.preventDefault();
        e.currentTarget.classList.add('drag-active');
    }
    
    handleDragLeave(e) {
        e.currentTarget.classList.remove('drag-over', 'drag-active');
    }
    
    handleDrop(e) {
        e.preventDefault();
        const zone = e.currentTarget;
        zone.classList.remove('drag-over', 'drag-active');
        
        const files = Array.from(e.dataTransfer.files);
        if (files.length > 0) {
            this.handleFileUpload(files, zone);
        }
    }
    
    handleFileUpload(files, zone) {
        const allowedTypes = zone.dataset.allowedTypes?.split(',') || [];
        const maxSize = parseInt(zone.dataset.maxSize) || 10 * 1024 * 1024; // 10MB default
        
        files.forEach(file => {
            // Validate file type
            if (allowedTypes.length > 0 && !allowedTypes.some(type => file.name.endsWith(type))) {
                this.notify('File Error', `File type not allowed: ${file.name}`, 'error');
                return;
            }
            
            // Validate file size
            if (file.size > maxSize) {
                this.notify('File Error', `File too large: ${file.name}`, 'error');
                return;
            }
            
            this.uploadFile(file, zone);
        });
    }
    
    uploadFile(file, zone) {
        const formData = new FormData();
        formData.append('file', file);
        
        // Create progress bar
        const progressId = 'upload-' + Date.now();
        const progressHtml = `
            <div class="upload-progress" id="${progressId}">
                <div class="upload-info">
                    <span class="file-name">${file.name}</span>
                    <span class="file-size">${this.formatFileSize(file.size)}</span>
                </div>
                <div class="progress">
                    <div class="progress-bar" style="width: 0%"></div>
                </div>
            </div>
        `;
        
        zone.insertAdjacentHTML('beforeend', progressHtml);
        const progressElement = document.getElementById(progressId);
        const progressBar = progressElement.querySelector('.progress-bar');
        
        // Simulate upload progress (replace with real XMLHttpRequest)
        let progress = 0;
        const interval = setInterval(() => {
            progress += Math.random() * 15;
            if (progress >= 100) {
                progress = 100;
                clearInterval(interval);
                
                setTimeout(() => {
                    progressElement.remove();
                    this.notify('Upload Complete', `${file.name} uploaded successfully`, 'success');
                }, 500);
            }
            
            progressBar.style.width = progress + '%';
        }, 200);
    }
    
    formatFileSize(bytes) {
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    }
    
    // ===== SEARCH WITH AUTOCOMPLETE =====
    initSearch() {
        const searchInputs = document.querySelectorAll('[data-search]');
        
        searchInputs.forEach(input => {
            let timeout;
            const dropdown = this.createSearchDropdown(input);
            
            // Search on Enter key
            input.addEventListener('keypress', (e) => {
                if (e.key === 'Enter') {
                    e.preventDefault();
                    this.performSearch(input.value);
                }
            });
            
            input.addEventListener('input', (e) => {
                clearTimeout(timeout);
                timeout = setTimeout(() => {
                    this.performSearchAutocomplete(e.target.value, dropdown, input);
                }, 300);
            });
            
            // Hide dropdown when clicking outside
            document.addEventListener('click', (e) => {
                if (!input.contains(e.target) && !dropdown.contains(e.target)) {
                    dropdown.style.display = 'none';
                }
            });
        });
    }
    
    createSearchDropdown(input) {
        const dropdown = document.createElement('div');
        dropdown.className = 'search-dropdown';
        dropdown.style.cssText = `
            position: absolute;
            top: 100%;
            left: 0;
            right: 0;
            background: var(--bg-elevated);
            border: 1px solid var(--border-default);
            border-radius: var(--radius-lg);
            box-shadow: var(--shadow-lg);
            max-height: 300px;
            overflow-y: auto;
            z-index: var(--z-dropdown);
            display: none;
        `;
        
        const container = input.parentNode;
        container.style.position = 'relative';
        container.appendChild(dropdown);
        
        return dropdown;
    }
    
    performSearchAutocomplete(query, dropdown, input) {
        if (query.length < 2) {
            dropdown.style.display = 'none';
            return;
        }
        
        // Show loading
        dropdown.innerHTML = '<div class="search-loading" style="padding: var(--space-3); text-align: center; color: var(--text-secondary);">🔍 Searching...</div>';
        dropdown.style.display = 'block';
        
        // Simulate API call (replace with real fetch)
        setTimeout(() => {
            const results = this.mockSearchResults(query);
            this.displaySearchResults(results, dropdown, input);
        }, 500);
    }
    
    mockSearchResults(query) {
        const mockData = [
            { title: 'Project Alpha', type: 'project', url: '/projects/1' },
            { title: 'Beta Analysis Report', type: 'document', url: '/docs/beta' },
            { title: 'Data Source Gamma', type: 'source', url: '/sources/gamma' },
            { title: 'Research Notes Delta', type: 'note', url: '/notes/delta' }
        ];
        
        return mockData.filter(item => 
            item.title.toLowerCase().includes(query.toLowerCase())
        );
    }
    
    displaySearchResults(results, dropdown, input) {
        if (results.length === 0) {
            dropdown.innerHTML = '<div class="search-empty" style="padding: var(--space-3); text-align: center; color: var(--text-tertiary);">Nessun risultato trovato</div>';
            return;
        }
        
        const html = results.map(result => `
            <div class="search-result" onclick="platform.selectSearchResult('${result.url}')" style="padding: var(--space-3); cursor: pointer; border-bottom: 1px solid var(--border-subtle); transition: background 0.2s;">
                <div class="result-title" style="color: var(--text-primary); font-weight: 500;">${result.title}</div>
                <div class="result-type" style="color: var(--text-tertiary); font-size: var(--text-xs); text-transform: uppercase;">${result.type}</div>
            </div>
        `).join('');
        
        dropdown.innerHTML = html;
        
        // Add hover styles
        const style = document.createElement('style');
        style.textContent = '.search-result:hover { background: var(--bg-tertiary) !important; }';
        if (!document.getElementById('search-result-styles')) {
            style.id = 'search-result-styles';
            document.head.appendChild(style);
        }
    }
    
    selectSearchResult(url) {
        window.location.href = url;
    }
    
    // ===== CHARTS AND VISUALIZATIONS =====
    initCharts() {
        // Initialize Chart.js if available
        if (typeof Chart !== 'undefined') {
            this.createDashboardCharts();
        }
    }
    
    createDashboardCharts() {
        // Projects overview chart
        const projectsCanvas = document.getElementById('projects-chart');
        if (projectsCanvas) {
            const ctx = projectsCanvas.getContext('2d');
            this.charts.set('projects', new Chart(ctx, {
                type: 'doughnut',
                data: {
                    labels: ['Active', 'Completed', 'Pending'],
                    datasets: [{
                        data: [12, 8, 3],
                        backgroundColor: [
                            'var(--accent-green)',
                            'var(--accent-blue)',
                            'var(--accent-orange)'
                        ],
                        borderWidth: 0
                    }]
                },
                options: {
                    responsive: true,
                    plugins: {
                        legend: {
                            position: 'bottom',
                            labels: {
                                color: 'var(--text-primary)',
                                usePointStyle: true,
                                padding: 20
                            }
                        }
                    }
                }
            }));
        }
        
        // Activity timeline chart
        const activityCanvas = document.getElementById('activity-chart');
        if (activityCanvas) {
            const ctx = activityCanvas.getContext('2d');
            this.charts.set('activity', new Chart(ctx, {
                type: 'line',
                data: {
                    labels: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
                    datasets: [{
                        label: 'Research Activity',
                        data: [12, 19, 8, 15, 25, 8, 14],
                        borderColor: 'var(--accent-blue)',
                        backgroundColor: 'rgba(59, 130, 246, 0.1)',
                        tension: 0.4,
                        fill: true
                    }]
                },
                options: {
                    responsive: true,
                    scales: {
                        y: {
                            beginAtZero: true,
                            grid: {
                                color: 'var(--border-subtle)'
                            },
                            ticks: {
                                color: 'var(--text-secondary)'
                            }
                        },
                        x: {
                            grid: {
                                color: 'var(--border-subtle)'
                            },
                            ticks: {
                                color: 'var(--text-secondary)'
                            }
                        }
                    },
                    plugins: {
                        legend: {
                            labels: {
                                color: 'var(--text-primary)'
                            }
                        }
                    }
                }
            }));
        }
    }
    
    // ===== LAZY LOADING =====
    initLazyLoading() {
        if ('IntersectionObserver' in window) {
            const imageObserver = new IntersectionObserver((entries, observer) => {
                entries.forEach(entry => {
                    if (entry.isIntersecting) {
                        const img = entry.target;
                        img.src = img.dataset.src;
                        img.classList.remove('lazy');
                        observer.unobserve(img);
                    }
                });
            });
            
            const lazyImages = document.querySelectorAll('img[data-src]');
            lazyImages.forEach(img => {
                img.classList.add('lazy');
                imageObserver.observe(img);
            });
            
            // Lazy load sections
            const sectionObserver = new IntersectionObserver((entries) => {
                entries.forEach(entry => {
                    if (entry.isIntersecting) {
                        entry.target.classList.add('animate-in');
                    }
                });
            });
            
            const sections = document.querySelectorAll('[data-animate]');
            sections.forEach(section => {
                sectionObserver.observe(section);
            });
        }
    }
    
    // ===== KEYBOARD SHORTCUTS =====
    initKeyboardShortcuts() {
        document.addEventListener('keydown', (e) => {
            // Ctrl/Cmd + K for search
            if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
                e.preventDefault();
                this.focusSearch();
            }
            
            // Ctrl/Cmd + N for new project
            if ((e.ctrlKey || e.metaKey) && e.key === 'n') {
                e.preventDefault();
                this.showModal('new-project-modal');
            }
            
            // Ctrl/Cmd + , for settings
            if ((e.ctrlKey || e.metaKey) && e.key === ',') {
                e.preventDefault();
                this.showModal('settings-modal');
            }
            
            // Escape to close current modal
            if (e.key === 'Escape') {
                this.closeAllModals();
            }
        });
    }
    
    focusSearch() {
        const searchInput = document.querySelector('[data-search]');
        if (searchInput) {
            searchInput.focus();
            searchInput.select();
        }
    }
    
    // ===== PROGRESS BARS =====
    initProgressBars() {
        const progressBars = document.querySelectorAll('[data-progress]');
        
        progressBars.forEach(bar => {
            const targetValue = parseInt(bar.dataset.progress) || 0;
            const progressFill = bar.querySelector('.progress-bar');
            
            if (progressFill) {
                // Animate to target value
                this.animateProgress(progressFill, 0, targetValue, 1000);
            }
        });
    }
    
    animateProgress(element, start, end, duration) {
        const startTime = performance.now();
        
        const updateProgress = (currentTime) => {
            const elapsed = currentTime - startTime;
            const progress = Math.min(elapsed / duration, 1);
            const currentValue = start + (end - start) * this.easeOutCubic(progress);
            
            element.style.width = currentValue + '%';
            
            if (progress < 1) {
                requestAnimationFrame(updateProgress);
            }
        };
        
        requestAnimationFrame(updateProgress);
    }
    
    easeOutCubic(t) {
        return 1 - Math.pow(1 - t, 3);
    }
    
    // ===== REAL-TIME DATA =====
    initRealTime() {
        // Simulate real-time updates
        setInterval(() => {
            this.updateDashboardStats();
        }, 30000); // Every 30 seconds
        
        // WebSocket connection (if available)
        if ('WebSocket' in window) {
            this.initWebSocket();
        }
    }
    
    updateDashboardStats() {
        fetch('/api/stats')
            .then(response => response.json())
            .then(data => {
                this.updateStatCards(data);
                this.emit('statsUpdated', data);
            })
            .catch(error => {
                console.warn('Failed to update stats:', error);
            });
    }
    
    updateStatCards(stats) {
        const statCards = document.querySelectorAll('[data-stat]');
        
        statCards.forEach(card => {
            const statType = card.dataset.stat;
            const valueElement = card.querySelector('.stat-value');
            
            if (valueElement && stats[statType] !== undefined) {
                const oldValue = parseInt(valueElement.textContent) || 0;
                const newValue = stats[statType];
                
                if (oldValue !== newValue) {
                    this.animateNumber(valueElement, oldValue, newValue, 1000);
                    
                    // Add pulse animation
                    card.classList.add('updated');
                    setTimeout(() => card.classList.remove('updated'), 1000);
                }
            }
        });
    }
    
    animateNumber(element, start, end, duration) {
        const startTime = performance.now();
        
        const updateNumber = (currentTime) => {
            const elapsed = currentTime - startTime;
            const progress = Math.min(elapsed / duration, 1);
            const currentValue = Math.round(start + (end - start) * this.easeOutCubic(progress));
            
            element.textContent = currentValue;
            
            if (progress < 1) {
                requestAnimationFrame(updateNumber);
            }
        };
        
        requestAnimationFrame(updateNumber);
    }
    
    // ===== EVENT SYSTEM =====
    emit(eventName, data) {
        const event = new CustomEvent(eventName, { detail: data });
        document.dispatchEvent(event);
    }
    
    on(eventName, callback) {
        document.addEventListener(eventName, callback);
    }
    
    off(eventName, callback) {
        document.removeEventListener(eventName, callback);
    }
    
    // ===== UTILITIES =====
    bindEvents() {
        // Bind click events for buttons
        document.addEventListener('click', (e) => {
            // Modal triggers
            if (e.target.matches('[data-modal]')) {
                e.preventDefault();
                const modalId = e.target.dataset.modal;
                this.showModal(modalId);
            }
            
            // Notification triggers
            if (e.target.matches('[data-notify]')) {
                e.preventDefault();
                const { title, message, type } = e.target.dataset;
                this.notify(title || 'Notification', message || 'Something happened', type || 'info');
            }
            
            // Copy to clipboard
            if (e.target.matches('[data-copy]')) {
                e.preventDefault();
                const text = e.target.dataset.copy;
                navigator.clipboard.writeText(text).then(() => {
                    this.notify('Copied!', 'Text copied to clipboard', 'success', 2000);
                });
            }
        });
        
        // Form enhancements
        document.addEventListener('submit', (e) => {
            if (e.target.matches('[data-ajax]')) {
                e.preventDefault();
                this.submitFormAjax(e.target);
            }
        });
    }
    
    submitFormAjax(form) {
        const formData = new FormData(form);
        const submitBtn = form.querySelector('[type="submit"]');
        
        // Show loading state
        if (submitBtn) {
            submitBtn.classList.add('btn-loading');
            submitBtn.disabled = true;
        }
        
        fetch(form.action, {
            method: form.method || 'POST',
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                this.notify('Success!', data.message || 'Form submitted successfully', 'success');
                form.reset();
            } else {
                this.notify('Error', data.message || 'Something went wrong', 'error');
            }
        })
        .catch(error => {
            this.notify('Error', 'Network error occurred', 'error');
            console.error('Form submission error:', error);
        })
        .finally(() => {
            // Remove loading state
            if (submitBtn) {
                submitBtn.classList.remove('btn-loading');
                submitBtn.disabled = false;
            }
        });
    }
    
    // ===== API HELPERS =====
    async apiGet(url) {
        try {
            const response = await fetch(url);
            return await response.json();
        } catch (error) {
            this.notify('API Error', 'Failed to fetch data', 'error');
            throw error;
        }
    }
    
    async apiPost(url, data) {
        try {
            const response = await fetch(url, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(data)
            });
            return await response.json();
        } catch (error) {
            this.notify('API Error', 'Failed to send data', 'error');
            throw error;
        }
    }
    
    // ===== PERFORMANCE MONITORING =====
    initPerformanceMonitoring() {
        // Monitor page load time
        window.addEventListener('load', () => {
            const loadTime = performance.now();
            console.log(`✨ Page loaded in ${loadTime.toFixed(2)}ms`);
            
            if (loadTime > 3000) {
                console.warn('⚠️ Slow page load detected');
            }
        });
        
        // Monitor memory usage (if available)
        if ('memory' in performance) {
            setInterval(() => {
                const memory = performance.memory;
                if (memory.usedJSHeapSize > memory.jsHeapSizeLimit * 0.9) {
                    console.warn('⚠️ High memory usage detected');
                }
            }, 60000); // Check every minute
        }
    }
    
    // ===== ACCESSIBILITY =====
    initAccessibility() {
        // Focus management
        this.setupFocusTraps();
        
        // Screen reader announcements
        this.setupScreenReaderAnnouncements();
        
        // Keyboard navigation
        this.setupKeyboardNavigation();
    }
    
    setupFocusTraps() {
        // Trap focus in modals
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Tab') {
                const activeModal = document.querySelector('.modal-overlay.active');
                if (activeModal) {
                    this.trapFocus(e, activeModal);
                }
            }
        });
    }
    
    trapFocus(e, container) {
        const focusableElements = container.querySelectorAll(
            'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
        );
        
        const firstElement = focusableElements[0];
        const lastElement = focusableElements[focusableElements.length - 1];
        
        if (e.shiftKey) {
            if (document.activeElement === firstElement) {
                lastElement.focus();
                e.preventDefault();
            }
        } else {
            if (document.activeElement === lastElement) {
                firstElement.focus();
                e.preventDefault();
            }
        }
    }
    
    setupScreenReaderAnnouncements() {
        // Create announcement region
        const announcer = document.createElement('div');
        announcer.setAttribute('aria-live', 'polite');
        announcer.setAttribute('aria-atomic', 'true');
        announcer.className = 'sr-only';
        announcer.style.cssText = `
            position: absolute !important;
            width: 1px !important;
            height: 1px !important;
            padding: 0 !important;
            margin: -1px !important;
            overflow: hidden !important;
            clip: rect(0,0,0,0) !important;
            white-space: nowrap !important;
            border: 0 !important;
        `;
        document.body.appendChild(announcer);
        
        this.announcer = announcer;
    }
    
    announce(message) {
        if (this.announcer) {
            this.announcer.textContent = message;
        }
    }
    
    setupKeyboardNavigation() {
        // Skip to main content link
        const skipLink = document.createElement('a');
        skipLink.href = '#main-content';
        skipLink.textContent = 'Skip to main content';
        skipLink.className = 'skip-link';
        skipLink.style.cssText = `
            position: absolute;
            top: -40px;
            left: 6px;
            background: var(--bg-primary);
            color: var(--text-primary);
            padding: 8px;
            text-decoration: none;
            border-radius: 4px;
            z-index: 1000;
            transition: top 0.3s;
        `;
        
        skipLink.addEventListener('focus', () => {
            skipLink.style.top = '6px';
        });
        
        skipLink.addEventListener('blur', () => {
            skipLink.style.top = '-40px';
        });
        
        document.body.insertBefore(skipLink, document.body.firstChild);
    }
}

// Initialize platform when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    window.platform = new ModernPlatform();
});

// Service Worker registration (if available)
if ('serviceWorker' in navigator) {
    window.addEventListener('load', () => {
        navigator.serviceWorker.register('/static/js/sw.js')
            .then(registration => {
                console.log('✅ Service Worker registered');
            })
            .catch(error => {
                console.log('❌ Service Worker registration failed');
            });
    });
}