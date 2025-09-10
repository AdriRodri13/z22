/**
 * SUBSECCION.JS - JavaScript simple para la página de subsecciones
 * ===============================================================
 */

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    initializeSearch();
});

/**
 * SEARCH FUNCTIONALITY
 * ===================
 */
function initializeSearch() {
    const searchInput = document.querySelector('.search-input');
    const clearButton = document.querySelector('.clear-search');
    
    if (clearButton) {
        clearButton.addEventListener('click', clearSearch);
    }
}

function clearSearch() {
    const searchInput = document.querySelector('.search-input');
    if (searchInput) {
        searchInput.value = '';
        searchInput.focus();
    }
    
    // Remove search parameter from URL and reload
    const url = new URL(window.location);
    url.searchParams.delete('search');
    window.location.href = url.toString();
}

/**
 * GLOBAL FUNCTIONS (called from templates)
 * =======================================
 */
window.clearSearch = clearSearch;