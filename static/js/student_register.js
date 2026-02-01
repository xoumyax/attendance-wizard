// Student Registration Page JavaScript

const registerForm = document.getElementById('registerForm');
const errorMessage = document.getElementById('error-message');
const successMessage = document.getElementById('success-message');

registerForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const name = document.getElementById('name').value.trim();
    const uin = document.getElementById('uin').value.trim();
    const password = document.getElementById('password').value;
    const confirmPassword = document.getElementById('confirmPassword').value;
    
    // Hide previous messages
    errorMessage.style.display = 'none';
    successMessage.style.display = 'none';
    
    // Validate password match
    if (password !== confirmPassword) {
        showError('Passwords do not match');
        return;
    }
    
    // Validate password length
    if (password.length < 6) {
        showError('Password must be at least 6 characters');
        return;
    }
    
    // Validate UIN format (9 digits)
    if (!/^\d{9}$/.test(uin)) {
        showError('UIN must be exactly 9 digits');
        return;
    }
    
    try {
        const response = await fetch('/api/student/register', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                name: name,
                uin: uin,
                password: password
            })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            // Hide the form and "Already registered?" link
            registerForm.style.display = 'none';
            document.getElementById('login-link').style.display = 'none';
            
            // Show success message with login button
            successMessage.innerHTML = `
                <h3 style="color: #2ecc71; margin-bottom: 1rem;">✅ Registration Successful!</h3>
                <p style="margin-bottom: 1.5rem;">Your account has been created successfully. Please login with your UIN and password.</p>
                <a href="/student/login" class="btn btn-primary" style="text-decoration: none; display: inline-block; padding: 0.75rem 2rem;">
                    Go to Login Page
                </a>
            `;
            successMessage.style.display = 'block';
        } else {
            showError(data.detail || 'Registration failed');
        }
    } catch (error) {
        console.error('Error:', error);
        showError('An error occurred during registration');
    }
});

function showError(message) {
    errorMessage.textContent = message;
    errorMessage.style.display = 'block';
}

function showSuccess(message) {
    successMessage.textContent = message;
    successMessage.style.display = 'block';
}
