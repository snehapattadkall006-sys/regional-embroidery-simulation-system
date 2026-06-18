/**
 * Regional Embroidery Simulation System — main.js
 * Global utilities: spinner, toasts, password toggle, animations
 */

// ── LOADING SPINNER ──────────────────────────────────────────
window.addEventListener('load', () => {
    const spinner = document.getElementById('loading-spinner');
    if (spinner) {
        setTimeout(() => spinner.classList.add('fade-out'), 300);
        setTimeout(() => spinner.remove(), 700);
    }
});

// ── TOAST NOTIFICATIONS ──────────────────────────────────────
function showToast(message, type = 'info', duration = 3500) {
    let container = document.getElementById('toast-container');
    if (!container) {
        container = document.createElement('div');
        container.id = 'toast-container';
        container.className = 'toast-container';
        document.body.appendChild(container);
    }

    const icons = {
        success: 'fa-check-circle',
        danger:  'fa-exclamation-circle',
        warning: 'fa-exclamation-triangle',
        info:    'fa-info-circle'
    };

    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    toast.innerHTML = `<i class="fas ${icons[type] || icons.info}"></i> ${message}`;
    container.appendChild(toast);

    setTimeout(() => {
        toast.style.opacity = '0';
        toast.style.transform = 'translateY(20px)';
        toast.style.transition = '0.3s ease';
        setTimeout(() => toast.remove(), 300);
    }, duration);
}

// ── PASSWORD TOGGLE ───────────────────────────────────────────
function togglePass(fieldId) {
    const field = document.getElementById(fieldId);
    if (!field) return;
    const btn = field.nextElementSibling;
    if (field.type === 'password') {
        field.type = 'text';
        if (btn) btn.querySelector('i').className = 'fas fa-eye-slash';
    } else {
        field.type = 'password';
        if (btn) btn.querySelector('i').className = 'fas fa-eye';
    }
}

// ── FLASH MESSAGE AUTO-DISMISS ────────────────────────────────
document.querySelectorAll('.flash-alert').forEach(alert => {
    setTimeout(() => {
        alert.style.opacity = '0';
        alert.style.transform = 'translateX(100%)';
        alert.style.transition = '0.4s ease';
        setTimeout(() => alert.remove(), 400);
    }, 5000);
});

// ── INTERSECTION OBSERVER: ANIMATE ON SCROLL ─────────────────
const observerOptions = {
    root: null,
    threshold: 0.1,
    rootMargin: '0px 0px -40px 0px'
};

const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
        if (entry.isIntersecting) {
            entry.target.classList.add('animate-in');
            observer.unobserve(entry.target);
        }
    });
}, observerOptions);

// Observe cards and sections
document.querySelectorAll(
    '.state-card, .feature-card, .objective-item, .design-card, .learn-card, .stat-card, .quick-card'
).forEach((el, i) => {
    el.style.opacity = '0';
    el.style.transform = 'translateY(24px)';
    el.style.transition = `opacity 0.5s ease ${i * 0.06}s, transform 0.5s ease ${i * 0.06}s`;
    observer.observe(el);
});

document.querySelectorAll('.animate-in').forEach = function(){};

// Add animate-in styles
const style = document.createElement('style');
style.textContent = '.animate-in { opacity: 1 !important; transform: translateY(0) !important; }';
document.head.appendChild(style);

// ── FORM VALIDATION HELPERS ───────────────────────────────────
function validateEmail(email) {
    return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
}

// Inline validation for auth forms
document.querySelectorAll('.auth-form input[type="email"]').forEach(input => {
    input.addEventListener('blur', function() {
        const errEl = this.parentElement.querySelector('.field-error');
        if (errEl) {
            errEl.textContent = this.value && !validateEmail(this.value) ? 'Invalid email format' : '';
        }
    });
});

// ── SMOOTH SCROLL ─────────────────────────────────────────────
document.querySelectorAll('a[href^="#"]').forEach(a => {
    a.addEventListener('click', function(e) {
        const target = document.querySelector(this.getAttribute('href'));
        if (target) {
            e.preventDefault();
            target.scrollIntoView({ behavior: 'smooth', block: 'start' });
        }
    });
});

// ── ACTIVE NAV LINK ───────────────────────────────────────────
const currentPath = window.location.pathname;
document.querySelectorAll('.sidebar-link').forEach(link => {
    if (link.getAttribute('href') === currentPath) link.classList.add('active');
});

// ── IMAGE LAZY LOADING FALLBACK ───────────────────────────────
document.querySelectorAll('img[onerror]').forEach(img => {
    img.addEventListener('error', function() {
        if (!this.dataset.errored) {
            this.dataset.errored = 'true';
        }
    });
});

// ── DESIGN SEARCH LIVE FILTER ─────────────────────────────────
const liveSearch = document.getElementById('liveSearch');
if (liveSearch) {
    liveSearch.addEventListener('input', function() {
        const query = this.value.toLowerCase();
        document.querySelectorAll('.design-card').forEach(card => {
            const name  = (card.dataset.name  || '').toLowerCase();
            const state = (card.dataset.state || '').toLowerCase();
            card.style.display = (name.includes(query) || state.includes(query)) ? '' : 'none';
        });
    });
}

// ── GENERAL UTILITY: Debounce ─────────────────────────────────
function debounce(fn, delay = 300) {
    let timer;
    return (...args) => {
        clearTimeout(timer);
        timer = setTimeout(() => fn.apply(this, args), delay);
    };
}

// ── CONFIRM DELETE / REMOVE ───────────────────────────────────
document.querySelectorAll('[data-confirm]').forEach(btn => {
    btn.addEventListener('click', function(e) {
        if (!confirm(this.dataset.confirm)) e.preventDefault();
    });
});

console.log('✦ RESS — Regional Embroidery Simulation System loaded');
