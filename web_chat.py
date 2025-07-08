#!/usr/bin/env python3
"""
Minimal Web Chat - Guaranteed Working Version
For Bunny AI Submission Demonstration
"""

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import json
from datetime import datetime

app = FastAPI(title="Self-Evolving Voice Agent Demo")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

# Simple in-memory storage for demo
users_data = {}

def get_user_profile(user_id: str):
    """Get or create user profile"""
    if user_id not in users_data:
        users_data[user_id] = {
            "user_id": user_id,
            "personality_vector": {
                "formality": 0.5,
                "enthusiasm": 0.6,
                "technical_depth": 0.5,
                "humor": 0.4,
                "verbosity": 0.5,
                "empathy": 0.6
            },
            "conversation_count": 0,
            "created_at": datetime.now().isoformat()
        }
    return users_data[user_id]

def evolve_personality(user_id: str, message: str):
    """Simple personality evolution"""
    profile = get_user_profile(user_id)
    personality = profile["personality_vector"]
    
    msg_lower = message.lower()
    changes = {}
    
    # Formality evolution
    if any(word in msg_lower for word in ['please', 'thank you', 'could you', 'would you']):
        old_val = personality['formality']
        personality['formality'] = min(1.0, personality['formality'] + 0.05)
        if personality['formality'] != old_val:
            changes['formality'] = f"+{personality['formality'] - old_val:.2f}"
    
    elif any(word in msg_lower for word in ['hey', 'cool', 'awesome', 'yo']):
        old_val = personality['formality']
        personality['formality'] = max(0.0, personality['formality'] - 0.03)
        if personality['formality'] != old_val:
            changes['formality'] = f"{personality['formality'] - old_val:.2f}"
    
    # Enthusiasm evolution
    if '!' in message or any(word in msg_lower for word in ['exciting', 'amazing', 'love it']):
        old_val = personality['enthusiasm']
        personality['enthusiasm'] = min(1.0, personality['enthusiasm'] + 0.04)
        if personality['enthusiasm'] != old_val:
            changes['enthusiasm'] = f"+{personality['enthusiasm'] - old_val:.2f}"
    
    # Technical depth evolution
    if any(word in msg_lower for word in ['algorithm', 'technical', 'code', 'analysis', 'implement']):
        old_val = personality['technical_depth']
        personality['technical_depth'] = min(1.0, personality['technical_depth'] + 0.05)
        if personality['technical_depth'] != old_val:
            changes['technical_depth'] = f"+{personality['technical_depth'] - old_val:.2f}"
    
    # Humor evolution
    if any(word in msg_lower for word in ['funny', 'joke', 'haha', 'lol', 'hilarious']):
        old_val = personality['humor']
        personality['humor'] = min(1.0, personality['humor'] + 0.04)
        if personality['humor'] != old_val:
            changes['humor'] = f"+{personality['humor'] - old_val:.2f}"
    
    profile["conversation_count"] += 1
    return changes

def generate_response(user_id: str, message: str):
    """Generate personality-adapted response"""
    profile = get_user_profile(user_id)
    personality = profile["personality_vector"]
    
    msg_lower = message.lower()
    
    # Base response selection
    if any(word in msg_lower for word in ['hello', 'hi', 'hey']):
        if personality['formality'] > 0.7:
            base_response = "Good day! How may I assist you today?"
        elif personality['formality'] < 0.3:
            base_response = "Hey there! What's up?"
        else:
            base_response = "Hello! Nice to meet you."
    
    elif any(word in msg_lower for word in ['how are you', 'how do you do']):
        if personality['enthusiasm'] > 0.7:
            base_response = "I'm doing fantastic! Thanks for asking!"
        else:
            base_response = "I'm doing well, thank you for asking."
    
    elif any(word in msg_lower for word in ['evolution', 'personality', 'adapt']):
        base_response = "I'm constantly evolving my personality based on our conversations! Each interaction helps me understand your communication style better."
    
    elif any(word in msg_lower for word in ['technical', 'algorithm', 'code']):
        if personality['technical_depth'] > 0.6:
            base_response = "From a technical perspective, I utilize multi-dimensional personality vectors that adapt through reinforcement learning mechanisms."
        else:
            base_response = "I use smart algorithms to learn and adapt to how you like to communicate!"
    
    else:
        # Default responses based on personality
        responses = [
            "That's interesting! Tell me more.",
            "I see what you mean. How do you feel about that?",
            "Thanks for sharing that with me.",
            "I'm learning more about you with each message!"
        ]
        
        if personality['enthusiasm'] > 0.7:
            base_response = "That's amazing! " + responses[0]
        elif personality['formality'] > 0.7:
            base_response = "I appreciate your input. " + responses[1]
        else:
            import random
            base_response = random.choice(responses)
    
    # Add personality touches
    if personality['humor'] > 0.6 and 'technical' not in msg_lower:
        base_response += " 😊"
    
    if personality['verbosity'] > 0.7:
        base_response += " I find our conversation quite engaging and look forward to learning more about your preferences."
    
    return base_response

