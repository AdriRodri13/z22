/**
 * HOME.JS - JavaScript para el catálogo de prendas
 * =================================================
 */

document.addEventListener('DOMContentLoaded', function() {
    
    initSeccionCards();
    initScrollAnimations();
    
});

/**
 * FUNCIONALIDAD DE CARDS DE SECCIONES
 * ===================================
 */
function initSeccionCards() {
    const seccionCards = document.querySelectorAll('.seccion-card');
    
    seccionCards.forEach(card => {
        const btnExplorar = card.querySelector('.btn-explorar');
        const seccionId = card.dataset.seccionId;
        
        // Click en la card completa
        card.addEventListener('click', () => {
            handleExplorarSeccion(seccionId, card);
        });
        
        // Click en el botón (evitar doble evento)
        if (btnExplorar) {
            btnExplorar.addEventListener('click', (e) => {
                e.stopPropagation();
                handleExplorarSeccion(seccionId, card);
            });
        }
        
        // Accesibilidad - Enter y Space
        card.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' || e.key === ' ') {
                e.preventDefault();
                handleExplorarSeccion(seccionId, card);
            }
        });
        
        // Hacer la card focusable
        card.setAttribute('tabindex', '0');
        card.setAttribute('role', 'button');
        card.setAttribute('aria-label', `Explorar sección ${card.querySelector('.seccion-nombre')?.textContent || ''}`);
        
        // Efecto hover mejorado con JavaScript
        card.addEventListener('mouseenter', () => {
            const icono = card.querySelector('.seccion-icono');
            if (icono) {
                icono.style.transform = 'scale(1.1) rotate(5deg)';
            }
        });
        
        card.addEventListener('mouseleave', () => {
            const icono = card.querySelector('.seccion-icono');
            if (icono) {
                icono.style.transform = '';
            }
        });
    });
}

/**
 * MANEJO DE CLICK EN SECCIÓN
 * ==========================
 */
function handleExplorarSeccion(seccionId, card) {
    
    // Efecto visual inmediato con gradiente
    card.style.transform = 'scale(0.96)';
    card.style.filter = 'brightness(1.1)';
    
    // Animación del icono
    const icono = card.querySelector('.seccion-icono');
    if (icono) {
        icono.style.transform = 'scale(1.2) rotate(10deg)';
    }
    
    // Simular carga con feedback visual
    setTimeout(() => {
        card.style.transform = '';
        card.style.filter = '';
        if (icono) {
            icono.style.transform = '';
        }
        
        // Ir a la página de la sección para ver sus subsecciones
        window.location.href = `/seccion/${seccionId}/`;
    }, 200);
}

/**
 * ANIMACIONES DE SCROLL SIMPLES
 * =============================
 */
function initScrollAnimations() {
    // Solo si el usuario no prefiere motion reducido
    if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
        return;
    }
    
    const observer = new IntersectionObserver((entries) => {
        entries.forEach((entry, index) => {
            if (entry.isIntersecting) {
                // Delay escalonado para las cards
                const delay = entry.target.classList.contains('seccion-card') ? index * 100 : 0;
                
                setTimeout(() => {
                    entry.target.style.opacity = '1';
                    entry.target.style.transform = 'translateY(0)';
                }, delay);
                
                observer.unobserve(entry.target);
            }
        });
    }, {
        threshold: 0.1,
        rootMargin: '0px 0px -20px 0px'
    });
    
    // Aplicar estado inicial y observar
    document.querySelectorAll('.seccion-card, .section-title').forEach(el => {
        el.style.opacity = '0';
        el.style.transform = 'translateY(20px)';
        el.style.transition = 'opacity 0.6s ease, transform 0.6s ease';
        observer.observe(el);
    });
}

/**
 * FEEDBACK SIMPLE
 * ===============
 */
function showFeedback(message, type = 'info') {
    // Crear toast simple
    const toast = document.createElement('div');
    toast.className = `alert alert-${type} position-fixed`;
    toast.style.cssText = `
        top: 20px;
        right: 20px;
        z-index: 9999;
        min-width: 250px;
        opacity: 0;
        transition: opacity 0.3s ease;
    `;
    toast.textContent = message;
    
    document.body.appendChild(toast);
    
    // Mostrar
    setTimeout(() => toast.style.opacity = '1', 10);
    
    // Ocultar y eliminar
    setTimeout(() => {
        toast.style.opacity = '0';
        setTimeout(() => toast.remove(), 300);
    }, 3000);
}

/**
 * LAZY LOADING SIMPLE
 * ===================
 */
function initLazyLoading() {
    if ('IntersectionObserver' in window) {
        const imageObserver = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    const img = entry.target;

                    
                    if (img.dataset.src) {
                        img.classList.add('loading');
                        
                        const tempImg = new Image();
                        tempImg.onload = () => {
                            img.src = tempImg.src;
                            img.classList.remove('loading');
                        };
                        tempImg.onerror = () => {
                            img.classList.remove('loading');
                        };
                        tempImg.src = img.dataset.src;
                    }
                    
                    imageObserver.unobserve(img);
                }
            });
        });
        
        document.querySelectorAll('img[data-src]').forEach(img => {
            imageObserver.observe(img);
        });
    }
}

// Inicializar lazy loading al cargar
document.addEventListener('DOMContentLoaded', initLazyLoading);