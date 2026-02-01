// Admin Dashboard JavaScript

// Check if admin is logged in
if (!localStorage.getItem('token') || localStorage.getItem('userType') !== 'admin') {
    window.location.href = '/admin/login';
}

const alertBox = document.getElementById('alertBox');
const userInfo = JSON.parse(localStorage.getItem('userInfo'));
document.getElementById('adminName').textContent = `Admin: ${userInfo.username}`;

// Load dashboard on page load
window.addEventListener('load', () => {
    loadDashboard();
    loadSessions();
    loadSettings();
});

// Load dashboard statistics
async function loadDashboard() {
    try {
        const response = await fetch('/api/admin/dashboard', {
            headers: {
                'Authorization': `Bearer ${localStorage.getItem('token')}`
            }
        });
        
        const data = await response.json();
        
        if (response.ok) {
            document.getElementById('totalStudents').textContent = data.total_students;
            document.getElementById('totalSessions').textContent = data.total_sessions;
            document.getElementById('totalAttendances').textContent = data.total_attendances;
            
            // Display recent attendances
            displayRecentAttendances(data.recent_attendances);
        } else {
            showAlert('Failed to load dashboard', 'error');
        }
    } catch (error) {
        showAlert('Network error', 'error');
        console.error('Dashboard error:', error);
    }
}

// Display recent attendances
function displayRecentAttendances(attendances) {
    const container = document.getElementById('recentAttendances');
    
    if (attendances.length === 0) {
        container.innerHTML = '<p class="empty-state">No recent attendances</p>';
        return;
    }
    
    let html = '<table><thead><tr><th>Student</th><th>Roll No</th><th>Session Date</th><th>Marked At</th></tr></thead><tbody>';
    
    attendances.forEach(att => {
        const sessionDate = new Date(att.session_date).toLocaleDateString();
        const markedAt = new Date(att.marked_at).toLocaleString();
        
        html += `
            <tr>
                <td>${att.student_name}</td>
                <td>${att.student_roll_number}</td>
                <td>${sessionDate}</td>
                <td>${markedAt}</td>
            </tr>
        `;
    });
    
    html += '</tbody></table>';
    container.innerHTML = html;
}

// Load sessions for token generation
async function loadSessions() {
    try {
        const response = await fetch('/api/admin/sessions', {
            headers: {
                'Authorization': `Bearer ${localStorage.getItem('token')}`
            }
        });
        
        const sessions = await response.json();
        const select = document.getElementById('tokenSessionSelect');
        select.innerHTML = '<option value="">-- Select a session --</option>';
        
        sessions.forEach(session => {
            const option = document.createElement('option');
            option.value = session.id;
            const date = new Date(session.date);
            option.textContent = `Session ${session.id} - ${date.toLocaleDateString()}`;
            
            if (session.is_test_session) {
                option.textContent += ' (TEST)';
            }
            
            select.appendChild(option);
        });
    } catch (error) {
        showAlert('Error loading sessions', 'error');
        console.error('Load sessions error:', error);
    }
}

// Create test sessions
async function createTestSessions() {
    if (!confirm('Create 2 test sessions for today?')) return;
    
    try {
        const response = await fetch('/api/admin/sessions/create-test', {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${localStorage.getItem('token')}`
            }
        });
        
        const data = await response.json();
        
        if (response.ok) {
            showAlert(`✅ ${data.message}`, 'success');
            loadSessions();
            loadDashboard();
        } else {
            showAlert(data.detail || 'Failed to create test sessions', 'error');
        }
    } catch (error) {
        showAlert('Network error', 'error');
        console.error('Create test sessions error:', error);
    }
}

// Create regular sessions
async function createRegularSessions() {
    if (!confirm('Create 30 regular sessions on preset dates (Feb-Apr)?')) return;
    
    try {
        const response = await fetch('/api/admin/sessions/create-regular', {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${localStorage.getItem('token')}`
            }
        });
        
        const data = await response.json();
        
        if (response.ok) {
            showAlert(`✅ ${data.message}`, 'success');
            loadSessions();
            loadDashboard();
        } else {
            showAlert(data.detail || 'Failed to create regular sessions', 'error');
        }
    } catch (error) {
        showAlert('Network error', 'error');
        console.error('Create regular sessions error:', error);
    }
}

// Load today's sessions
async function loadTodaySessions() {
    try {
        const response = await fetch('/api/admin/sessions/today', {
            headers: {
                'Authorization': `Bearer ${localStorage.getItem('token')}`
            }
        });
        
        const data = await response.json();
        const card = document.getElementById('todaySessionsCard');
        const list = document.getElementById('todaySessionsList');
        
        if (data.sessions && data.sessions.length > 0) {
            let html = '<table><thead><tr><th>Session ID</th><th>Type</th><th>Actions</th></tr></thead><tbody>';
            
            data.sessions.forEach(session => {
                const type = session.is_test_session ? '<span class="badge badge-warning">TEST</span>' : '<span class="badge badge-info">Regular</span>';
                html += `
                    <tr>
                        <td>${session.id}</td>
                        <td>${type}</td>
                        <td><button class="btn btn-success" onclick="quickGenerateToken(${session.id})">Generate Token</button></td>
                    </tr>
                `;
            });
            
            html += '</tbody></table>';
            list.innerHTML = html;
            card.style.display = 'block';
        } else {
            list.innerHTML = '<p class="empty-state">No sessions for today. Create test sessions first!</p>';
            card.style.display = 'block';
        }
    } catch (error) {
        showAlert('Error loading today\'s sessions', 'error');
        console.error('Load today sessions error:', error);
    }
}

