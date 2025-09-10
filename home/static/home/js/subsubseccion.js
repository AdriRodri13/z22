/**
 * EQUIPO.JS - JavaScript para página de equipaciones
 * ==================================================
 */

document.addEventListener('DOMContentLoaded', function() {
    initEquipacionCards();
    initScrollAnimations();
    initModalFunctionality();
    initMobileOptimizations();
});

/**
 * FUNCIONALIDAD DE CARDS DE EQUIPACIONES
 * ======================================
 */
function initEquipacionCards() {
    const equipacionCards = document.querySelectorAll('.equipacion-card');
    
    equipacionCards.forEach(card => {
        const equipacionId = card.dataset.equipacionId;
        const equipacionImg = card.querySelector('.equipacion-img');
        const btnContactar = card.querySelector('.btn-contactar');
        
        // Click en la card para ver imagen ampliada
        card.addEventListener('click', (e) => {
            // Si se hizo click en el botón, no abrir modal
            if (e.target.closest('.btn-contactar')) {
                return;
            }
            openEquipacionModal(equipacionImg);
        });
        
        // Click en botón contactar
        if (btnContactar) {
            btnContactar.addEventListener('click', (e) => {
                e.stopPropagation();
                contactarInstagram(equipacionImg);
            });
        }
        
        // Accesibilidad - Enter y Space para abrir modal
        card.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' || e.key === ' ') {
                e.preventDefault();
                openEquipacionModal(equipacionImg);
            }
        });
        
        // Hacer la card focusable
        card.setAttribute('tabindex', '0');
        card.setAttribute('role', 'button');
        card.setAttribute('aria-label', 'Ver equipación en detalle');
        
        // Lazy loading de imagen
        if (equipacionImg.dataset.src) {
            initLazyLoading(equipacionImg);
        }
    });
}

/**
 * MODAL DE EQUIPACIÓN
 * ===================
 */
function initModalFunctionality() {
    const modal = document.getElementById('equipacionModal');
    
    if (modal) {
        // Cerrar modal con Escape
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape') {
                const bootstrapModal = bootstrap.Modal.getInstance(modal);
                if (bootstrapModal) {
                    bootstrapModal.hide();
                }
            }
        });
        
        // Prevenir scroll del body cuando el modal está abierto
        modal.addEventListener('show.bs.modal', () => {
            document.body.style.overflow = 'hidden';
        });
        
        modal.addEventListener('hidden.bs.modal', () => {
            document.body.style.overflow = '';
        });
    }
}

function openEquipacionModal(imgElement) {
    const modal = document.getElementById('equipacionModal');
    const modalImg = document.getElementById('modalEquipacionImg');
    
    if (modal && modalImg && imgElement) {
        // Actualizar imagen del modal
        modalImg.src = imgElement.src;
        modalImg.alt = imgElement.alt;
        
        // Mostrar modal
        const bootstrapModal = new bootstrap.Modal(modal);
        bootstrapModal.show();
        
        // Focus en el modal para accesibilidad
        modal.addEventListener('shown.bs.modal', () => {
            modal.focus();
        });
    }
}

/**
 * FUNCIONALIDAD DE INSTAGRAM
 * ==========================
 */
function contactarInstagram(imgElement = null) {
    // URL de Instagram actualizada para zone22._
    const instagramUrl = 'https://www.instagram.com/zone22._/';
    
    // Abrir Instagram en nueva pestaña
    window.open(instagramUrl, '_blank');
    
    // Cerrar modal si está abierto
    const modal = document.getElementById('prendaModal');
    const bootstrapModal = bootstrap.Modal.getInstance(modal);
    if (bootstrapModal) {
        bootstrapModal.hide();
    }
    
    // Feedback visual
    showFeedback('Redirigiendo a Instagram...', 'success');
}

// Función global para el botón del modal
window.contactarInstagram = contactarInstagram;

