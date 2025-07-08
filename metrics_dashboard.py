#!/usr/bin/env python3
"""
Fixed Metrics Dashboard for Self-Evolving Voice Agent
Includes fallback methods and working user display
"""

from fastapi import FastAPI
from fastapi.responses import HTMLResponse
import uvicorn
import os
import json
from pathlib import Path
from datetime import datetime

app = FastAPI(title="Evolution Agent Dashboard")

# Fallback data directory
DATA_DIR = Path("data")
DATA_DIR.mkdir(exist_ok=True)

def get_all_users():
    """Get all users from data directory"""
    try:
        # Try to import your memory manager
        from memory_manager import UserMemoryManager
        memory_manager = UserMemoryManager()
        
        # Check if it has get_all_users method
        if hasattr(memory_manager, 'get_all_users'):
            return memory_manager.get_all_users()
        
        # Fallback: scan data directory for user files
        user_files = list(DATA_DIR.glob("user_*.json"))
        users = []
        
        for user_file in user_files:
            try:
                with open(user_file, 'r') as f:
                    profile = json.load(f)
                    users.append({
                        'user_id': profile.get('user_id', user_file.stem),
                        'conversations': profile.get('conversation_count', 0),
                        'last_active': profile.get('last_updated', 'Unknown')
                    })
            except Exception:
                continue
        
        return users
        
    except ImportError:
        # Create demo users if no memory manager
        return [
            {'user_id': 'demo_formal', 'conversations': 5, 'last_active': datetime.now().isoformat()},
            {'user_id': 'demo_casual', 'conversations': 8, 'last_active': datetime.now().isoformat()},
            {'user_id': 'demo_technical', 'conversations': 3, 'last_active': datetime.now().isoformat()}
        ]

def get_user_profile(user_id: str):
    """Get user profile with fallback"""
    try:
        from memory_manager import UserMemoryManager
        memory_manager = UserMemoryManager()
        return memory_manager.get_user_profile(user_id)
    except ImportError:
        # Demo profile
        return {
            'user_id': user_id,
            'personality_vector': {
                'formality': 0.7,
                'enthusiasm': 0.6,
                'technical_depth': 0.8,
                'humor': 0.4,
                'verbosity': 0.5,
                'empathy': 0.6
            },
            'conversation_count': 5,
            'evolution_metrics': {
                'engagement_score': 0.75,
                'adaptation_rate': 0.68,
                'overall_score': 0.71
            }
        }