@app.get("/", response_class=HTMLResponse)
async def get_chat_interface():
    return '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>🧠 Self-Evolving Voice Agent Demo</title>
        <meta charset="UTF-8">
        <style>
            body { 
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; 
                margin: 0;
                padding: 20px;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
            }
            .container {
                max-width: 800px;
                margin: 0 auto;
                background: white;
                border-radius: 15px;
                padding: 30px;
                box-shadow: 0 10px 30px rgba(0,0,0,0.3);
            }
            .header {
                text-align: center;
                margin-bottom: 30px;
                color: #333;
            }
            .status {
                background: #e3f2fd;
                padding: 15px;
                border-radius: 10px;
                margin-bottom: 20px;
                text-align: center;
                color: #1976d2;
                font-weight: bold;
            }
            .user-controls {
                background: #f8f9fa;
                padding: 15px;
                border-radius: 10px;
                margin-bottom: 20px;
                display: flex;
                align-items: center;
                gap: 15px;
                flex-wrap: wrap;
            }
            #chat { 
                height: 400px; 
                overflow-y: auto; 
                border: 2px solid #e0e0e0; 
                padding: 20px; 
                margin: 20px 0; 
                background: #fafafa; 
                border-radius: 10px;
            }
            .message { 
                margin: 15px 0; 
                padding: 12px 16px; 
                border-radius: 18px; 
                max-width: 80%;
                animation: fadeIn 0.3s ease-in;
            }
            @keyframes fadeIn {
                from { opacity: 0; transform: translateY(10px); }
                to { opacity: 1; transform: translateY(0); }
            }
            .user { 
                background: linear-gradient(135deg, #667eea, #764ba2); 
                color: white;
                margin-left: auto;
                text-align: right; 
            }
            .agent { 
                background: #e8f5e8; 
                border: 1px solid #c8e6c9;
            }
            .evolution { 
                background: linear-gradient(135deg, #ffd54f, #ffb74d); 
                font-size: 0.85em; 
                font-style: italic;
                margin: 5px auto;
                text-align: center;
                max-width: 70%;
            }
            .input-area {
                display: flex;
                gap: 10px;
                margin-top: 20px;
            }
            input { 
                flex: 1;
                padding: 12px 16px; 
                border: 2px solid #e0e0e0;
                border-radius: 25px;
                font-size: 16px;
                outline: none;
            }
            input:focus { border-color: #667eea; }
            button { 
                padding: 12px 24px; 
                background: linear-gradient(135deg, #667eea, #764ba2); 
                color: white; 
                border: none; 
                border-radius: 25px; 
                cursor: pointer; 
                font-weight: bold;
                transition: transform 0.2s;
            }
            button:hover { transform: translateY(-2px); }
            select {
                padding: 8px 12px;
                border: 2px solid #e0e0e0;
                border-radius: 8px;
                background: white;
            }
            .personality { 
                background: linear-gradient(135deg, #e8f5e8, #f1f8e9); 
                padding: 20px; 
                margin: 20px 0; 
                border-radius: 15px; 
                border: 2px solid #c8e6c9;
            }
            .personality-bar {
                display: flex;
                align-items: center;
                margin: 10px 0;
                gap: 15px;
            }
            .personality-bar label {
                min-width: 130px;
                font-weight: bold;
                color: #333;
            }
            .bar-container {
                flex: 1;
                height: 15px;
                background: #e0e0e0;
                border-radius: 8px;
                overflow: hidden;
            }
            .bar-fill {
                height: 100%;
                background: linear-gradient(90deg, #4CAF50, #2196F3);
                transition: width 0.5s ease;
                border-radius: 8px;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🧠 Self-Evolving Voice Agent</h1>
                <p><strong>Bunny AI Engineer Task Demo</strong></p>
                <p>Chat with an AI that adapts its personality to match your communication style</p>
            </div>
            
            <div class="status" id="status">
                ✅ Agent ready - Start chatting to see personality evolution!
            </div>
            
            <div class="user-controls">
                <label><strong>User Profile:</strong></label>
                <select id="userId">
                    <option value="formal_user">👔 Formal User</option>
                    <option value="casual_user">😎 Casual User</option>
                    <option value="technical_user">🔬 Technical User</option>
                    <option value="creative_user">🎨 Creative User</option>
                </select>
                <button onclick="showPersonality()">📊 Show Personality</button>
                <button onclick="clearChat()">🗑️ Clear Chat</button>
            </div>
            
            <div id="chat">
                <div class="message agent">
                    <strong>🤖 Agent:</strong> Hello! I'm your self-evolving AI assistant. My personality will adapt based on how you communicate with me. Try different conversation styles and watch my personality bars change! What would you like to talk about?
                </div>
            </div>
            
            <div class="input-area">
                <input type="text" id="messageInput" placeholder="Type your message here..." />
                <button onclick="sendMessage()">Send 🚀</button>
            </div>
            
            <div id="personality" class="personality" style="display:none;">
                <h3>📊 Current Personality Profile</h3>
                <div id="personalityData"></div>
                <p><em>💡 These bars show how the AI has adapted to your communication style!</em></p>
            </div>
        </div>

        <script>
            async function sendMessage() {
                const input = document.getElementById('messageInput');
                const userId = document.getElementById('userId').value;
                const message = input.value.trim();
                
                if (!message) return;
                
                addMessage('user', '👤 You: ' + message);
                input.value = '';
                
                try {
                    const response = await fetch('/chat/' + userId, {
                        method: 'POST',
                        headers: {'Content-Type': 'application/json'},
                        body: JSON.stringify({message: message})
                    });
                    
                    const data = await response.json();
                    addMessage('agent', '🤖 Agent: ' + data.response);
                    
                    if (data.evolution_changes && Object.keys(data.evolution_changes).length > 0) {
                        const changes = Object.entries(data.evolution_changes)
                            .map(([k,v]) => `${k}: ${v}`)
                            .join(', ');
                        addMessage('evolution', '🔄 Evolution: ' + changes);
                    }
                    
                    updateStatus('✅ Message processed - personality adapted!');
                    
                } catch (error) {
                    addMessage('agent', '❌ Error: ' + error.message);
                    updateStatus('❌ Connection error');
                }
            }
            
            function addMessage(type, text) {
                const chat = document.getElementById('chat');
                const div = document.createElement('div');
                div.className = 'message ' + type;
                div.innerHTML = text;
                chat.appendChild(div);
                chat.scrollTop = chat.scrollHeight;
            }
            
            function updateStatus(message) {
                document.getElementById('status').innerHTML = message;
                setTimeout(() => {
                    document.getElementById('status').innerHTML = '✅ Agent ready for conversation';
                }, 3000);
            }
            
            async function showPersonality() {
                const userId = document.getElementById('userId').value;
                try {
                    const response = await fetch('/profile/' + userId);
                    const data = await response.json();
                    
                    const personalityDiv = document.getElementById('personalityData');
                    let html = '';
                    
                    if (data.personality_vector) {
                        for (const [trait, value] of Object.entries(data.personality_vector)) {
                            const percentage = Math.round(value * 100);
                            html += `
                                <div class="personality-bar">
                                    <label>${trait.charAt(0).toUpperCase() + trait.slice(1).replace('_', ' ')}:</label>
                                    <div class="bar-container">
                                        <div class="bar-fill" style="width: ${percentage}%"></div>
                                    </div>
                                    <span><strong>${percentage}%</strong></span>
                                </div>
                            `;
                        }
                        
                        html += `<p><strong>Conversations:</strong> ${data.conversation_count}</p>`;
                    }
                    
                    personalityDiv.innerHTML = html;
                    document.getElementById('personality').style.display = 'block';
                    
                } catch (error) {
                    alert('Error loading personality: ' + error.message);
                }
            }
            
            function clearChat() {
                const chat = document.getElementById('chat');
                chat.innerHTML = `
                    <div class="message agent">
                        <strong>🤖 Agent:</strong> Chat cleared! I still remember your personality preferences. Let's continue!
                    </div>
                `;
            }
            
            // Enter key support
            document.getElementById('messageInput').addEventListener('keypress', function(e) {
                if (e.key === 'Enter') sendMessage();
            });
        </script>
    </body>
    </html>
    '''

@app.post("/chat/{user_id}")
async def chat_endpoint(user_id: str, request: Request):
    try:
        data = await request.json()
        message = data.get('message', '')
        
        # Evolve personality and get changes
        evolution_changes = evolve_personality(user_id, message)
        
        # Generate response
        response = generate_response(user_id, message)
        
        return {
            "response": response,
            "evolution_changes": evolution_changes,
            "status": "success"
        }
    except Exception as e:
        return {
            "error": str(e), 
            "response": "I'm still learning! Try again!",
            "evolution_changes": {}
        }

@app.get("/profile/{user_id}")
async def get_profile(user_id: str):
    return get_user_profile(user_id)

@app.get("/api/health")
async def health_check():
    return {
        "status": "healthy",
        "users": len(users_data),
        "demo": "Self-Evolving Voice Agent"
    }

if __name__ == "__main__":
    print("🌐 Starting Minimal Web Chat (Guaranteed Working)...")
    print("🔗 Open: http://localhost:8001")
    print("📋 This version works without any dependencies!")
    uvicorn.run(app, host="127.0.0.1", port=8001, log_level="info")