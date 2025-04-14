// Enhanced script for search results page

document.addEventListener('DOMContentLoaded', function() {
    // Hide the loading indicator since the page is already loaded with data
    const loadingElement = document.getElementById('loading');
    if (loadingElement) {
        loadingElement.style.display = 'none';
    }
    
    // Add hover effects to restaurant cards
    const restaurantCards = document.querySelectorAll('.restaurant-card');
    restaurantCards.forEach(card => {
        card.addEventListener('mouseenter', function() {
            this.style.transform = 'translateY(-5px)';
            this.style.boxShadow = '0 6px 12px rgba(0, 0, 0, 0.15)';
        });
        
        card.addEventListener('mouseleave', function() {
            this.style.transform = 'translateY(0)';
            this.style.boxShadow = '0 4px 8px rgba(0, 0, 0, 0.1)';
        });
    });
    
    // Make entire card clickable to view details
    restaurantCards.forEach(card => {
        const detailsLink = card.querySelector('.view-details-btn');
        if (detailsLink) {
            const href = detailsLink.getAttribute('href');
            
            card.addEventListener('click', function(e) {
                // Don't trigger if clicking on the actual button
                if (!e.target.classList.contains('view-details-btn')) {
                    window.location.href = href;
                }
            });
        }
    });
    
    // Highlight current page in pagination
    const paginationLinks = document.querySelectorAll('.page-link');
    const urlParams = new URLSearchParams(window.location.search);
    const currentPage = urlParams.get('page') || '1';
    
    paginationLinks.forEach(link => {
        const linkParams = new URLSearchParams(new URL(link.href).search);
        const linkPage = linkParams.get('page');
        
        if (linkPage === currentPage) {
            link.classList.add('current-page');
            link.classList.remove('page-link');
        }
    });
    
    console.log('Enhanced search results page loaded');
});