from flask import Flask, request, jsonify, render_template
import requests
import os
from datetime import datetime
import json

app = Flask(__name__)

# OpenRouter API Configuration
OPENROUTER_API_KEY = os.getenv('OPENROUTER_API_KEY', 'your-api-key-here')
OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"
DEFAULT_MODEL = "anthropic/claude-3.5-sonnet"

class CSAgent:
    def __init__(self, api_key, model=DEFAULT_MODEL):
        self.api_key = api_key
        self.model = model
        self.conversation_history = []
        
    def add_system_message(self):
        """Add system message to define CS agent behavior"""
        system_message = {
            "role": "system",
            "content": """You are a helpful customer service agent. Your role is to:
1. Greet customers warmly and professionally
2. Listen carefully to their concerns
3. Provide accurate and helpful information
4. Escalate complex issues when necessary
5. Maintain a friendly and professional tone
6. Ask clarifying questions when needed
7. Provide solutions or next steps

Always be polite, patient, and solution-oriented."""
        }
        return system_message
    
    def chat(self, user_message, conversation_id=None):
        """Send message to OpenRouter API and get response"""
        try:
            # Prepare messages
            messages = [self.add_system_message()]
            
            # Add conversation history
            if self.conversation_history:
                messages.extend(self.conversation_history)
            
            # Add current user message
            messages.append({
                "role": "user",
                "content": user_message
            })
            
            # Prepare API request
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
                "HTTP-Referer": "http://localhost:5000",
                "X-Title": "CS Agent"
            }
            
            data = {
                "model": self.model,
                "messages": messages,
                "max_tokens": 1000,
                "temperature": 0.7
            }
            
            # Make API call
            response = requests.post(
                f"{OPENROUTER_BASE_URL}/chat/completions",
                headers=headers,
                json=data,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                assistant_message = result['choices'][0]['message']['content']
                
                # Update conversation history
                self.conversation_history.append({
                    "role": "user",
                    "content": user_message
                })
                self.conversation_history.append({
                    "role": "assistant",
                    "content": assistant_message
                })
                
                return {
                    "success": True,
                    "response": assistant_message,
                    "conversation_id": conversation_id,
                    "timestamp": datetime.now().isoformat()
                }
            else:
                return {
                    "success": False,
                    "error": f"API Error: {response.status_code} - {response.text}",
                    "conversation_id": conversation_id
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": f"Error: {str(e)}",
                "conversation_id": conversation_id
            }
    
    def clear_history(self):
        """Clear conversation history"""
        self.conversation_history = []
        return {"success": True, "message": "Conversation history cleared"}

# Initialize CS Agent
cs_agent = CSAgent(OPENROUTER_API_KEY)

@app.route('/')
def index():
    """Main page for CS Agent interface"""
    return render_template('index.html')

@app.route('/api/chat', methods=['POST'])
def chat():
    """API endpoint for chat functionality"""
    try:
        data = request.get_json()
        user_message = data.get('message', '')
        conversation_id = data.get('conversation_id')
        
        if not user_message:
            return jsonify({
                "success": False,
                "error": "Message is required"
            }), 400
        
        # Get response from CS Agent
        result = cs_agent.chat(user_message, conversation_id)
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": f"Server error: {str(e)}"
        }), 500

@app.route('/api/clear', methods=['POST'])
def clear_conversation():
    """Clear conversation history"""
    try:
        result = cs_agent.clear_history()
        return jsonify(result)
    except Exception as e:
        return jsonify({
            "success": False,
            "error": f"Server error: {str(e)}"
        }), 500

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "agent_model": cs_agent.model
    })

if __name__ == '__main__':
    # Create templates directory if it doesn't exist
    os.makedirs('templates', exist_ok=True)
    
    # Create basic HTML template
    html_template = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>CS Agent - Customer Service</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f5f5f5;
        }
        .chat-container {
            background: white;
            border-radius: 10px;
            padding: 20px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        .chat-messages {
            height: 400px;
            overflow-y: auto;
            border: 1px solid #ddd;
            padding: 15px;
            margin-bottom: 20px;
            border-radius: 5px;
        }
        .message {
            margin-bottom: 15px;
            padding: 10px;
            border-radius: 5px;
        }
        .user-message {
            background-color: #e3f2fd;
            margin-left: 20%;
        }
        .agent-message {
            background-color: #f5f5f5;
            margin-right: 20%;
        }
        .input-container {
            display: flex;
            gap: 10px;
        }
        #messageInput {
            flex: 1;
            padding: 10px;
            border: 1px solid #ddd;
            border-radius: 5px;
        }
        button {
            padding: 10px 20px;
            background-color: #007bff;
            color: white;
            border: none;
            border-radius: 5px;
            cursor: pointer;
        }
        button:hover {
            background-color: #0056b3;
        }
        .clear-btn {
            background-color: #dc3545;
        }
        .clear-btn:hover {
            background-color: #c82333;
        }
        .status {
            margin-top: 10px;
            padding: 10px;
            border-radius: 5px;
        }
        .success {
            background-color: #d4edda;
            color: #155724;
        }
        .error {
            background-color: #f8d7da;
            color: #721c24;
        }
    </style>
