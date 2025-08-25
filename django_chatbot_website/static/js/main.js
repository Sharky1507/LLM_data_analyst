// Main JavaScript functionality
document.addEventListener('DOMContentLoaded', function() {
    // Dark mode functionality
    initDarkMode();
    
    // Auto-hide messages after 5 seconds
    const messages = document.querySelectorAll('.message');
    messages.forEach(function(message) {
        setTimeout(function() {
            message.style.opacity = '0';
            setTimeout(function() {
                message.remove();
            }, 300);
        }, 5000);
    });

    // Add smooth scrolling to anchor links
    const anchorLinks = document.querySelectorAll('a[href^="#"]');
    anchorLinks.forEach(function(link) {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });

    // Form validation enhancements
    const forms = document.querySelectorAll('form');
    forms.forEach(function(form) {
        form.addEventListener('submit', function(e) {
            const submitButton = form.querySelector('button[type="submit"]');
            if (submitButton) {
                submitButton.disabled = true;
                submitButton.textContent = 'Loading...';
                
                // Re-enable button after 3 seconds in case of issues
                setTimeout(function() {
                    submitButton.disabled = false;
                    submitButton.textContent = submitButton.getAttribute('data-original-text') || 'Submit';
                }, 3000);
            }
        });
    });

    // Store original button text
    const submitButtons = document.querySelectorAll('button[type="submit"]');
    submitButtons.forEach(function(button) {
        button.setAttribute('data-original-text', button.textContent);
    });

    // Chatbot iframe management
    const chatbotFrame = document.getElementById('chatbot-frame');
    if (chatbotFrame) {
        // Handle iframe loading states
        let loadTimeout;
        
        function showConnectionStatus(status, message) {
            const statusIndicator = document.querySelector('.status-indicator');
            const statusText = document.querySelector('.status-text');
            
            if (statusIndicator && statusText) {
                statusIndicator.className = 'status-indicator ' + status;
                statusText.textContent = message;
            }
        }
        
        // Set loading timeout
        loadTimeout = setTimeout(function() {
            showConnectionStatus('error', 'Connection timeout - Please check if chatbot server is running on port 8002');
        }, 15000);
        
        chatbotFrame.addEventListener('load', function() {
            clearTimeout(loadTimeout);
            showConnectionStatus('connected', 'Connected');
        });
        
        chatbotFrame.addEventListener('error', function() {
            clearTimeout(loadTimeout);
            showConnectionStatus('error', 'Failed to load chatbot - Please ensure server is running');
        });
        
        // Periodic health check for the chatbot
        function checkChatbotHealth() {
            fetch('http://localhost:8002', { 
                method: 'HEAD',
                mode: 'no-cors'
            }).catch(function() {
                showConnectionStatus('error', 'Chatbot server appears to be offline');
            });
        }
        
        // Check health every 30 seconds
        setInterval(checkChatbotHealth, 30000);
    }

    // Add loading states to navigation links
    const navLinks = document.querySelectorAll('.nav-link');
    navLinks.forEach(function(link) {
        link.addEventListener('click', function() {
            const linkText = link.textContent;
            link.style.opacity = '0.7';
            link.textContent = 'Loading...';
            
            // Reset after 2 seconds in case navigation fails
            setTimeout(function() {
                link.style.opacity = '1';
                link.textContent = linkText;
            }, 2000);
        });
    });

    // Enhanced responsive navigation for mobile
    function checkMobileView() {
        const navLinks = document.querySelector('.nav-links');
        const navContainer = document.querySelector('.nav-container');
        
        if (window.innerWidth <= 768) {
            navContainer.classList.add('mobile-nav');
        } else {
            navContainer.classList.remove('mobile-nav');
        }
    }
    
    window.addEventListener('resize', checkMobileView);
    checkMobileView();
});

// Utility functions
function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `message message-${type}`;
    notification.textContent = message;
    notification.style.position = 'fixed';
    notification.style.top = '20px';
    notification.style.right = '20px';
    notification.style.zIndex = '9999';
    notification.style.minWidth = '300px';
    
    document.body.appendChild(notification);
    
    setTimeout(function() {
        notification.style.opacity = '0';
        setTimeout(function() {
            notification.remove();
        }, 300);
    }, 4000);
}

// Export for use in other scripts
window.ChatbotUtils = {
    showNotification: showNotification
};

// Dark Mode Functionality
function initDarkMode() {
    // Check for saved theme preference or default to 'light'
    const savedTheme = localStorage.getItem('theme') || 
                      (window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light');
    
    // Apply the saved theme
    setTheme(savedTheme);
    
    // Add event listener to theme toggle button
    const themeToggle = document.getElementById('theme-toggle');
    if (themeToggle) {
        themeToggle.addEventListener('click', toggleTheme);
        
        // Update button icon based on current theme
        updateThemeToggleIcon(savedTheme);
    }
    
    // Listen for system theme changes
    window.matchMedia('(prefers-color-scheme: dark)').addListener(function(e) {
        if (!localStorage.getItem('theme')) {
            setTheme(e.matches ? 'dark' : 'light');
        }
    });
}

function setTheme(theme) {
    document.documentElement.setAttribute('data-theme', theme);
    localStorage.setItem('theme', theme);
    updateThemeToggleIcon(theme);
    
    // Emit custom event for other components to listen to
    window.dispatchEvent(new CustomEvent('themeChanged', { detail: { theme } }));
}

function toggleTheme() {
    const currentTheme = document.documentElement.getAttribute('data-theme') || 'light';
    const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
    setTheme(newTheme);
    
    // Add a nice animation effect
    document.body.style.transition = 'background-color 0.3s ease, color 0.3s ease';
    setTimeout(() => {
        document.body.style.transition = '';
    }, 300);
}

function updateThemeToggleIcon(theme) {
    const themeIcon = document.querySelector('.theme-icon');
    if (themeIcon) {
        themeIcon.textContent = theme === 'dark' ? '☀️' : '🌙';
        themeIcon.setAttribute('title', `Switch to ${theme === 'dark' ? 'light' : 'dark'} mode`);
    }
}

// Theme utilities for other scripts
window.ThemeUtils = {
    getCurrentTheme: function() {
        return document.documentElement.getAttribute('data-theme') || 'light';
    },
    setTheme: setTheme,
    toggleTheme: toggleTheme,
    onThemeChange: function(callback) {
        window.addEventListener('themeChanged', function(e) {
            callback(e.detail.theme);
        });
    }
};
