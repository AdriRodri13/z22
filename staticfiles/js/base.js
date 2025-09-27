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
    initCestaGlobal();
    
});

/**
 * NAVEGACIÓN RESPONSIVE
 * ====================
 */
function initNavbar() {
    const navbarToggler = document.querySelector('.navbar-toggler');
    const navbarCollapse = document.querySelector('.navbar-collapse');
    const navLinks = document.querySelectorAll('.nav-link');

    // Auto-cerrar menú móvil al hacer clic en enlaces (EXCEPTO dropdowns)
    if (navLinks.length > 0) {
        navLinks.forEach(link => {
            link.addEventListener('click', (e) => {
                // No cerrar si es un dropdown toggle
                if (link.classList.contains('dropdown-toggle')) {
                    e.stopPropagation();
                    return;
                }

                // Solo cerrar en móvil para enlaces normales
                if (window.innerWidth < 992 && navbarCollapse.classList.contains('show')) {
                    const bsCollapse = bootstrap.Collapse.getInstance(navbarCollapse);
                    if (bsCollapse) {
                        bsCollapse.hide();
                    }
                }
            });
        });
    }

    // Manejar específicamente los dropdowns en móvil
    const dropdownToggles = document.querySelectorAll('.navbar .dropdown-toggle');
    dropdownToggles.forEach(toggle => {
        toggle.addEventListener('click', (e) => {
            if (window.innerWidth < 992) {
                // Solo evitar que se cierre el navbar collapse, pero permitir que Bootstrap maneje el dropdown
                e.stopPropagation();

                // Permitir que Bootstrap maneje el dropdown normalmente
                // No preventDefault() para que Bootstrap funcione

                // Pequeño delay para que Bootstrap procese primero
                setTimeout(() => {
                    const dropdownMenu = toggle.nextElementSibling;
                    if (dropdownMenu && dropdownMenu.classList.contains('dropdown-menu')) {
                        // Si Bootstrap no lo abrió, hacerlo manualmente
                        if (!dropdownMenu.classList.contains('show')) {
                            // Usar Bootstrap dropdown si está disponible
                            try {
                                const dropdown = new bootstrap.Dropdown(toggle);
                                dropdown.show();
                            } catch (error) {
                                // Fallback manual si Bootstrap falla
                                dropdownMenu.classList.add('show');
                            }
                        }
                    }
                }, 10);
            }
        });
    });

    // Evitar que clicks en el dropdown menu cierren el navbar
    document.querySelectorAll('.navbar .dropdown-menu').forEach(menu => {
        menu.addEventListener('click', (e) => {
            if (window.innerWidth < 992) {
                e.stopPropagation();
            }
        });
    });

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
function showNotification(message, type = 'info', timeout = 4000) {
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

    // Inicializar Bootstrap Alert
    try {
        new bootstrap.Alert(notification);
    } catch (e) {
        console.warn('Bootstrap Alert no pudo inicializarse:', e);
    }

    // Auto-remove después del timeout especificado con múltiples fallbacks
    const removeNotification = () => {
        if (notification && notification.parentNode) {
            try {
                const bsAlert = bootstrap.Alert.getInstance(notification);
                if (bsAlert) {
                    bsAlert.close();
                } else {
                    // Fallback: remover directamente
                    notification.remove();
                }
            } catch (e) {
                // Fallback final: remover directamente
                notification.remove();
            }
        }
    };

    setTimeout(removeNotification, timeout);
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
    showNotification('Conexión restaurada', 'success', 3000);
});

