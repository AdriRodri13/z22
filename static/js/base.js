/**
 * BASE.JS - JavaScript base para el catálogo de equipos
 * ====================================================
 */

// Inicializar cuando el DOM esté listo
document.addEventListener('DOMContentLoaded', function() {

    
    // Inicializar funcionalidades
    initNavbar();
    initScrollEffects();
    initResponsiveHandling();
    initAccessibility();
    
});

/**
 * NAVEGACIÓN RESPONSIVE
 * ====================
 */
function initNavbar() {
    const navbarToggler = document.querySelector('.navbar-toggler');
    const navbarCollapse = document.querySelector('.navbar-collapse');
    const navLinks = document.querySelectorAll('.nav-link');
    
    // Auto-cerrar menú móvil al hacer clic en enlaces
    if (navLinks.length > 0) {
        navLinks.forEach(link => {
            link.addEventListener('click', () => {
                // Solo cerrar en móvil
                if (window.innerWidth < 992 && navbarCollapse.classList.contains('show')) {
                    const bsCollapse = bootstrap.Collapse.getInstance(navbarCollapse);
                    if (bsCollapse) {
                        bsCollapse.hide();
                    }
                }
            });
        });
    }
    
    // Mejorar botón hamburguesa
    if (navbarToggler) {
        navbarToggler.addEventListener('click', function() {
            // Agregar clase para animación
            this.classList.toggle('active');
        });
    }
}

/**
 * EFECTOS DE SCROLL
 * ================
 */
function initScrollEffects() {
    const header = document.querySelector('.main-header');
    let lastScrollTop = 0;
    
    // Throttle para optimizar rendimiento
    let ticking = false;
    
    function updateHeader() {
        const scrollTop = window.pageYOffset || document.documentElement.scrollTop;
        
        // Agregar clase 'scrolled' cuando se hace scroll
        if (scrollTop > 50) {
            header.classList.add('scrolled');
        } else {
            header.classList.remove('scrolled');
        }
        
        // Auto-hide en móvil al hacer scroll hacia abajo
        if (window.innerWidth < 992) {
            if (scrollTop > lastScrollTop && scrollTop > 100) {
                // Scrolling hacia abajo
                header.style.transform = 'translateY(-100%)';
            } else {
                // Scrolling hacia arriba
                header.style.transform = 'translateY(0)';
            }
        } else {
            // En desktop siempre visible
            header.style.transform = 'translateY(0)';
        }
        
        lastScrollTop = scrollTop <= 0 ? 0 : scrollTop;
        ticking = false;
    }
    
    window.addEventListener('scroll', function() {
        if (!ticking) {
            requestAnimationFrame(updateHeader);
            ticking = true;
        }
    });
    
    // Smooth scroll para enlaces ancla
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function(e) {
            const href = this.getAttribute('href');
            if (href !== '#' && href.length > 1) {
                e.preventDefault();
                const target = document.querySelector(href);
                if (target) {
                    const headerHeight = header.offsetHeight;
                    const targetPosition = target.offsetTop - headerHeight - 20;
                    
                    window.scrollTo({
                        top: targetPosition,
                        behavior: 'smooth'
                    });
                }
            }
        });
    });
}

/**
 * MANEJO RESPONSIVE
 * ================
 */
function initResponsiveHandling() {
    let resizeTimer;
    
    function handleResize() {
        const isMobile = window.innerWidth < 768;
        const isTablet = window.innerWidth >= 768 && window.innerWidth < 1024;
        const isDesktop = window.innerWidth >= 1024;
        
        // Limpiar clases existentes
        document.body.classList.remove('is-mobile', 'is-tablet', 'is-desktop');
        
        // Agregar clase apropiada
        if (isMobile) {
            document.body.classList.add('is-mobile');
        } else if (isTablet) {
            document.body.classList.add('is-tablet');
        } else {
            document.body.classList.add('is-desktop');
        }
        
        // Cerrar menú móvil si cambió a desktop
        if (isDesktop) {
            const navbarCollapse = document.querySelector('.navbar-collapse');
            if (navbarCollapse && navbarCollapse.classList.contains('show')) {
                const bsCollapse = bootstrap.Collapse.getInstance(navbarCollapse);
                if (bsCollapse) {
                    bsCollapse.hide();
                }
            }
            
            // Resetear transform del header
            const header = document.querySelector('.main-header');
            if (header) {
                header.style.transform = '';
            }
        }
    }
    
    window.addEventListener('resize', function() {
        clearTimeout(resizeTimer);
        resizeTimer = setTimeout(handleResize, 150);
    });
    
    // Ejecutar al cargar
    handleResize();
}

/**
 * ACCESIBILIDAD
 * =============
 */
