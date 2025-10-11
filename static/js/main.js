// ====================================
// NAVBAR - Menu Mobile Toggle
// ====================================

document.addEventListener('DOMContentLoaded', function() {
    const hamburger = document.querySelector('.hamburger');
    const navMenu = document.querySelector('.nav-menu');
    const navLinks = document.querySelectorAll('.nav-link');
    const navbar = document.querySelector('.navbar');

    // Toggle menu mobile
    if (hamburger) {
        hamburger.addEventListener('click', function() {
            hamburger.classList.toggle('active');
            navMenu.classList.toggle('active');
        });
    }

    // Cerrar menu al hacer click en un link
    navLinks.forEach(link => {
        link.addEventListener('click', function() {
            hamburger.classList.remove('active');
            navMenu.classList.remove('active');
        });
    });

    // ====================================
    // NAVBAR - Scroll Effect
    // ====================================

    window.addEventListener('scroll', function() {
        if (window.scrollY > 50) {
            navbar.classList.add('scrolled');
        } else {
            navbar.classList.remove('scrolled');
        }
    });

    // ====================================
    // ACTIVE LINK - Highlight on Scroll
    // ====================================

    const sections = document.querySelectorAll('section[id]');
    
    function highlightNavLink() {
        const scrollY = window.pageYOffset;

        sections.forEach(section => {
            const sectionHeight = section.offsetHeight;
            const sectionTop = section.offsetTop - 100;
            const sectionId = section.getAttribute('id');
            const navLink = document.querySelector(`.nav-link[href="#${sectionId}"]`);

            if (navLink) {
                if (scrollY > sectionTop && scrollY <= sectionTop + sectionHeight) {
                    navLink.classList.add('active');
                } else {
                    navLink.classList.remove('active');
                }
            }
        });
    }

    window.addEventListener('scroll', highlightNavLink);

    // ====================================
    // SMOOTH SCROLL
    // ====================================

    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function(e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            
            if (target) {
                const offsetTop = target.offsetTop - 70;
                window.scrollTo({
                    top: offsetTop,
                    behavior: 'smooth'
                });
            }
        });
    });

    // ====================================
    // ANIMACIÓN DE ENTRADA - Intersection Observer
    // ====================================

    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -100px 0px'
    };

    const observer = new IntersectionObserver(function(entries) {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.style.opacity = '1';
                entry.target.style.transform = 'translateY(0)';
            }
        });
    }, observerOptions);

    // Elementos a animar
    const animatedElements = document.querySelectorAll('.feature-card, .author-card, .info-box, .tech-tag');
    
    animatedElements.forEach(el => {
        el.style.opacity = '0';
        el.style.transform = 'translateY(30px)';
        el.style.transition = 'opacity 0.6s ease, transform 0.6s ease';
        observer.observe(el);
    });

    // ====================================
    // ANIMACIÓN DE NÚMEROS (Counter)
    // ====================================

    function animateCounter(element, target, duration = 2000) {
        const start = 0;
        const increment = target / (duration / 16);
        let current = start;

        const timer = setInterval(() => {
            current += increment;
            if (current >= target) {
                element.textContent = target;
                clearInterval(timer);
            } else {
                element.textContent = Math.floor(current);
            }
        }, 16);
    }

    // Activar contadores cuando sean visibles
    const counterElements = document.querySelectorAll('[data-counter]');
    const counterObserver = new IntersectionObserver(function(entries) {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const target = parseInt(entry.target.getAttribute('data-counter'));
                animateCounter(entry.target, target);
                counterObserver.unobserve(entry.target);
            }
        });
    }, observerOptions);

    counterElements.forEach(el => counterObserver.observe(el));

    // ====================================
    // EFECTO PARALLAX EN HERO
    // ====================================

    const hero = document.querySelector('.hero');
    const circles = document.querySelectorAll('.circle');

    if (hero && circles.length > 0) {
        window.addEventListener('scroll', function() {
            const scrolled = window.pageYOffset;
            const heroHeight = hero.offsetHeight;

            if (scrolled < heroHeight) {
                circles.forEach((circle, index) => {
                    const speed = 0.1 + (index * 0.05);
                    circle.style.transform = `translateY(${scrolled * speed}px)`;
                });
            }
        });
    }

    // ====================================
    // TOOLTIP (opcional)
    // ====================================

    const tooltipElements = document.querySelectorAll('[data-tooltip]');
    
    tooltipElements.forEach(el => {
        el.addEventListener('mouseenter', function() {
            const tooltip = document.createElement('div');
            tooltip.className = 'tooltip';
            tooltip.textContent = this.getAttribute('data-tooltip');
            document.body.appendChild(tooltip);

            const rect = this.getBoundingClientRect();
            tooltip.style.position = 'absolute';
            tooltip.style.top = `${rect.top - tooltip.offsetHeight - 10}px`;
            tooltip.style.left = `${rect.left + (rect.width - tooltip.offsetWidth) / 2}px`;
            
            this._tooltip = tooltip;
        });

        el.addEventListener('mouseleave', function() {
            if (this._tooltip) {
                this._tooltip.remove();
                this._tooltip = null;
            }
        });
    });

    // ====================================
    // PRELOADER (opcional)
    // ====================================

    window.addEventListener('load', function() {
        const preloader = document.querySelector('.preloader');
        if (preloader) {
            preloader.style.opacity = '0';
            setTimeout(() => {
                preloader.style.display = 'none';
            }, 300);
        }
    });

    // ====================================
    // FORMULARIOS - Validación (para futuras páginas)
    // ====================================

    const forms = document.querySelectorAll('form[data-validate]');
    
    forms.forEach(form => {
        form.addEventListener('submit', function(e) {
            e.preventDefault();
            
            const inputs = form.querySelectorAll('input[required], textarea[required], select[required]');
            let isValid = true;

            inputs.forEach(input => {
                if (!input.value.trim()) {
                    isValid = false;
                    input.classList.add('error');
                } else {
                    input.classList.remove('error');
                }
            });

            if (isValid) {
                // Aquí iría el código para enviar el formulario
                console.log('Formulario válido, enviando...');
                form.submit();
            }
        });
    });

    // ====================================
    // DARK MODE TOGGLE (opcional para futuro)
    // ====================================

    const darkModeToggle = document.querySelector('#dark-mode-toggle');
    
    if (darkModeToggle) {
        // Verificar preferencia guardada
        const darkMode = localStorage.getItem('darkMode');
        if (darkMode === 'enabled') {
            document.body.classList.add('dark-mode');
        }

        darkModeToggle.addEventListener('click', function() {
            document.body.classList.toggle('dark-mode');
            
            if (document.body.classList.contains('dark-mode')) {
                localStorage.setItem('darkMode', 'enabled');
            } else {
                localStorage.setItem('darkMode', null);
            }
        });
    }

    // ====================================
    // CONSOLE MESSAGE
    // ====================================

    console.log('%c¡Bienvenido al proyecto!', 'color: #2563eb; font-size: 20px; font-weight: bold;');
    console.log('%cDesarrollado con 💙 por el equipo', 'color: #7c3aed; font-size: 14px;');
});

// ====================================
// UTILIDADES GLOBALES
// ====================================

// Función para mostrar notificaciones
function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.textContent = message;
    
    notification.style.cssText = `
        position: fixed;
        top: 90px;
        right: 20px;
        padding: 15px 25px;
        background: white;
        border-radius: 8px;
        box-shadow: 0 10px 25px rgba(0, 0, 0, 0.2);
        z-index: 10000;
        animation: slideInRight 0.3s ease;
    `;

    document.body.appendChild(notification);

    setTimeout(() => {
        notification.style.animation = 'slideOutRight 0.3s ease';
        setTimeout(() => notification.remove(), 300);
    }, 3000);
}

// Función para copiar al portapapeles
function copyToClipboard(text) {
    navigator.clipboard.writeText(text).then(() => {
        showNotification('Copiado al portapapeles', 'success');
    }).catch(err => {
        console.error('Error al copiar:', err);
        showNotification('Error al copiar', 'error');
    });
}