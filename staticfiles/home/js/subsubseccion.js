/**
 * SUBSUBSECCION.JS - JavaScript para página de subsubsección
 * ===========================================================
 */

// Declarar función agregarACesta globalmente ANTES del DOMContentLoaded
function agregarACesta() {
    const btn = document.getElementById('btnAgregarCesta');
    if (!btn) return;

    // Obtener datos de la prenda desde el botón
    const prendaData = {
        id: btn.dataset.prendaId,
        nombre: btn.dataset.prendaNombre,
        precio: btn.dataset.prendaPrecio,
        imagen: btn.dataset.prendaImg
    };

    // Validar datos
    if (!prendaData.id || !prendaData.nombre) {
        showFeedback('Error: Datos de prenda incompletos', 'error', 4000);
        return;
    }

    // Mostrar estado de carga
    showLoadingState(btn);

    // Simular pequeño delay para UX
    setTimeout(() => {
        try {
            // Usar la función global si está disponible
            if (typeof window.addToCestaGlobal === 'function') {
                const wasAdded = window.addToCestaGlobal(prendaData);

                if (wasAdded) {
                    showFeedback('¡Agregado a la cesta!', 'success', 2500);
                    hideLoadingState(btn);
                    showSuccessState(btn);
                } else {
                    showFeedback('Prenda ya está en la cesta', 'info', 3000);
                    hideLoadingState(btn);
                }
            } else {
                // Fallback: usar sistema local
                const existingIndex = cestaItems.findIndex(item => item.id === prendaData.id);

                if (existingIndex !== -1) {
                    cestaItems[existingIndex].timestamp = new Date().toISOString();
                    showFeedback('Prenda ya está en la cesta', 'info', 3000);
                    hideLoadingState(btn);
                } else {
                    cestaItems.push({
                        ...prendaData,
                        timestamp: new Date().toISOString()
                    });
                    showFeedback('¡Agregado a la cesta!', 'success', 2500);
                    hideLoadingState(btn);
                    showSuccessState(btn);
                }

                saveCestaToStorage();
                updateCestaCounter();
            }

            // Anunciar a screen readers
            announceToScreenReader(`${prendaData.nombre} agregado a la cesta`);

        } catch (error) {
            console.error('Error al agregar a la cesta:', error);
            showFeedback('Error al agregar a la cesta', 'error', 4000);
            hideLoadingState(btn);
        }
    }, 800);
}

// Hacer disponible globalmente inmediatamente
window.agregarACesta = agregarACesta;

document.addEventListener('DOMContentLoaded', function() {
    initPrendaCards();
    initScrollAnimations();
    initModalFunctionality();
    initMobileOptimizations();
    initCestaFunctionality();
});

/**
 * FUNCIONALIDAD DE CARDS DE PRENDAS
 * ==================================
 */
function initPrendaCards() {
    const prendaCards = document.querySelectorAll('.prenda-card');
    
    prendaCards.forEach(card => {
        const prendaId = card.dataset.prendaId;
        const prendaImg = card.querySelector('.prenda-img');

        // Click en la card para ver imagen ampliada
        card.addEventListener('click', (e) => {
            openPrendaModal(prendaImg);
        });
        
        // Accesibilidad - Enter y Space para abrir modal
        card.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' || e.key === ' ') {
                e.preventDefault();
                openPrendaModal(prendaImg);
            }
        });
        
        // Hacer la card focusable
        card.setAttribute('tabindex', '0');
        card.setAttribute('role', 'button');
        card.setAttribute('aria-label', 'Ver prenda en detalle');
        
        // Lazy loading de imagen
        if (prendaImg.dataset.src) {
            initLazyLoading(prendaImg);
        }
    });
}

/**
 * MODAL DE PRENDA
 * ===============
 */
