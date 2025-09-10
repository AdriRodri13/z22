/**
 * LIGA.JS - JavaScript simplificado para página de liga
 * ====================================================
 */

document.addEventListener('DOMContentLoaded', function() {
    initEquipoCards();
    initSearchFunctionality();
    initScrollAnimations();
});

/**
 * FUNCIONALIDAD DE CARDS DE EQUIPOS
 * =================================
 */
function initEquipoCards() {
    const equipoCards = document.querySelectorAll('.equipo-card');
    
    equipoCards.forEach(card => {
        const equipoId = card.dataset.equipoId;
        const equipoNombre = card.querySelector('.equipo-nombre').textContent;
        
        // Click en la card
        card.addEventListener('click', () => {
            handleEquipoClick(equipoId, equipoNombre, card);
        });
        
        // Accesibilidad - Enter y Space
        card.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' || e.key === ' ') {
                e.preventDefault();
                handleEquipoClick(equipoId, equipoNombre, card);
            }
        });
        
        // Hacer la card focusable
        card.setAttribute('tabindex', '0');
        card.setAttribute('role', 'button');
        card.setAttribute('aria-label', `Seleccionar equipo ${equipoNombre}`);
    });
}

/**
 * MANEJO DE CLICK EN EQUIPO
 * =========================
 */
function handleEquipoClick(equipoId, equipoNombre, card) {
    // Efecto visual inmediato
    card.style.transform = 'scale(0.95)';
    card.style.opacity = '0.8';
    
    // Navegar al equipo
    setTimeout(() => {
        window.location.href = `/equipo/${equipoId}/`;
    }, 200);
}

/**
 * FUNCIONALIDAD DE BÚSQUEDA INSTANTÁNEA
 * =====================================
 */
function initSearchFunctionality() {
    const searchInput = document.querySelector('.search-input');
    const searchForm = document.querySelector('.search-form');
    
    if (searchInput && searchForm) {
        // Prevenir submit del formulario
        searchForm.addEventListener('submit', function(e) {
            e.preventDefault();
            return false;
        });
        
        // Búsqueda instantánea con cada tecla
        searchInput.addEventListener('input', function(e) {
            e.preventDefault();
            const query = this.value.trim();
            
            // Filtrar inmediatamente sin delay
            performRealTimeSearch(query);
            updateClearButton(query);
        });
        
        // Prevenir cualquier comportamiento del Enter
        searchInput.addEventListener('keydown', (e) => {
            if (e.key === 'Enter') {
                e.preventDefault();
                e.stopPropagation();
                return false;
            }
        });
        
        // Limpiar búsqueda con Escape
        searchInput.addEventListener('keydown', (e) => {
            if (e.key === 'Escape') {
                e.preventDefault();
                clearSearch();
            }
        });
        
        // También escuchar keyup por si acaso
        searchInput.addEventListener('keyup', function(e) {
            const query = this.value.trim();
            performRealTimeSearch(query);
            updateClearButton(query);
        });
        
        // Focus automático en móvil si no hay equipos
        if (window.innerWidth <= 768 && !document.querySelector('.equipo-card')) {
            setTimeout(() => searchInput.focus(), 100);
        }
    }
}

/**
 * BÚSQUEDA INSTANTÁNEA
 * ===================
 */
function performRealTimeSearch(query) {
    const equipoCards = document.querySelectorAll('.equipo-card');
    let visibleCount = 0;
    
    equipoCards.forEach((card, index) => {
        const equipoNombre = card.querySelector('.equipo-nombre').textContent.toLowerCase();
        const matches = query === '' || equipoNombre.includes(query.toLowerCase());
        
        if (matches) {
            // Mostrar card inmediatamente
            card.style.display = 'flex';
            card.style.opacity = '1';
            card.style.transform = 'translateY(0)';
            
            visibleCount++;
        } else {
            // Ocultar card inmediatamente
            card.style.opacity = '0';
            card.style.transform = 'translateY(-5px)';
            
            setTimeout(() => {
                if (card.style.opacity === '0') {
                    card.style.display = 'none';
                }
            }, 100);
        }
        
        // Highlight del término buscado
        highlightSearchTerm(card, query);
    });
    
    // Actualizar contador y estado vacío
    updateResultsCounter(query, visibleCount);
    toggleEmptyState(query, visibleCount);
}

/**
 * ACTUALIZAR BOTÓN CLEAR DINÁMICO
 * ===============================
 */
function updateClearButton(query) {
    const searchInputWrapper = document.querySelector('.search-input-wrapper');
    let clearButton = searchInputWrapper.querySelector('.clear-search');
    
    if (query && query.length > 0) {
        if (!clearButton) {
            clearButton = document.createElement('button');
            clearButton.type = 'button';
            clearButton.className = 'clear-search';
            clearButton.innerHTML = '<i class="fas fa-times"></i>';
            clearButton.onclick = clearSearch;
            searchInputWrapper.appendChild(clearButton);
        }
    } else {
        if (clearButton) {
            clearButton.remove();
        }
    }
}

/**
 * HIGHLIGHT DE TÉRMINOS BUSCADOS
 * ==============================
 */
function highlightSearchTerm(card, searchTerm) {
    const nombreElement = card.querySelector('.equipo-nombre');
    
    // Restaurar texto original
    if (nombreElement.dataset.originalText) {
        nombreElement.textContent = nombreElement.dataset.originalText;
    } else {
        nombreElement.dataset.originalText = nombreElement.textContent;
    }
    
    // Aplicar highlight si hay término de búsqueda
    if (searchTerm && searchTerm.length > 0) {
        const originalText = nombreElement.dataset.originalText;
        const regex = new RegExp(`(${escapeRegExp(searchTerm)})`, 'gi');
        const highlightedText = originalText.replace(regex, '<mark>$1</mark>');
        nombreElement.innerHTML = highlightedText;
    }
}

