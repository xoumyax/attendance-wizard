// Student Attendance JavaScript

// Check if user is logged in
if (!localStorage.getItem('token')) {
    window.location.href = '/';
}

const alertBox = document.getElementById('alertBox');
const attendanceForm = document.getElementById('attendanceForm');
const submitBtn = document.getElementById('submitBtn');
const windowStatus = document.getElementById('windowStatus');

// Load user info
const userInfo = JSON.parse(localStorage.getItem('userInfo'));
document.getElementById('studentName').textContent = `Welcome, ${userInfo.name}!`;

// Store settings state
let timeRestrictionsDisabled = false;
let hasTestSession = false;

// Load admin settings to check if time restrictions are disabled
async function loadSettings() {
    try {
        const response = await fetch('/api/admin/settings');
        if (response.ok) {
            const settings = await response.json();
            timeRestrictionsDisabled = settings.disable_time_restrictions;
        }
    } catch (error) {
        // Settings endpoint might require auth, that's okay
        console.log('Could not fetch settings (this is normal)');
    }
}

// Update time and window status
function updateTime() {
    const now = new Date();
    const timeString = now.toLocaleTimeString('en-US', {
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit'
    });
    document.getElementById('currentTime').textContent = timeString;
    
    checkAttendanceWindow();
}

function checkAttendanceWindow() {
    const hour = new Date().getHours();
    const isWithinWindow = hour >= 8 && hour < 9;
    
    // Allow if time restrictions disabled OR it's a test session OR within time window
    if (timeRestrictionsDisabled || hasTestSession || isWithinWindow) {
        if (timeRestrictionsDisabled) {
            windowStatus.innerHTML = '<span>✅ Testing Mode - All Day Access Enabled</span>';
            windowStatus.className = 'status-indicator status-test';
        } else if (hasTestSession) {
            windowStatus.innerHTML = '<span>✅ Test Session - 24 Hour Access</span>';
            windowStatus.className = 'status-indicator status-test';
        } else {
            windowStatus.innerHTML = '<span>✅ Attendance Window Open (8 AM - 9 AM)</span>';
            windowStatus.className = 'status-indicator status-open';
        }
        submitBtn.disabled = false;
    } else {
        windowStatus.innerHTML = '<span>⏰ Attendance Window Closed (Opens 8 AM - 9 AM)</span>';
        windowStatus.className = 'status-indicator status-closed';
        submitBtn.disabled = true;
    }
}

// Initialize
loadSettings();
updateTime();
setInterval(updateTime, 1000);

// Load available sessions
async function loadSessions() {
    try {
        const response = await fetch('/api/student/sessions/today', {
            headers: {
                'Authorization': `Bearer ${localStorage.getItem('token')}`
            }
        });
        
        const data = await response.json();
        const select = document.getElementById('sessionSelect');
        select.innerHTML = '<option value="">-- Select a session --</option>';
        
        if (data.sessions && data.sessions.length > 0) {
            // Check if any session is a test session
            hasTestSession = data.sessions.some(s => s.is_test_session);
            
            data.sessions.forEach(session => {
                const option = document.createElement('option');
                option.value = session.id;
                option.dataset.isTest = session.is_test_session;
                const date = new Date(session.date);
                option.textContent = `Session ${session.id} - ${date.toLocaleDateString()}`;
                
                if (session.is_test_session) {
                    option.textContent += ' (TEST SESSION - 24hr token validity)';
                }
                
                if (session.already_marked) {
                    option.textContent += ' ✓ Already Marked';
                    option.disabled = true;
                }
                
                select.appendChild(option);
            });
            
            // Update window status after loading sessions
            checkAttendanceWindow();
        } else {
            select.innerHTML = '<option value="">No sessions available for today</option>';
        }
    } catch (error) {
        showAlert('Error loading sessions', 'error');
        console.error('Load sessions error:', error);
    }
}

// Monitor session selection changes
document.getElementById('sessionSelect').addEventListener('change', function() {
    const selectedOption = this.options[this.selectedIndex];
    if (selectedOption && selectedOption.dataset.isTest === 'true') {
        hasTestSession = true;
        checkAttendanceWindow();
    }
});

loadSessions();

// Mark attendance
attendanceForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const sessionId = document.getElementById('sessionSelect').value;
    const token = document.getElementById('token').value.trim();
    
    if (!sessionId) {
        showAlert('Please select a session', 'error');
        return;
    }
    
    if (!token || token.length !== 6) {
        showAlert('Please enter a valid 6-digit token', 'error');
        return;
    }
    
    try {
        const response = await fetch('/api/student/attendance/mark', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${localStorage.getItem('token')}`
            },
            body: JSON.stringify({
                session_id: parseInt(sessionId),
                token: token
            })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            showAlert('✅ Attendance marked successfully!', 'success');
            document.getElementById('token').value = '';
            loadSessions(); // Reload to show updated status
        } else {
            showAlert(data.detail || 'Failed to mark attendance', 'error');
        }
    } catch (error) {
        showAlert('Network error. Please try again.', 'error');
        console.error('Mark attendance error:', error);
    }
});

// View records
async function viewMyRecords() {
    try {
        const response = await fetch('/api/student/attendance/my-records', {
            headers: {
                'Authorization': `Bearer ${localStorage.getItem('token')}`
            }
        });
        
        const data = await response.json();
        
        if (response.ok) {
            const stats = data.statistics;
            const message = `
📊 Your Attendance Statistics:

OVERALL:
• Total Sessions (All): ${stats.total_sessions}
• Attended (All): ${stats.attended_sessions}

FOR GRADING (Regular Sessions Only):
• Regular Sessions: ${stats.total_regular_sessions}
• Attended Regular: ${stats.attended_regular_sessions}
• Test Sessions Attended: ${stats.attended_test_sessions}
• Attendance %: ${stats.attendance_percentage}%
• Grade Points: ${stats.grade_points}/10

Note: Only regular sessions count toward your grade.
Test sessions are for practice/testing only.
            `;
            alert(message);
        } else {
            showAlert('Failed to load records', 'error');
        }
    } catch (error) {
        showAlert('Network error', 'error');
        console.error('View records error:', error);
    }
}

// Logout
function logout() {
    localStorage.clear();
    window.location.href = '/';
}

// Show alert
function showAlert(message, type) {
    alertBox.innerHTML = `<div class="alert alert-${type}">${message}</div>`;
    setTimeout(() => {
        alertBox.innerHTML = '';
    }, 5000);
}