function initModalFunctionality() {
    const modal = document.getElementById('prendaModal');
    
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

function openPrendaModal(imgElement) {
    const modal = document.getElementById('prendaModal');
    const modalImg = document.getElementById('modalPrendaImg');
    const modalPrecio = document.getElementById('modalPrendaPrecio');
    const btnAgregarCesta = document.getElementById('btnAgregarCesta');

    if (modal && modalImg && imgElement) {
        // Obtener datos de la prenda desde el card
        const prendaCard = imgElement.closest('.prenda-card');
        const prendaId = prendaCard?.dataset.prendaId;
        const precioElement = prendaCard?.querySelector('.precio-valor');

        // Actualizar imagen del modal
        modalImg.src = imgElement.src;
        modalImg.alt = imgElement.alt;

        // Actualizar solo el precio
        if (modalPrecio && precioElement) {
            modalPrecio.textContent = precioElement.textContent;
        } else if (modalPrecio) {
            modalPrecio.textContent = 'Precio no disponible';
        }

        // Actualizar botón de cesta con ID de prenda
        if (btnAgregarCesta && prendaId) {
            btnAgregarCesta.dataset.prendaId = prendaId;
            btnAgregarCesta.dataset.prendaImg = imgElement.src;
            btnAgregarCesta.dataset.prendaNombre = imgElement.alt || 'Prenda';
            btnAgregarCesta.dataset.prendaPrecio = precioElement?.textContent || '0€';
        }

        // Mostrar modal - verificar si Bootstrap está disponible
        if (typeof bootstrap !== 'undefined') {
            const bootstrapModal = new bootstrap.Modal(modal);
            bootstrapModal.show();
        } else {
            // Fallback si Bootstrap no está disponible
            modal.style.display = 'block';
            modal.classList.add('show');
            document.body.classList.add('modal-open');
        }

        // Focus en el modal para accesibilidad
        modal.addEventListener('shown.bs.modal', () => {
            modal.focus();
        }, { once: true });
    }
}

/**
 * FUNCIONALIDAD DE INSTAGRAM
 * ==========================
 */
function contactarInstagram(imgElement = null) {
    // URL directa al DM de Instagram para zone22._
    const instagramUrl = 'https://ig.me/m/zone22._';

    // Abrir DM de Instagram en nueva pestaña
    window.open(instagramUrl, '_blank');
    
    // Cerrar modal si está abierto
    const modal = document.getElementById('prendaModal');
    const bootstrapModal = bootstrap.Modal.getInstance(modal);
    if (bootstrapModal) {
        bootstrapModal.hide();
    }
    
    // Feedback visual
    showFeedback('Redirigiendo a Instagram...', 'success', 2000);
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
                const delay = entry.target.classList.contains('prenda-card') ? index * 50 : 0;
                
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
    document.querySelectorAll('.prenda-card, .subsubseccion-info-header').forEach(el => {
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
            showFeedback('Enlace copiado al portapapeles', 'success', 2500);
        }).catch(() => {
            showFeedback('Error al copiar enlace', 'error', 3500);
        });
    }
}

// Función para descargar imagen (si se quiere implementar)
function descargarImagen(imgElement) {
    if (imgElement) {
        const link = document.createElement('a');
        link.href = imgElement.src;
        link.download = `prenda-${Date.now()}.jpg`;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        showFeedback('Descarga iniciada', 'success', 2500);
    }
}

// Feedback visual simple
function showFeedback(message, type = 'info', timeout = 3000) {
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
    }, timeout);
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
        const cards = document.querySelectorAll('.prenda-card');
        cards.forEach(card => {
            card.style.willChange = 'transform';
        });
        
        // Mejorar el tap en móvil
        document.addEventListener('touchstart', function() {}, {passive: true});
        
        // Optimizar imágenes para móvil
        const images = document.querySelectorAll('.prenda-img');
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
        const modal = document.getElementById('prendaModal');
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
        const cards = document.querySelectorAll('.prenda-card');
        cards.forEach(card => {
            // En dispositivos móviles, abrir modal al hacer tap
            card.addEventListener('touchend', function(e) {
                e.preventDefault();
                const prendaImg = this.querySelector('.prenda-img');
                if (prendaImg) {
                    openPrendaModal(prendaImg);
                }
            }, {passive: false});
        });
    }
}

/**
 * GESTIÓN DE ERRORES
 * ==================
 */