/**
 * LAZY LOADING DE IMÁGENES
 * ========================
 */
function initLazyLoading(img) {
    const imageObserver = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const imgElement = entry.target;
                imgElement.classList.add('loading');
                
                const tempImg = new Image();
                tempImg.onload = () => {
                    imgElement.src = tempImg.src;
                    imgElement.classList.remove('loading');
                };
                tempImg.onerror = () => {
                    imgElement.classList.remove('loading');
                    imgElement.style.opacity = '0.5';
                    console.warn('Error loading image:', tempImg.src);
                };
                tempImg.src = imgElement.dataset.src;
                
                imageObserver.unobserve(imgElement);
            }
        });
    }, {
        threshold: 0.1,
        rootMargin: '50px'
    });
    
    imageObserver.observe(img);
}

/**
 * ANIMACIONES DE SCROLL
 * =====================
 */
function initScrollAnimations() {
    // Solo si el usuario no prefiere motion reducido
    if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
        return;
    }
    
    const observer = new IntersectionObserver((entries) => {
        entries.forEach((entry, index) => {
            if (entry.isIntersecting) {
                const delay = entry.target.classList.contains('equipacion-card') ? index * 50 : 0;
                
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
    document.querySelectorAll('.equipacion-card, .equipo-info-header').forEach(el => {
        el.style.opacity = '0';
        el.style.transform = 'translateY(20px)';
        el.style.transition = 'opacity 0.6s ease, transform 0.6s ease';
        observer.observe(el);
    });
}

/**
 * UTILIDADES ADICIONALES
 * ======================
 */

// Función para copiar enlace de imagen
function copiarEnlaceImagen(imgElement) {
    if (navigator.clipboard && imgElement) {
        navigator.clipboard.writeText(imgElement.src).then(() => {
            showFeedback('Enlace copiado al portapapeles', 'success');
        }).catch(() => {
            showFeedback('Error al copiar enlace', 'error');
        });
    }
}

// Función para descargar imagen (si se quiere implementar)
function descargarImagen(imgElement) {
    if (imgElement) {
        const link = document.createElement('a');
        link.href = imgElement.src;
        link.download = `equipacion-${Date.now()}.jpg`;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        showFeedback('Descarga iniciada', 'success');
    }
}

// Feedback visual simple
function showFeedback(message, type = 'info') {
    const toast = document.createElement('div');
    toast.className = `alert alert-${type} position-fixed`;
    toast.style.cssText = `
        top: 20px;
        right: 20px;
        z-index: 9999;
        min-width: 250px;
        opacity: 0;
        transition: opacity 0.3s ease;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
        border-radius: 0.5rem;
        backdrop-filter: blur(10px);
    `;
    toast.textContent = message;
    
    document.body.appendChild(toast);
    
    setTimeout(() => toast.style.opacity = '1', 10);
    
    setTimeout(() => {
        toast.style.opacity = '0';
        setTimeout(() => toast.remove(), 300);
    }, 3000);
}

/**
 * OPTIMIZACIONES MÓVILES
 * ======================
 */
function initMobileOptimizations() {
    if (window.innerWidth <= 768) {
        // Mejorar el scroll en móvil
        document.body.style.webkitOverflowScrolling = 'touch';
        
        // Reducir animaciones en móvil para mejor performance
        const cards = document.querySelectorAll('.equipacion-card');
        cards.forEach(card => {
            card.style.willChange = 'transform';
        });
        
        // Mejorar el tap en móvil
        document.addEventListener('touchstart', function() {}, {passive: true});
        
        // Optimizar imágenes para móvil
        const images = document.querySelectorAll('.equipacion-img');
        images.forEach(img => {
            img.addEventListener('load', function() {
                this.style.willChange = 'auto';
            });
        });
        
        // Prevenir zoom accidental en inputs
        const meta = document.querySelector('meta[name="viewport"]');
        if (meta) {
            meta.setAttribute('content', 'width=device-width, initial-scale=1, maximum-scale=1, user-scalable=no');
        }
        
        // Optimizar el modal para móvil
        const modal = document.getElementById('equipacionModal');
        if (modal) {
            modal.addEventListener('show.bs.modal', () => {
                // Ajustar altura del modal en móvil
                const modalDialog = modal.querySelector('.modal-dialog');
                modalDialog.style.height = '100vh';
                modalDialog.style.margin = '0';
                modalDialog.style.maxWidth = '100%';
            });
            
            modal.addEventListener('hidden.bs.modal', () => {
                // Restaurar estilos
                const modalDialog = modal.querySelector('.modal-dialog');
                modalDialog.style.height = '';
                modalDialog.style.margin = '';
                modalDialog.style.maxWidth = '';
            });
        }
    }
    
    // Detectar cambios de orientación
    window.addEventListener('orientationchange', () => {
        setTimeout(() => {
            // Recalcular layout después del cambio de orientación
            window.dispatchEvent(new Event('resize'));
        }, 100);
    });
    
    // Optimización para dispositivos con hover limitado
    if (window.matchMedia('(hover: none)').matches) {
        const cards = document.querySelectorAll('.equipacion-card');
        cards.forEach(card => {
            // En dispositivos sin hover, mostrar overlay al hacer tap
            card.addEventListener('touchstart', function(e) {
                const overlay = this.querySelector('.equipacion-overlay');
                if (overlay) {
                    overlay.style.transform = 'translateY(0)';
                }
            }, {passive: true});
            
            card.addEventListener('touchend', function(e) {
                const overlay = this.querySelector('.equipacion-overlay');
                if (overlay) {
                    setTimeout(() => {
                        overlay.style.transform = 'translateY(100%)';
                    }, 2000);
                }
            }, {passive: true});
        });
    }
}

/**
 * GESTIÓN DE ERRORES
 * ==================
 */
window.addEventListener('error', function(e) {
    console.error('Error en equipo.js:', e.error);
    showFeedback('Ha ocurrido un error inesperado', 'error');
});

// Prevenir errores de Bootstrap si no está cargado
window.addEventListener('load', function() {
    if (typeof bootstrap === 'undefined') {
        console.warn('Bootstrap no está cargado. Algunas funcionalidades pueden no funcionar correctamente.');
    }
});

/**
 * CLEANUP Y PERFORMANCE
 * =====================
 */
window.addEventListener('beforeunload', function() {
    // Limpiar observers y event listeners para evitar memory leaks
    const observers = document.querySelectorAll('[data-observer]');
    observers.forEach(el => {
        const observer = el.dataset.observer;
        if (observer && observer.disconnect) {
            observer.disconnect();
        }
    });
});

// Throttle para eventos de scroll/resize
function throttle(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

// Aplicar throttle a eventos costosos
window.addEventListener('scroll', throttle(() => {
    // Lógica de scroll si es necesaria
}, 16)); // ~60fps

window.addEventListener('resize', throttle(() => {
    // Recalcular dimensiones si es necesario
    initMobileOptimizations();
}, 250));

/**
 * ACCESSIBILITY IMPROVEMENTS
 * ==========================
 */
document.addEventListener('keydown', function(e) {
    // Navegación por teclado mejorada
    if (e.key === 'Tab') {
        document.body.classList.add('keyboard-navigation');
    }
});

document.addEventListener('mousedown', function() {
    document.body.classList.remove('keyboard-navigation');
});

// Anunciar cambios importantes para screen readers
function announceToScreenReader(message) {
    const announcement = document.createElement('div');
    announcement.setAttribute('aria-live', 'polite');
    announcement.setAttribute('aria-atomic', 'true');
    announcement.className = 'sr-only';
    announcement.textContent = message;
    
    document.body.appendChild(announcement);
    
    setTimeout(() => {
        document.body.removeChild(announcement);
    }, 1000);
}

