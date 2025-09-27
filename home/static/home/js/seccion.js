/**
 * SECCION.JS - JavaScript para filtrado automático de subsecciones
 * ================================================================
 */

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    initializeSearch();
});

/**
 * SEARCH FUNCTIONALITY - FILTRADO AUTOMÁTICO
 * ==========================================
 */
function initializeSearch() {
    const searchInput = document.getElementById('searchInput');
    const clearButton = document.querySelector('.clear-search');
    const cards = document.querySelectorAll('.subseccion-card');

    if (searchInput) {
        searchInput.addEventListener('input', function() {
            const query = this.value.toLowerCase().trim();
            filterCards(query, cards, clearButton);
        });
    }

    if (clearButton) {
        clearButton.addEventListener('click', function() {
            clearSearch(searchInput, cards, clearButton);
        });
    }
}

function filterCards(query, cards, clearButton) {
    cards.forEach(card => {
        const title = card.querySelector('.card-title').textContent.toLowerCase();
        const description = card.querySelector('.card-description');
        const descText = description ? description.textContent.toLowerCase() : '';

        const matches = title.includes(query) || descText.includes(query);

        if (matches) {
            card.style.display = 'block';
            card.style.animation = 'fadeIn 0.3s ease-in-out';
        } else {
            card.style.display = 'none';
        }
    });

    // Mostrar/ocultar botón clear
    if (query) {
        clearButton.style.display = 'block';
    } else {
        clearButton.style.display = 'none';
    }
}

function clearSearch(searchInput, cards, clearButton) {
    searchInput.value = '';
    clearButton.style.display = 'none';

    // Mostrar todas las tarjetas
    cards.forEach(card => {
        card.style.display = 'block';
        card.style.animation = 'fadeIn 0.3s ease-in-out';
    });

    searchInput.focus();
}

/**
 * GLOBAL FUNCTIONS (called from templates)
 * =======================================
 */
window.clearSearch = function() {
    const searchInput = document.getElementById('searchInput');
    const cards = document.querySelectorAll('.subseccion-card');
    const clearButton = document.querySelector('.clear-search');

    clearSearch(searchInput, cards, clearButton);
};