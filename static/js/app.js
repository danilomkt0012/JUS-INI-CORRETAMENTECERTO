// JusBrasil Clone - JavaScript functionality
document.addEventListener('DOMContentLoaded', function() {
    
    // Initialize tooltips and interactive elements
    initializeTooltips();
    initializeFormValidation();
    initializeSearchFunctionality();
    initializeResponsiveNav();
    
    // Add loading states to buttons
    addLoadingStates();
    
    // Initialize copy to clipboard functionality
    initializeCopyButtons();
    
    console.log('JusBrasil Clone initialized successfully');
});

/**
 * Initialize tooltips for help text
 */
function initializeTooltips() {
    const tooltipElements = document.querySelectorAll('[data-tooltip]');
    
    tooltipElements.forEach(element => {
        element.addEventListener('mouseenter', function() {
            showTooltip(this, this.getAttribute('data-tooltip'));
        });
        
        element.addEventListener('mouseleave', function() {
            hideTooltip();
        });
    });
}

/**
 * Show tooltip
 */
function showTooltip(element, text) {
    const tooltip = document.createElement('div');
    tooltip.id = 'tooltip';
    tooltip.className = 'absolute z-50 px-2 py-1 text-xs text-white bg-gray-900 rounded shadow-lg';
    tooltip.textContent = text;
    
    document.body.appendChild(tooltip);
    
    const rect = element.getBoundingClientRect();
    tooltip.style.left = rect.left + 'px';
    tooltip.style.top = (rect.top - tooltip.offsetHeight - 5) + 'px';
}

/**
 * Hide tooltip
 */
function hideTooltip() {
    const tooltip = document.getElementById('tooltip');
    if (tooltip) {
        tooltip.remove();
    }
}

/**
 * Initialize form validation
 */
function initializeFormValidation() {
    const forms = document.querySelectorAll('form');
    
    forms.forEach(form => {
        form.addEventListener('submit', function(e) {
            if (!validateForm(this)) {
                e.preventDefault();
                return false;
            }
            
            // Add loading state to submit button
            const submitButton = this.querySelector('button[type="submit"]');
            if (submitButton) {
                addLoadingState(submitButton);
            }
        });
    });
}

/**
 * Validate form inputs
 */
function validateForm(form) {
    let isValid = true;
    const requiredFields = form.querySelectorAll('[required]');
    
    requiredFields.forEach(field => {
        if (!field.value.trim()) {
            showFieldError(field, 'Este campo é obrigatório');
            isValid = false;
        } else {
            clearFieldError(field);
            
            // Specific validations
            if (field.type === 'email' && !isValidEmail(field.value)) {
                showFieldError(field, 'Email inválido');
                isValid = false;
            }
            
            if (field.name === 'cpf' && !isValidCPF(field.value)) {
                showFieldError(field, 'CPF inválido');
                isValid = false;
            }
        }
    });
    
    return isValid;
}

/**
 * Show field error
 */
function showFieldError(field, message) {
    clearFieldError(field);
    
    field.classList.add('border-red-500');
    
    const errorDiv = document.createElement('div');
    errorDiv.className = 'field-error text-red-500 text-xs mt-1';
    errorDiv.textContent = message;
    
    field.parentNode.appendChild(errorDiv);
}

/**
 * Clear field error
 */
function clearFieldError(field) {
    field.classList.remove('border-red-500');
    
    const existingError = field.parentNode.querySelector('.field-error');
    if (existingError) {
        existingError.remove();
    }
}

/**
 * Validate email format
 */
function isValidEmail(email) {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
}

/**
 * Validate CPF format (Brazilian tax ID)
 */
function isValidCPF(cpf) {
    // Remove non-numeric characters
    cpf = cpf.replace(/\D/g, '');
    
    // Check if has 11 digits
    if (cpf.length !== 11) return false;
    
    // Check if all digits are the same
    if (/^(\d)\1{10}$/.test(cpf)) return false;
    
    // Validate CPF algorithm
    let sum = 0;
    for (let i = 0; i < 9; i++) {
        sum += parseInt(cpf.charAt(i)) * (10 - i);
    }
    
    let remainder = 11 - (sum % 11);
    if (remainder === 10 || remainder === 11) remainder = 0;
    if (remainder !== parseInt(cpf.charAt(9))) return false;
    
    sum = 0;
    for (let i = 0; i < 10; i++) {
        sum += parseInt(cpf.charAt(i)) * (11 - i);
    }
    
    remainder = 11 - (sum % 11);
    if (remainder === 10 || remainder === 11) remainder = 0;
    if (remainder !== parseInt(cpf.charAt(10))) return false;
    
    return true;
}

/**
 * Initialize search functionality
 */
function initializeSearchFunctionality() {
    const searchInputs = document.querySelectorAll('input[name="search_term"]');
    
    searchInputs.forEach(input => {
        // Add real-time search suggestions (placeholder for future implementation)
        input.addEventListener('input', function() {
            const value = this.value.trim();
            
            if (value.length > 2) {
                // Future: implement search suggestions
                console.log('Search term:', value);
            }
        });
        
        // Format CPF input
        input.addEventListener('input', function() {
            if (this.value.replace(/\D/g, '').length === 11) {
                this.value = formatCPF(this.value);
            }
        });
    });
}

