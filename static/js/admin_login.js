// Admin Login JavaScript

const loginForm = document.getElementById('loginForm');
const alertBox = document.getElementById('alertBox');

loginForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const username = document.getElementById('username').value.trim();
    const password = document.getElementById('password').value;
    
    if (!username || !password) {
        showAlert('Please fill in all fields', 'error');
        return;
    }
    
    try {
        const response = await fetch('/api/admin/login', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                username: username,
                password: password
            })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            // Store token and user info
            localStorage.setItem('token', data.access_token);
            localStorage.setItem('userType', data.user_type);
            localStorage.setItem('userInfo', JSON.stringify(data.user_info));
            
            showAlert('Login successful! Redirecting...', 'success');
            setTimeout(() => {
                window.location.href = '/admin/dashboard';
            }, 1000);
        } else {
            showAlert(data.detail || 'Invalid admin credentials', 'error');
        }
    } catch (error) {
        showAlert('Network error. Please try again.', 'error');
        console.error('Login error:', error);
    }
});

function showAlert(message, type) {
    alertBox.innerHTML = `<div class="alert alert-${type}">${message}</div>`;
    setTimeout(() => {
        alertBox.innerHTML = '';
    }, 5000);
}