function initAccessibility() {
    // Manejo de teclado
    document.addEventListener('keydown', function(e) {
        // ESC para cerrar menús
        if (e.key === 'Escape') {
            const navbarCollapse = document.querySelector('.navbar-collapse');
            if (navbarCollapse && navbarCollapse.classList.contains('show')) {
                const bsCollapse = bootstrap.Collapse.getInstance(navbarCollapse);
                if (bsCollapse) {
                    bsCollapse.hide();
                }
            }
        }
        
        // Mejorar visibilidad del focus con teclado
        if (e.key === 'Tab') {
            document.body.classList.add('using-keyboard');
        }
    });
    
    // Quitar clase de teclado al usar mouse
    document.addEventListener('mousedown', function() {
        document.body.classList.remove('using-keyboard');
    });
    
    // Tab trap en menú móvil
    const navbarCollapse = document.querySelector('.navbar-collapse');
    if (navbarCollapse) {
        navbarCollapse.addEventListener('keydown', function(e) {
            if (e.key === 'Tab' && this.classList.contains('show')) {
                const focusableElements = this.querySelectorAll('a, button, [tabindex]:not([tabindex="-1"])');
                const firstElement = focusableElements[0];
                const lastElement = focusableElements[focusableElements.length - 1];
                
                if (e.shiftKey) {
                    // Shift + Tab
                    if (document.activeElement === firstElement) {
                        e.preventDefault();
                        lastElement.focus();
                    }
                } else {
                    // Tab normal
                    if (document.activeElement === lastElement) {
                        e.preventDefault();
                        firstElement.focus();
                    }
                }
            }
        });
    }
}

/**
 * UTILIDADES ADICIONALES
 * ======================
 */

// Función para mostrar notificaciones simples
function showNotification(message, type = 'info') {
    // Crear contenedor si no existe
    let container = document.querySelector('.notification-container');
    if (!container) {
        container = document.createElement('div');
        container.className = 'notification-container position-fixed top-0 end-0 p-3';
        container.style.zIndex = '9999';
        document.body.appendChild(container);
    }
    
    // Crear notificación
    const notification = document.createElement('div');
    notification.className = `alert alert-${type} alert-dismissible fade show`;
    notification.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    container.appendChild(notification);
    
    // Auto-remove después de 5 segundos
    setTimeout(() => {
        if (notification.parentNode) {
            const bsAlert = bootstrap.Alert.getInstance(notification);
            if (bsAlert) {
                bsAlert.close();
            }
        }
    }, 5000);
}

// Función para lazy loading de imágenes
function initLazyLoading() {
    if ('IntersectionObserver' in window) {
        const imageObserver = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    const img = entry.target;
                    if (img.dataset.src) {
                        img.src = img.dataset.src;
                        img.classList.remove('lazy-load');
                        img.classList.add('loaded');
                        imageObserver.unobserve(img);
                    }
                }
            });
        }, {
            threshold: 0.1,
            rootMargin: '50px'
        });
        
        // Observar todas las imágenes con data-src
        document.querySelectorAll('img[data-src]').forEach(img => {
            img.classList.add('lazy-load');
            imageObserver.observe(img);
        });
    }
}

// Manejo de errores de imágenes
document.addEventListener('error', function(e) {
    if (e.target.tagName === 'IMG') {
        e.target.style.opacity = '0.5';
        e.target.alt = 'Imagen no disponible';
        
        // Intentar cargar placeholder si existe
        if (e.target.dataset.placeholder) {
            e.target.src = e.target.dataset.placeholder;
        }
    }
}, true);

// Detectar estado de conexión
window.addEventListener('online', function() {
    showNotification('Conexión restaurada', 'success');
});

window.addEventListener('offline', function() {
    showNotification('Sin conexión a internet', 'warning');
});

// CSS adicional para estados específicos
const additionalCSS = `
<style>
.using-keyboard *:focus {
    outline: 2px solid #fff !important;
    outline-offset: 2px !important;
}

.navbar-toggler.active .navbar-toggler-icon {
    transform: rotate(90deg);
    transition: transform 0.3s ease;
}

.scrolled {
    backdrop-filter: blur(10px);
    background: rgba(0, 0, 0, 0.95) !important;
}

.lazy-load {
    opacity: 0;
    transition: opacity 0.3s ease;
}

.loaded {
    opacity: 1;
}

.notification-container .alert {
    margin-bottom: 0.5rem;
    min-width: 300px;
}

@media (prefers-reduced-motion: reduce) {
    * {
        animation-duration: 0.01ms !important;
        animation-iteration-count: 1 !important;
        transition-duration: 0.01ms !important;
    }
}

@media (max-width: 767.98px) {
    .main-header {
        transition: transform 0.3s ease;
    }
}
</style>
`;

// Agregar CSS al head
document.head.insertAdjacentHTML('beforeend', additionalCSS);

// Inicializar lazy loading cuando el DOM esté listo
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initLazyLoading);
} else {
    initLazyLoading();
}