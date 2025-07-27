/**
 * HOME.JS - JavaScript simple para la página de inicio
 * ====================================================
 */

document.addEventListener('DOMContentLoaded', function() {
    
    initLigaCards();
    initScrollAnimations();
    
});

/**
 * FUNCIONALIDAD SIMPLE DE CARDS
 * =============================
 */
function initLigaCards() {
    const ligaCards = document.querySelectorAll('.liga-card');
    
    ligaCards.forEach(card => {
        const btnExplorar = card.querySelector('.btn-explorar');
        const ligaId = card.dataset.ligaId;
        
        // Click en la card completa
        card.addEventListener('click', () => {
            handleExplorarLiga(ligaId, card);
        });
        
        // Click en el botón (evitar doble evento)
        if (btnExplorar) {
            btnExplorar.addEventListener('click', (e) => {
                e.stopPropagation();
                handleExplorarLiga(ligaId, card);
            });
        }
        
        // Accesibilidad - Enter y Space
        card.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' || e.key === ' ') {
                e.preventDefault();
                handleExplorarLiga(ligaId, card);
            }
        });
        
        // Hacer la card focusable
        card.setAttribute('tabindex', '0');
        card.setAttribute('role', 'button');
        card.setAttribute('aria-label', `Explorar liga ${card.querySelector('.liga-name')?.textContent || ''}`);
    });
}

/**
 * MANEJO DE CLICK EN LIGA
 * =======================
 */
function handleExplorarLiga(ligaId, card) {
    
    // Efecto visual inmediato
    card.style.transform = 'scale(0.98)';
    
    // Simular carga
    setTimeout(() => {
        card.style.transform = '';
        
        // Ir a la página de la liga
        window.location.href = `/liga/${ligaId}/`;
    }, 150);
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
                const delay = entry.target.classList.contains('liga-card') ? index * 100 : 0;
                
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
    document.querySelectorAll('.liga-card, .section-title').forEach(el => {
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