/**
 * ESCAPAR CARACTERES ESPECIALES REGEX
 * ===================================
 */
function escapeRegExp(string) {
    return string.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
}

/**
 * ACTUALIZAR CONTADOR DE RESULTADOS
 * =================================
 */
function updateResultsCounter(query, visibleCount) {
    const statsElement = document.querySelector('.liga-stats');
    let searchResults = statsElement.querySelector('.search-results');
    
    if (query && query.length > 0) {
        const resultsText = ` • ${visibleCount} resultado${visibleCount !== 1 ? 's' : ''}`;
        
        if (searchResults) {
            searchResults.textContent = resultsText;
        } else {
            searchResults = document.createElement('span');
            searchResults.className = 'search-results';
            searchResults.textContent = resultsText;
            statsElement.appendChild(searchResults);
        }
    } else {
        if (searchResults) {
            searchResults.remove();
        }
    }
}

/**
 * MOSTRAR/OCULTAR ESTADO VACÍO
 * ============================
 */
function toggleEmptyState(query, visibleCount) {
    let emptyState = document.querySelector('.dynamic-empty-state');
    const equiposContainer = document.querySelector('.equipos-section .container');
    
    if (query && visibleCount === 0) {
        // Crear estado "sin resultados" si no existe
        if (!emptyState) {
            emptyState = document.createElement('div');
            emptyState.className = 'dynamic-empty-state text-center py-5';
            emptyState.innerHTML = `
                <div class="empty-state">
                    <i class="fas fa-search text-muted mb-3" style="font-size: 3rem; display: block; color: rgba(255, 255, 255, 0.3);"></i>
                    <h4 class="text-white">No se encontraron equipos</h4>
                    <p class="text-muted mb-4">No hay equipos que coincidan con "<span class="search-term"></span>"</p>
                    <button onclick="clearSearch()" class="btn btn-outline-light btn-sm">
                        <i class="fas fa-times me-2"></i>
                        Limpiar búsqueda
                    </button>
                </div>
            `;
            equiposContainer.appendChild(emptyState);
        }
        
        // Actualizar término de búsqueda
        const searchTermSpan = emptyState.querySelector('.search-term');
        if (searchTermSpan) {
            searchTermSpan.textContent = query;
        }
        
        emptyState.style.display = 'block';
    } else {
        // Ocultar estado vacío
        if (emptyState) {
            emptyState.style.display = 'none';
        }
    }
}

/**
 * LIMPIAR BÚSQUEDA
 * ================
 */
function clearSearch() {
    const searchInput = document.querySelector('.search-input');
    
    if (searchInput) {
        searchInput.value = '';
        searchInput.focus();
        
        // Mostrar todos los equipos inmediatamente
        performRealTimeSearch('');
        updateClearButton('');
    }
}

// Función global para el botón de limpiar en el template
window.clearSearch = clearSearch;

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
                const delay = entry.target.classList.contains('equipo-card') ? index * 25 : 0;
                
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
    
    // Aplicar estado inicial y observar solo si no hay búsqueda activa
    const searchInput = document.querySelector('.search-input');
    if (!searchInput.value) {
        document.querySelectorAll('.equipo-card, .liga-info-header').forEach(el => {
            el.style.opacity = '0';
            el.style.transform = 'translateY(15px)';
            el.style.transition = 'opacity 0.4s ease, transform 0.4s ease';
            observer.observe(el);
        });
    }
}

/**
 * FEEDBACK VISUAL
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
        min-width: 280px;
        max-width: 400px;
        opacity: 0;
        transition: opacity 0.3s ease;
        font-size: 0.9rem;
    `;
    toast.textContent = message;
    
    document.body.appendChild(toast);
    
    // Mostrar
    setTimeout(() => toast.style.opacity = '1', 10);
    
    // Ocultar y eliminar
    setTimeout(() => {
        toast.style.opacity = '0';
        setTimeout(() => toast.remove(), 300);
    }, 3500);
}

/**
 * OPTIMIZACIONES MÓVILES
 * ======================
 */
if (window.innerWidth <= 768) {
    // Prevenir zoom en iOS al enfocar input
    const searchInput = document.querySelector('.search-input');
    if (searchInput) {
        searchInput.addEventListener('focus', function() {
            this.style.fontSize = '16px';
        });
        
        searchInput.addEventListener('blur', function() {
            this.style.fontSize = '';
        });
    }
    
    // Mejorar el scroll en móvil
    document.addEventListener('touchstart', function() {}, { passive: true });
}

/**
 * CSS ADICIONAL PARA BÚSQUEDA INSTANTÁNEA
 * =======================================
 */
const searchCSS = `
<style>
.equipo-card {
    transition: opacity 0.15s ease, transform 0.15s ease;
}

.equipo-card:hover {
    transition: all 0.3s ease;
}

mark {
    background-color: #fff3cd;
    color: #856404;
    padding: 0.1em 0.2em;
    border-radius: 0.2em;
    font-weight: 600;
}

.search-input {
    transition: font-size 0.3s ease;
}

.equipo-card:active {
    transform: scale(0.95) !important;
    transition: transform 0.1s ease !important;
}

.clear-search {
    opacity: 0;
    animation: fadeInButton 0.2s ease forwards;
}

@keyframes fadeInButton {
    to { opacity: 1; }
}

@media (prefers-reduced-motion: reduce) {
    .equipo-card,
    .clear-search {
        animation: none !important;
        transition: none !important;
    }
}
</style>
`;

// Agregar CSS al head
document.head.insertAdjacentHTML('beforeend', searchCSS);