/**
 * Format CPF with masks
 */
function formatCPF(cpf) {
    cpf = cpf.replace(/\D/g, '');
    cpf = cpf.replace(/(\d{3})(\d)/, '$1.$2');
    cpf = cpf.replace(/(\d{3})(\d)/, '$1.$2');
    cpf = cpf.replace(/(\d{3})(\d{1,2})$/, '$1-$2');
    return cpf;
}

/**
 * Initialize responsive navigation
 */
function initializeResponsiveNav() {
    const navToggle = document.querySelector('[data-nav-toggle]');
    const navMenu = document.querySelector('[data-nav-menu]');
    
    if (navToggle && navMenu) {
        navToggle.addEventListener('click', function() {
            navMenu.classList.toggle('hidden');
        });
        
        // Close menu when clicking outside
        document.addEventListener('click', function(e) {
            if (!navToggle.contains(e.target) && !navMenu.contains(e.target)) {
                navMenu.classList.add('hidden');
            }
        });
    }
}

/**
 * Add loading states to buttons
 */
function addLoadingStates() {
    const buttons = document.querySelectorAll('button[type="submit"], .btn-loading');
    
    buttons.forEach(button => {
        button.addEventListener('click', function() {
            if (this.form && !this.form.checkValidity()) return;
            addLoadingState(this);
        });
    });
}

/**
 * Add loading state to specific button
 */
function addLoadingState(button) {
    const originalText = button.innerHTML;
    button.innerHTML = '<i class="fas fa-spinner fa-spin mr-2"></i>Processando...';
    button.disabled = true;
    
    // Remove loading state after 3 seconds (fallback)
    setTimeout(() => {
        button.innerHTML = originalText;
        button.disabled = false;
    }, 3000);
}

/**
 * Initialize copy to clipboard functionality
 */
function initializeCopyButtons() {
    const copyButtons = document.querySelectorAll('[data-copy]');
    
    copyButtons.forEach(button => {
        button.addEventListener('click', function() {
            const textToCopy = this.getAttribute('data-copy');
            
            navigator.clipboard.writeText(textToCopy).then(() => {
                showNotification('Copiado para a área de transferência!', 'success');
            }).catch(() => {
                showNotification('Erro ao copiar texto', 'error');
            });
        });
    });
}

/**
 * Show notification message
 */
function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `fixed top-4 right-4 z-50 px-4 py-2 rounded-md text-white text-sm transition-all duration-300 transform translate-x-full`;
    
    switch (type) {
        case 'success':
            notification.classList.add('bg-green-500');
            break;
        case 'error':
            notification.classList.add('bg-red-500');
            break;
        case 'warning':
            notification.classList.add('bg-yellow-500');
            break;
        default:
            notification.classList.add('bg-blue-500');
    }
    
    notification.textContent = message;
    document.body.appendChild(notification);
    
    // Animate in
    setTimeout(() => {
        notification.classList.remove('translate-x-full');
    }, 100);
    
    // Animate out and remove
    setTimeout(() => {
        notification.classList.add('translate-x-full');
        setTimeout(() => {
            if (notification.parentNode) {
                notification.parentNode.removeChild(notification);
            }
        }, 300);
    }, 3000);
}

/**
 * Initialize smooth scrolling for anchor links
 */
function initializeSmoothScroll() {
    const links = document.querySelectorAll('a[href^="#"]');
    
    links.forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            
            const targetId = this.getAttribute('href').substring(1);
            const targetElement = document.getElementById(targetId);
            
            if (targetElement) {
                targetElement.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });
}

/**
 * Utility function to format Brazilian phone numbers
 */
function formatPhone(phone) {
    phone = phone.replace(/\D/g, '');
    
    if (phone.length === 11) {
        return phone.replace(/(\d{2})(\d{5})(\d{4})/, '($1) $2-$3');
    } else if (phone.length === 10) {
        return phone.replace(/(\d{2})(\d{4})(\d{4})/, '($1) $2-$3');
    }
    
    return phone;
}

/**
 * Utility function to format process numbers
 */
function formatProcessNumber(processNumber) {
    processNumber = processNumber.replace(/\D/g, '');
    
    if (processNumber.length === 20) {
        return processNumber.replace(/(\d{7})(\d{2})(\d{4})(\d{1})(\d{2})(\d{4})/, '$1-$2.$3.$4.$5.$6');
    }
    
    return processNumber;
}

/**
 * Initialize accessibility features
 */
function initializeAccessibility() {
    // Add skip links
    const skipLink = document.createElement('a');
    skipLink.href = '#main-content';
    skipLink.textContent = 'Pular para o conteúdo principal';
    skipLink.className = 'sr-only focus:not-sr-only focus:absolute focus:top-4 focus:left-4 bg-emerald-600 text-white px-4 py-2 rounded';
    document.body.insertBefore(skipLink, document.body.firstChild);
    
    // Add ARIA labels to interactive elements
    const buttons = document.querySelectorAll('button:not([aria-label])');
    buttons.forEach(button => {
        if (!button.getAttribute('aria-label') && button.textContent.trim()) {
            button.setAttribute('aria-label', button.textContent.trim());
        }
    });
}

// Initialize accessibility on load
document.addEventListener('DOMContentLoaded', initializeAccessibility);