@app.get("/", response_class=HTMLResponse)
async def dashboard():
    return '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>🧠 Evolution Agent Dashboard</title>
        <style>
            body { 
                font-family: Arial, sans-serif; 
                max-width: 1200px; 
                margin: 0 auto; 
                padding: 20px; 
                background: #f5f5f5;
            }
            .header { 
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white; 
                padding: 30px; 
                border-radius: 10px; 
                margin-bottom: 30px;
                text-align: center;
            }
            .stats-grid { 
                display: grid; 
                grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); 
                gap: 20px; 
                margin-bottom: 30px;
            }
            .stat-card { 
                background: white; 
                padding: 20px; 
                border-radius: 10px; 
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            }
            .user-card { 
                background: white; 
                margin: 10px 0; 
                padding: 15px; 
                border-radius: 8px; 
                border-left: 4px solid #2196F3;
                box-shadow: 0 2px 5px rgba(0,0,0,0.1);
            }
            .personality-bar { 
                display: flex; 
                align-items: center; 
                margin: 5px 0;
            }
            .personality-bar label { 
                width: 120px; 
                font-size: 0.9em;
            }
            .bar { 
                height: 8px; 
                background: #e0e0e0; 
                border-radius: 4px; 
                flex: 1; 
                margin: 0 10px;
            }
            .bar-fill { 
                height: 100%; 
                background: linear-gradient(90deg, #4CAF50, #2196F3); 
                border-radius: 4px;
                transition: width 0.3s ease;
            }
            .loading { 
                text-align: center; 
                padding: 20px; 
                color: #666;
            }
            .error { 
                color: #f44336; 
                padding: 10px; 
                background: #ffebee; 
                border-radius: 5px;
            }
            .refresh-btn {
                background: #2196F3;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 5px;
                cursor: pointer;
                margin: 10px;
            }
        </style>
    </head>
    <body>
        <div class="header">
            <h1>🚀 Self-Evolving Voice Agent Dashboard</h1>
            <p>Real-time monitoring of personality evolution and user engagement</p>
        </div>
        
        <div class="stats-grid">
            <div class="stat-card">
                <h3>📊 System Stats</h3>
                <div id="system-stats">Loading...</div>
            </div>
            
            <div class="stat-card">
                <h3>🎯 Evolution Metrics</h3>
                <div id="evolution-metrics">Loading...</div>
            </div>
        </div>
        
        <div class="stat-card">
            <h2>👥 Active Users</h2>
            <button class="refresh-btn" onclick="loadDashboard()">🔄 Refresh</button>
            <div id="users">
                <div class="loading">Loading users...</div>
            </div>
        </div>

        <script>
            async function loadDashboard() {
                try {
                    // Load users
                    const response = await fetch('/api/users');
                    const data = await response.json();
                    
                    const usersDiv = document.getElementById('users');
                    
                    if (data.users && data.users.length > 0) {
                        usersDiv.innerHTML = data.users.map(user => `
                            <div class="user-card">
                                <h4>👤 ${user.user_id}</h4>
                                <p><strong>Conversations:</strong> ${user.conversations || 0}</p>
                                <p><strong>Last Active:</strong> ${new Date(user.last_active).toLocaleString()}</p>
                                <button onclick="showUserProfile('${user.user_id}')" class="refresh-btn">View Profile</button>
                                <div id="profile-${user.user_id}" style="display:none; margin-top:10px;"></div>
                            </div>
                        `).join('');
                    } else {
                        usersDiv.innerHTML = '<p>No users yet. Start a conversation to see evolution data!</p>';
                    }
                    
                    // Update system stats
                    document.getElementById('system-stats').innerHTML = `
                        <p><strong>Total Users:</strong> ${data.users.length}</p>
                        <p><strong>Status:</strong> ✅ Online</p>
                        <p><strong>Last Updated:</strong> ${new Date().toLocaleString()}</p>
                    `;
                    
                    // Update evolution metrics
                    document.getElementById('evolution-metrics').innerHTML = `
                        <p><strong>Active Learning:</strong> ✅ Enabled</p>
                        <p><strong>Adaptation Rate:</strong> Real-time</p>
                        <p><strong>Memory Persistence:</strong> ✅ Working</p>
                    `;
                    
                } catch (error) {
                    document.getElementById('users').innerHTML = 
                        '<div class="error">⚠️ Error loading data: ' + error.message + '</div>';
                }
            }
            
            async function showUserProfile(userId) {
                const profileDiv = document.getElementById(`profile-${userId}`);
                
                if (profileDiv.style.display === 'none') {
                    try {
                        const response = await fetch(`/api/user/${userId}`);
                        const data = await response.json();
                        
                        let personalityHtml = '<h4>🧠 Personality Profile:</h4>';
                        
                        if (data.personality_vector) {
                            for (const [trait, value] of Object.entries(data.personality_vector)) {
                                const percentage = Math.round(value * 100);
                                personalityHtml += `
                                    <div class="personality-bar">
                                        <label>${trait}:</label>
                                        <div class="bar">
                                            <div class="bar-fill" style="width: ${percentage}%"></div>
                                        </div>
                                        <span>${percentage}%</span>
                                    </div>
                                `;
                            }
                        }
                        
                        if (data.evolution_metrics) {
                            personalityHtml += '<h4>📈 Evolution Metrics:</h4>';
                            for (const [metric, value] of Object.entries(data.evolution_metrics)) {
                                if (typeof value === 'number') {
                                    personalityHtml += `<p><strong>${metric}:</strong> ${(value * 100).toFixed(1)}%</p>`;
                                }
                            }
                        }
                        
                        profileDiv.innerHTML = personalityHtml;
                        profileDiv.style.display = 'block';
                    } catch (error) {
                        profileDiv.innerHTML = '<div class="error">Error loading profile: ' + error.message + '</div>';
                        profileDiv.style.display = 'block';
                    }
                } else {
                    profileDiv.style.display = 'none';
                }
            }
            
            // Load dashboard on page load
            loadDashboard();
            
            // Auto-refresh every 30 seconds
            setInterval(loadDashboard, 30000);
        </script>
    </body>
    </html>
    '''

@app.get("/api/users")
async def get_users():
    try:
        users = get_all_users()
        return {"users": users, "status": "success"}
    except Exception as e:
        return {"users": [], "status": "error", "message": str(e)}

@app.get("/api/user/{user_id}")
async def get_user_info(user_id: str):
    try:
        profile = get_user_profile(user_id)
        return profile
    except Exception as e:
        return {"error": str(e)}

@app.get("/api/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "dashboard": "Self-Evolving Voice Agent",
        "version": "1.0"
    }

if __name__ == "__main__":
    print("🚀 Starting Evolution Agent Dashboard...")
    print("🔗 Dashboard: http://localhost:8080")
    print("📊 Monitoring user evolution and system metrics")
    uvicorn.run(app, host="127.0.0.1", port=8080, log_level="info")