window.addEventListener('offline', function() {
    showNotification('Sin conexión a internet', 'warning', 4000);
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

/**
 * FUNCIONALIDAD GLOBAL DE CESTA
 * =============================
 */

// Variable global para la cesta
let cestaGlobal = [];

function initCestaGlobal() {
    // Cargar cesta desde localStorage
    loadCestaGlobal();

    // Actualizar contador al cargar
    updateCestaGlobalCounter();

    // Escuchar cambios en localStorage para sincronizar entre pestañas
    window.addEventListener('storage', function(e) {
        if (e.key === 'cesta_prendas') {
            loadCestaGlobal();
            updateCestaGlobalCounter();

            // Si el modal está abierto, actualizarlo
            const modal = document.getElementById('cestaModal');
            if (modal && modal.classList.contains('show')) {
                renderCestaModal();
            }
        }
    });
}

function loadCestaGlobal() {
    try {
        const storedCesta = localStorage.getItem('cesta_prendas');
        cestaGlobal = storedCesta ? JSON.parse(storedCesta) : [];

        // Limpiar items antiguos (más de 7 días)
        const sevenDaysAgo = new Date();
        sevenDaysAgo.setDate(sevenDaysAgo.getDate() - 7);

        cestaGlobal = cestaGlobal.filter(item => {
            return new Date(item.timestamp) > sevenDaysAgo;
        });

        // Guardar cesta limpia
        localStorage.setItem('cesta_prendas', JSON.stringify(cestaGlobal));
    } catch (error) {
        console.error('Error al cargar cesta global:', error);
        cestaGlobal = [];
    }
}

function updateCestaGlobalCounter() {
    const badge = document.querySelector('.cesta-badge');
    const count = cestaGlobal.length;

    if (badge) {
        badge.textContent = count;
        badge.style.display = count > 0 ? 'inline-block' : 'none';

        // Animar cuando hay cambios
        if (count > 0) {
            badge.classList.add('animate');
            setTimeout(() => badge.classList.remove('animate'), 300);
        }
    }
}

function abrirModalCesta() {
    const modal = document.getElementById('cestaModal');
    if (modal) {
        renderCestaModal();

        // Mostrar modal usando Bootstrap
        const bootstrapModal = new bootstrap.Modal(modal);
        bootstrapModal.show();
    }
}

function renderCestaModal() {
    const content = document.getElementById('cestaContent');
    const footer = document.getElementById('cestaFooter');
    const total = document.getElementById('cestaTotal');

    if (!content) return;

    if (cestaGlobal.length === 0) {
        // Cesta vacía
        content.innerHTML = `
            <div class="cesta-empty">
                <i class="fas fa-shopping-cart text-muted mb-3" style="font-size: 3rem;"></i>
                <h5 class="text-white">Tu cesta está vacía</h5>
                <p class="text-muted">Agrega algunas prendas para comenzar</p>
            </div>
        `;

        if (footer) footer.style.display = 'none';
    } else {
        // Verificar si el usuario está autenticado y obtener descuentos
        const isAuthenticated = document.body.classList.contains('user-authenticated');

        if (isAuthenticated) {
            // Cargar descuentos del usuario y renderizar con descuentos
            obtenerDescuentosUsuario().then(descuentos => {
                renderCestaConDescuentos(descuentos);
            }).catch(() => {
                // Si falla, mostrar sin descuentos
                renderCestaSinDescuentos();
            });
        } else {
            // Usuario no autenticado, mostrar sin descuentos
            renderCestaSinDescuentos();
        }
    }
}

function renderCestaSinDescuentos() {
    const content = document.getElementById('cestaContent');
    const footer = document.getElementById('cestaFooter');
    const total = document.getElementById('cestaTotal');

    // Mostrar items de la cesta sin descuentos
    let itemsHTML = '';
    let totalPrecio = 0;

    cestaGlobal.forEach((item, index) => {
        const precio = parseFloat(item.precio.replace('€', '').replace(',', '.')) || 0;
        totalPrecio += precio;

        itemsHTML += `
            <div class="cesta-item d-flex align-items-center p-3 border-bottom border-secondary">
                <img src="${item.imagen}" alt="${item.nombre}" class="cesta-item-img me-3" style="width: 50px; height: 50px; object-fit: cover; border-radius: 8px;">
                <div class="cesta-item-info flex-grow-1">
                    <div class="text-white fw-medium mb-1">${item.nombre}</div>
                    <div class="text-primary fw-bold">${item.precio}</div>
                </div>
                <button class="btn btn-outline-danger btn-sm" onclick="removeFromCestaGlobal('${item.id}')" title="Eliminar">
                    <i class="fas fa-times"></i>
                </button>
            </div>
        `;
    });

    content.innerHTML = itemsHTML;

    // Actualizar total
    if (total) {
        total.textContent = `${totalPrecio.toFixed(2)}€`;
    }

    // Mostrar footer
    if (footer) footer.style.display = 'block';
}

function renderCestaConDescuentos(descuentos) {
    const content = document.getElementById('cestaContent');
    const footer = document.getElementById('cestaFooter');
    const total = document.getElementById('cestaTotal');

    // Obtener el mejor descuento disponible
    const mejorDescuento = descuentos.length > 0 ? descuentos.reduce((prev, current) =>
        (prev.porcentaje > current.porcentaje) ? prev : current
    ) : null;

    let itemsHTML = '';
    let totalPrecio = 0;
    let totalConDescuento = 0;

    // Mostrar descuento disponible si existe
    if (mejorDescuento) {
        itemsHTML += `
            <div class="alert alert-success border-0 mb-3" style="background: rgba(40, 167, 69, 0.15);">
                <div class="d-flex align-items-center">
                    <i class="fas fa-tag text-success me-2"></i>
                    <div class="flex-grow-1">
                        <strong class="text-success">¡Tienes un ${mejorDescuento.porcentaje}% de descuento!</strong>
                        <div class="small text-light">Código: <code class="bg-dark text-success px-2 py-1 rounded">${mejorDescuento.codigo}</code></div>
                    </div>
                </div>
            </div>
        `;
    }

    cestaGlobal.forEach((item, index) => {
        const precio = parseFloat(item.precio.replace('€', '').replace(',', '.')) || 0;
        totalPrecio += precio;

        let precioConDescuento = precio;
        let descuentoHTML = '';

        if (mejorDescuento) {
            precioConDescuento = precio * (1 - mejorDescuento.porcentaje / 100);
            totalConDescuento += precioConDescuento;

            descuentoHTML = `
                <div class="d-flex align-items-center gap-2">
                    <div class="text-light text-decoration-line-through small" style="opacity: 0.7;">${item.precio}</div>
                    <div class="badge fs-6 fw-bold px-3 py-2" style="font-size: 0.9rem !important; background: linear-gradient(135deg, #ffffff, #f8f9fa) !important; color: #28a745 !important; box-shadow: 0 2px 8px rgba(255, 255, 255, 0.3); border-radius: 12px; border: 2px solid #28a745;">${precioConDescuento.toFixed(2)}€</div>
                </div>
            `;
        } else {
            totalConDescuento += precio;
            descuentoHTML = `<div class="text-primary fw-bold">${item.precio}</div>`;
        }

        itemsHTML += `
            <div class="cesta-item d-flex align-items-center p-3 border-bottom border-secondary">
                <img src="${item.imagen}" alt="${item.nombre}" class="cesta-item-img me-3" style="width: 50px; height: 50px; object-fit: cover; border-radius: 8px;">
                <div class="cesta-item-info flex-grow-1">
                    <div class="text-white fw-medium mb-1">${item.nombre}</div>
                    ${descuentoHTML}
                </div>
                <button class="btn btn-outline-danger btn-sm" onclick="removeFromCestaGlobal('${item.id}')" title="Eliminar">
                    <i class="fas fa-times"></i>
                </button>
            </div>
        `;
    });

    content.innerHTML = itemsHTML;

    // Actualizar total con descuento - VERSION SIMPLE
    if (total) {
        if (mejorDescuento && totalPrecio !== totalConDescuento) {
            const ahorro = totalPrecio - totalConDescuento;
            total.style.cssText = '';
            total.innerHTML = `
                <div style="text-align: right;">
                    <div style="color: #ffffff; text-decoration: line-through; font-size: 0.9em; margin-bottom: 5px; opacity: 0.7;">${totalPrecio.toFixed(2)}€</div>
                    <div style="background: white; color: #28a745; font-weight: bold; padding: 8px 16px; border-radius: 8px; border: 2px solid #28a745; font-size: 1.1em; margin-bottom: 5px;">${totalConDescuento.toFixed(2)}€</div>
                    <div style="color: #00d4aa; font-weight: bold; font-size: 0.9em;">¡Ahorras ${ahorro.toFixed(2)}€!</div>
                </div>
            `;
        } else {
            total.style.cssText = 'color: white; font-size: 1.25rem; font-weight: bold;';
            total.textContent = `${totalPrecio.toFixed(2)}€`;
        }
    }

    // Mostrar footer
    if (footer) footer.style.display = 'block';
}

async function obtenerDescuentosUsuario() {
    try {
        const response = await fetch('/carrito/descuentos/', {
            method: 'GET',
            headers: {
                'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]')?.value || ''
            }
        });

        const data = await response.json();

        if (data.success) {
            return data.descuentos;
        } else {
            throw new Error(data.error || 'Error al obtener descuentos');
        }
    } catch (error) {
        console.error('Error obteniendo descuentos:', error);
        throw error;
    }
}

function removeFromCestaGlobal(prendaId) {
    const index = cestaGlobal.findIndex(item => item.id === prendaId);
    if (index !== -1) {
        const removedItem = cestaGlobal.splice(index, 1)[0];

        // Guardar en localStorage
        localStorage.setItem('cesta_prendas', JSON.stringify(cestaGlobal));

        // Actualizar UI
        updateCestaGlobalCounter();
        renderCestaModal();

        // Mostrar feedback
        showNotification(`${removedItem.nombre} eliminado de la cesta`, 'info', 3000);
    }
}

function clearCestaGlobal() {
    if (cestaGlobal.length === 0) {
        showNotification('La cesta ya está vacía', 'info', 3000);
        return;
    }

    // Vaciar cesta directamente
    cestaGlobal = [];
    localStorage.setItem('cesta_prendas', JSON.stringify(cestaGlobal));

    // Actualizar UI
    updateCestaGlobalCounter();
    renderCestaModal();

    // Mostrar feedback
    showNotification('Cesta vaciada', 'success', 3000);
}

function consultarDisponibilidad() {
    if (cestaGlobal.length === 0) {
        showNotification('Tu cesta está vacía', 'warning', 3000);
        return;
    }

    // Verificar si el usuario está autenticado
    const userDropdown = document.getElementById('userDropdown');
    if (userDropdown) {
        // Usuario autenticado - enviar automáticamente
        enviarConsultaAutomatica();
        return;
    }

    // Usuario no autenticado - mostrar modal
    // Cerrar modal de cesta y abrir modal de consulta
    const cestaModal = bootstrap.Modal.getInstance(document.getElementById('cestaModal'));
    if (cestaModal) {
        cestaModal.hide();
    }

    // Abrir modal de consulta después de un pequeño delay
    setTimeout(() => {
        const consultaModal = new bootstrap.Modal(document.getElementById('consultaModal'));
        consultaModal.show();
    }, 300);
}

function enviarConsultaAutomatica() {
    // Prevenir ejecuciones múltiples
    if (window.enviandoConsulta) {
        console.log('Ya se está enviando una consulta, ignorando nueva solicitud');
        return;
    }
    window.enviandoConsulta = true;

    // Cerrar modal de cesta
    const cestaModal = bootstrap.Modal.getInstance(document.getElementById('cestaModal'));
    if (cestaModal) {
        cestaModal.hide();
    }

    // Mostrar notificación de procesamiento
    showNotification('Enviando consulta de disponibilidad...', 'info', 2000);

    // Preparar datos - el backend obtendrá automáticamente el nombre e Instagram del usuario autenticado
    const consultaData = {
        productos: cestaGlobal.map(item => ({
            id: item.id,
            nombre: item.nombre,
            precio: item.precio
        })),
        usuario_autenticado: true
    };

    // Enviar consulta
    fetch('/consultar-disponibilidad/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]')?.value || ''
        },
        body: JSON.stringify(consultaData)
    })
    .then(response => {
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        return response.json();
    })
    .then(data => {
        if (data.success) {
            showNotification('✅ Consulta enviada correctamente. Te contactaremos pronto por Instagram.', 'success', 5000);
            // Limpiar cesta después del envío exitoso
            cestaGlobal = [];
            updateCestaBadge();
            localStorage.removeItem('cestaGlobal');
        } else {
            showNotification(`❌ Error: ${data.error}`, 'danger', 5000);
        }
    })
    .catch(error => {
        console.error('Error en enviarConsultaAutomatica:', error);
        showNotification('❌ Error de conexión. Inténtalo de nuevo.', 'danger', 5000);
    })
    .finally(() => {
        // Siempre limpiar el flag al final
        window.enviandoConsulta = false;
    });
}