window.addEventListener('error', function(e) {
    console.error('Error en subsubseccion.js:', e.error);
    showFeedback('Ha ocurrido un error inesperado', 'error', 5000);
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

/**
 * FUNCIONALIDAD DE CESTA
 * ======================
 */

// Variable global para manejar la cesta
let cestaItems = [];

function initCestaFunctionality() {
    // Cargar cesta desde localStorage
    loadCestaFromStorage();

    // Actualizar contador visual si existe
    updateCestaCounter();

    // Escuchar eventos de storage para sincronizar entre pestañas
    window.addEventListener('storage', function(e) {
        if (e.key === 'cesta_prendas') {
            loadCestaFromStorage();
            updateCestaCounter();
        }
    });
}

function showLoadingState(btn) {
    const originalText = btn.innerHTML;
    btn.dataset.originalText = originalText;
    btn.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Agregando...';
    btn.classList.add('loading');
    btn.disabled = true;
}

function hideLoadingState(btn) {
    if (btn.dataset.originalText) {
        btn.innerHTML = btn.dataset.originalText;
    }
    btn.classList.remove('loading');
    btn.disabled = false;
}

function showSuccessState(btn) {
    // Usar el texto original guardado por showLoadingState, o el actual como fallback
    const originalText = btn.dataset.originalText || btn.innerHTML;
    btn.innerHTML = '<i class="fas fa-check me-2"></i>¡Agregado!';
    btn.classList.add('success');
    btn.disabled = true;

    setTimeout(() => {
        btn.innerHTML = originalText;
        btn.classList.remove('success');
        btn.disabled = false;
        // Limpiar el dataset
        delete btn.dataset.originalText;
    }, 2000);
}

function loadCestaFromStorage() {
    try {
        const storedCesta = localStorage.getItem('cesta_prendas');
        cestaItems = storedCesta ? JSON.parse(storedCesta) : [];

        // Limpiar items muy antiguos (más de 7 días)
        const sevenDaysAgo = new Date();
        sevenDaysAgo.setDate(sevenDaysAgo.getDate() - 7);

        cestaItems = cestaItems.filter(item => {
            return new Date(item.timestamp) > sevenDaysAgo;
        });

        saveCestaToStorage();
    } catch (error) {
        console.error('Error al cargar cesta desde localStorage:', error);
        cestaItems = [];
    }
}

function saveCestaToStorage() {
    try {
        localStorage.setItem('cesta_prendas', JSON.stringify(cestaItems));
    } catch (error) {
        console.error('Error al guardar cesta en localStorage:', error);
        showFeedback('Error al guardar en la cesta', 'error', 4000);
    }
}

function updateCestaCounter() {
    // Usar la función global si está disponible
    if (typeof window.updateCestaGlobalCounter === 'function') {
        window.updateCestaGlobalCounter();
        return;
    }

    // Fallback: usar sistema local
    const counters = document.querySelectorAll('.cesta-counter');
    const count = cestaItems.length;

    counters.forEach(counter => {
        counter.textContent = count;
        counter.style.display = count > 0 ? 'block' : 'none';

        // Animar si hay cambios
        if (count > 0) {
            counter.classList.add('animate');
            setTimeout(() => counter.classList.remove('animate'), 300);
        }
    });

    // Actualizar badge si existe
    const badges = document.querySelectorAll('.cesta-badge');
    badges.forEach(badge => {
        badge.textContent = count;
        badge.style.display = count > 0 ? 'inline-block' : 'none';
    });
}

function getCestaItems() {
    return [...cestaItems]; // Retornar copia para evitar mutaciones
}

function getCestaCount() {
    return cestaItems.length;
}

function removeFromCesta(prendaId) {
    const index = cestaItems.findIndex(item => item.id === prendaId);
    if (index !== -1) {
        const removedItem = cestaItems.splice(index, 1)[0];
        saveCestaToStorage();
        updateCestaCounter();
        showFeedback(`${removedItem.nombre} eliminado de la cesta`, 'info', 3000);
        return true;
    }
    return false;
}

function clearCesta() {
    cestaItems = [];
    saveCestaToStorage();
    updateCestaCounter();
    showFeedback('Cesta vaciada', 'info', 2500);
}

function getCestaTotal() {
    return cestaItems.reduce((total, item) => {
        const precio = parseFloat(item.precio.replace('€', '').replace(',', '.')) || 0;
        return total + precio;
    }, 0);
}

// Hacer funciones globales para uso en otros archivos
window.getCestaItems = getCestaItems;
window.getCestaCount = getCestaCount;
window.removeFromCesta = removeFromCesta;
window.clearCesta = clearCesta;
window.getCestaTotal = getCestaTotal;