// Generate token
async function generateToken() {
    const sessionId = document.getElementById('tokenSessionSelect').value;
    
    if (!sessionId) {
        showAlert('Please select a session', 'error');
        return;
    }
    
    await quickGenerateToken(sessionId);
}

// Quick generate token
async function quickGenerateToken(sessionId) {
    try {
        const response = await fetch('/api/admin/tokens/generate', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${localStorage.getItem('token')}`
            },
            body: JSON.stringify({ session_id: parseInt(sessionId) })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            document.getElementById('tokenDisplay').textContent = data.token;
            document.getElementById('tokenExpiry').textContent = new Date(data.expires_at).toLocaleString();
            document.getElementById('tokenValidity').textContent = data.expiry_info;
            document.getElementById('generatedToken').style.display = 'block';
            
            showAlert(`✅ Token generated: ${data.token}`, 'success');
        } else {
            showAlert(data.detail || 'Failed to generate token', 'error');
        }
    } catch (error) {
        showAlert('Network error', 'error');
        console.error('Generate token error:', error);
    }
}

// Load settings
async function loadSettings() {
    try {
        const response = await fetch('/api/admin/settings', {
            headers: {
                'Authorization': `Bearer ${localStorage.getItem('token')}`
            }
        });
        
        const data = await response.json();
        
        if (response.ok) {
            document.getElementById('timeRestrictionToggle').checked = data.disable_time_restrictions;
        }
    } catch (error) {
        console.error('Load settings error:', error);
    }
}

// Update settings
async function updateSettings() {
    const disableTimeRestrictions = document.getElementById('timeRestrictionToggle').checked;
    
    try {
        const response = await fetch('/api/admin/settings', {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${localStorage.getItem('token')}`
            },
            body: JSON.stringify({ disable_time_restrictions: disableTimeRestrictions })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            showAlert(`✅ Time restrictions ${disableTimeRestrictions ? 'disabled' : 'enabled'}`, 'success');
        } else {
            showAlert('Failed to update settings', 'error');
        }
    } catch (error) {
        showAlert('Network error', 'error');
        console.error('Update settings error:', error);
    }
}

// Export to Excel
async function exportExcel() {
    try {
        const response = await fetch('/api/admin/export/excel', {
            headers: {
                'Authorization': `Bearer ${localStorage.getItem('token')}`
            }
        });
        
        const data = await response.json();
        
        if (response.ok) {
            showAlert(`✅ ${data.message}<br>File: ${data.filename}<br>Location: ${data.path}`, 'success');
        } else {
            showAlert(data.detail || 'Failed to export Excel', 'error');
        }
    } catch (error) {
        showAlert('Network error', 'error');
        console.error('Export Excel error:', error);
    }
}

// View token history
async function viewTokenHistory() {
    const modal = document.getElementById('tokenHistoryModal');
    const content = document.getElementById('tokenHistoryContent');
    
    modal.style.display = 'block';
    content.innerHTML = '<div class="spinner"></div>';
    
    try {
        const response = await fetch('/api/admin/tokens/history', {
            headers: {
                'Authorization': `Bearer ${localStorage.getItem('token')}`
            }
        });
        
        const data = await response.json();
        
        if (response.ok) {
            if (data.tokens.length === 0) {
                content.innerHTML = '<p class="empty-state">No tokens generated yet</p>';
                return;
            }
            
            let html = `
                <p style="color: #666; margin-bottom: 15px;">Total tokens generated: ${data.total}</p>
                <table>
                    <thead>
                        <tr>
                            <th>Session ID</th>
                            <th>Date</th>
                            <th>Type</th>
                            <th>Token</th>
                            <th>Generated At</th>
                            <th>Expires At</th>
                            <th>Status</th>
                        </tr>
                    </thead>
                    <tbody>
            `;
            
            data.tokens.forEach(token => {
                const sessionDate = new Date(token.session_date).toLocaleDateString();
                const createdAt = new Date(token.created_at).toLocaleString();
                const expiresAt = new Date(token.expires_at).toLocaleString();
                const sessionType = token.is_test_session ? 
                    '<span class="badge badge-warning">TEST</span>' : 
                    '<span class="badge badge-info">Regular</span>';
                
                let statusBadge;
                if (token.is_expired) {
                    statusBadge = '<span class="badge badge-danger">Expired</span>';
                } else if (token.is_active) {
                    statusBadge = '<span class="badge badge-success">Active</span>';
                } else {
                    statusBadge = '<span class="badge">Inactive</span>';
                }
                
                html += `
                    <tr>
                        <td>${token.session_id}</td>
                        <td>${sessionDate}</td>
                        <td>${sessionType}</td>
                        <td><strong>${token.token}</strong></td>
                        <td>${createdAt}</td>
                        <td>${expiresAt}</td>
                        <td>${statusBadge}</td>
                    </tr>
                `;
            });
            
            html += '</tbody></table>';
            content.innerHTML = html;
        } else {
            content.innerHTML = '<p class="empty-state">Failed to load token history</p>';
        }
    } catch (error) {
        content.innerHTML = '<p class="empty-state">Network error</p>';
        console.error('Token history error:', error);
    }
}

// Close token history modal
function closeTokenHistory() {
    document.getElementById('tokenHistoryModal').style.display = 'none';
}

// Logout
function logout() {
    localStorage.clear();
    window.location.href = '/admin/login';
}

// Show alert
function showAlert(message, type) {
    alertBox.innerHTML = `<div class="alert alert-${type}">${message}</div>`;
    setTimeout(() => {
        alertBox.innerHTML = '';
    }, 5000);
}