function enviarConsulta() {
    const form = document.getElementById('consultaForm');
    const nombre = document.getElementById('nombreCliente').value.trim();
    const instagram = document.getElementById('instagramCliente').value.trim();

    // Validar campos
    if (!nombre || !instagram) {
        showNotification('Por favor completa todos los campos', 'warning', 4000);
        return;
    }

    // Validar Instagram (sin @)
    const instagramClean = instagram.replace('@', '');
    if (instagramClean.length < 3) {
        showNotification('El usuario de Instagram debe tener al menos 3 caracteres', 'warning', 4000);
        return;
    }

    // Preparar datos
    const consultaData = {
        nombre: nombre,
        instagram: instagramClean,
        productos: cestaGlobal.map(item => ({
            id: item.id,
            nombre: item.nombre,
            precio: item.precio
        }))
    };

    // Deshabilitar botón y mostrar loading
    const btnEnviar = document.querySelector('#consultaModal .btn-cesta');
    const originalText = btnEnviar.innerHTML;
    btnEnviar.disabled = true;
    btnEnviar.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Enviando...';

    // Enviar petición
    fetch('/consultar-disponibilidad/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
        },
        body: JSON.stringify(consultaData)
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            // Cerrar modal de consulta
            const consultaModal = bootstrap.Modal.getInstance(document.getElementById('consultaModal'));
            consultaModal.hide();

            // Limpiar cesta
            clearCestaGlobal();

            // Limpiar formulario
            form.reset();

            // Mostrar mensaje de éxito
            showNotification(data.message, 'success', 5000);
        } else {
            showNotification(data.error || 'Error al enviar la consulta', 'error', 5000);
        }
    })
    .catch(error => {
        console.error('Error:', error);
        showNotification('Error de conexión. Inténtalo de nuevo.', 'error', 5000);
    })
    .finally(() => {
        // Restaurar botón
        btnEnviar.disabled = false;
        btnEnviar.innerHTML = originalText;
    });
}

// Hacer funciones globales
window.abrirModalCesta = abrirModalCesta;
window.removeFromCestaGlobal = removeFromCestaGlobal;
window.clearCesta = clearCestaGlobal;
window.consultarDisponibilidad = consultarDisponibilidad;
window.enviarConsulta = enviarConsulta;

// Funciones para usar desde otras páginas
window.getCestaGlobalItems = function() {
    return [...cestaGlobal];
};

window.getCestaGlobalCount = function() {
    return cestaGlobal.length;
};

window.addToCestaGlobal = function(prendaData) {
    // Verificar si ya existe
    const existingIndex = cestaGlobal.findIndex(item => item.id === prendaData.id);

    if (existingIndex === -1) {
        // Agregar nuevo item
        cestaGlobal.push({
            ...prendaData,
            timestamp: new Date().toISOString()
        });

        // Guardar en localStorage
        localStorage.setItem('cesta_prendas', JSON.stringify(cestaGlobal));

        // Actualizar contador
        updateCestaGlobalCounter();

        return true; // Item agregado
    }

    return false; // Item ya existe
};