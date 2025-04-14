document.addEventListener('DOMContentLoaded', function() {
    const loginTab = document.getElementById('login-tab');
    const registerTab = document.getElementById('register-tab');
    const loginForm = document.getElementById('login-form');
    const registerForm = document.getElementById('register-form');
    const registerPassword = document.getElementById('register-password');
    const registerConfirmPassword = document.getElementById('register-confirm-password');
    const forgotPasswordLink = document.getElementById('forgot-password');

    // Switch between login and register forms
    loginTab.addEventListener('click', function() {
        loginTab.classList.add('active');
        registerTab.classList.remove('active');
        loginForm.classList.add('active-form');
        registerForm.classList.remove('active-form');
    });

    registerTab.addEventListener('click', function() {
        registerTab.classList.add('active');
        loginTab.classList.remove('active');
        registerForm.classList.add('active-form');
        loginForm.classList.remove('active-form');
    });

    // Form validation
    registerForm.addEventListener('submit', function(event) {
        // Check if passwords match
        if (registerPassword.value !== registerConfirmPassword.value) {
            event.preventDefault();
            alert('Passwords do not match!');
        }
    });

    // Handle forgot password link
    if (forgotPasswordLink) {
        forgotPasswordLink.addEventListener('click', function(event) {
            event.preventDefault();
            console.log("Forgot password link clicked");
            window.location.href = '/forgot-password';
        });
    } else {
        console.error("Forgot password link not found in the DOM");
    }

    // Check URL parameters to determine which form to show
    const urlParams = new URLSearchParams(window.location.search);
    if (urlParams.get('form') === 'register') {
        registerTab.click();
    }

    // Password strength indicator could be added here
    registerPassword.addEventListener('input', function() {
        // Simple password strength check
        const password = registerPassword.value;
        let strength = 0;
        
        if (password.length >= 8) strength += 1;
        if (password.match(/[a-z]+/)) strength += 1;
        if (password.match(/[A-Z]+/)) strength += 1;
        if (password.match(/[0-9]+/)) strength += 1;
        if (password.match(/[^a-zA-Z0-9]+/)) strength += 1;
        
        // You could add visual feedback based on strength
        // This is just a placeholder for now
        console.log(`Password strength: ${strength}/5`);
    });
});