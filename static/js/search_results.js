// This script handles the loading overlay and other client-side interactions

// Show loading overlay immediately when script loads
window.addEventListener('load', function() {
    showLoadingOverlay(true);
});

document.addEventListener('DOMContentLoaded', function() {
    // Hide the old loading indicator
    const loadingElement = document.getElementById('loading');
    if (loadingElement) {
        loadingElement.style.display = 'none';
    }
    
    // Hide the loading overlay after a short delay to ensure content is visible
    setTimeout(function() {
        showLoadingOverlay(false);
    }, 800); // Short delay to make the loading animation visible
    
    console.log('Search results page loaded');
});

// Function to show/hide the loading overlay
function showLoadingOverlay(show) {
    const overlay = document.getElementById('loading-overlay');
    if (!overlay) return;
    
    if (show) {
        overlay.style.display = 'flex';
    } else {
        // Add a fade-out effect
        overlay.style.opacity = '0';
        setTimeout(function() {
            overlay.style.display = 'none';
            overlay.style.opacity = '1';
        }, 300);
    }
}