</head>
<body>
    <div class="chat-container">
        <h1>🤖 CS Agent - Customer Service</h1>
        <div class="chat-messages" id="chatMessages">
            <div class="message agent-message">
                <strong>CS Agent:</strong> Hello! I'm your customer service assistant. How can I help you today?
            </div>
        </div>
        <div class="input-container">
            <input type="text" id="messageInput" placeholder="Type your message here..." onkeypress="handleKeyPress(event)">
            <button onclick="sendMessage()">Send</button>
            <button class="clear-btn" onclick="clearConversation()">Clear</button>
        </div>
        <div id="status"></div>
    </div>

    <script>
        function handleKeyPress(event) {
            if (event.key === 'Enter') {
                sendMessage();
            }
        }

        async function sendMessage() {
            const messageInput = document.getElementById('messageInput');
            const message = messageInput.value.trim();
            
            if (!message) return;
            
            // Add user message to chat
            addMessage('You', message, 'user-message');
            messageInput.value = '';
            
            // Show loading
            const loadingId = addMessage('CS Agent', 'Typing...', 'agent-message');
            
            try {
                const response = await fetch('/api/chat', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ message: message })
                });
                
                const result = await response.json();
                
                // Remove loading message
                removeMessage(loadingId);
                
                if (result.success) {
                    addMessage('CS Agent', result.response, 'agent-message');
                    showStatus('Message sent successfully!', 'success');
                } else {
                    addMessage('CS Agent', 'Sorry, I encountered an error. Please try again.', 'agent-message');
                    showStatus('Error: ' + result.error, 'error');
                }
            } catch (error) {
                removeMessage(loadingId);
                addMessage('CS Agent', 'Sorry, I encountered an error. Please try again.', 'agent-message');
                showStatus('Network error: ' + error.message, 'error');
            }
        }

        function addMessage(sender, content, className) {
            const chatMessages = document.getElementById('chatMessages');
            const messageDiv = document.createElement('div');
            const messageId = 'msg-' + Date.now();
            messageDiv.id = messageId;
            messageDiv.className = 'message ' + className;
            messageDiv.innerHTML = `<strong>${sender}:</strong> ${content}`;
            chatMessages.appendChild(messageDiv);
            chatMessages.scrollTop = chatMessages.scrollHeight;
            return messageId;
        }

        function removeMessage(messageId) {
            const message = document.getElementById(messageId);
            if (message) {
                message.remove();
            }
        }

        async function clearConversation() {
            try {
                const response = await fetch('/api/clear', {
                    method: 'POST'
                });
                const result = await response.json();
                
                if (result.success) {
                    document.getElementById('chatMessages').innerHTML = 
                        '<div class="message agent-message"><strong>CS Agent:</strong> Hello! I\'m your customer service assistant. How can I help you today?</div>';
                    showStatus('Conversation cleared!', 'success');
                } else {
                    showStatus('Error clearing conversation: ' + result.error, 'error');
                }
            } catch (error) {
                showStatus('Network error: ' + error.message, 'error');
            }
        }

        function showStatus(message, type) {
            const statusDiv = document.getElementById('status');
            statusDiv.textContent = message;
            statusDiv.className = 'status ' + type;
            setTimeout(() => {
                statusDiv.textContent = '';
                statusDiv.className = 'status';
            }, 3000);
        }
    </script>
</body>
</html>"""
    
    # Write template to file
    with open('templates/index.html', 'w', encoding='utf-8') as f:
        f.write(html_template)
    
    print("🚀 CS Agent starting...")
    print("📝 Make sure to set your OPENROUTER_API_KEY environment variable")
    print("🌐 Access the application at: http://localhost:5000")
    
    app.run(debug=True, host='0.0.0.0', port=5000)
