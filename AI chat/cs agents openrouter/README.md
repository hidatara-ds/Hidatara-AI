# CS Agent - Customer Service Bot

A Flask-based customer service agent that uses OpenRouter API to provide intelligent customer support.

## Features

- 🤖 AI-powered customer service responses
- 💬 Real-time chat interface
- 📝 Conversation history management
- 🎨 Clean and responsive UI
- 🔧 Easy configuration

## Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Get OpenRouter API Key

1. Visit [OpenRouter](https://openrouter.ai/keys)
2. Sign up and get your API key
3. Set the environment variable:

**Windows:**
```cmd
set OPENROUTER_API_KEY=your-api-key-here
```

**Linux/Mac:**
```bash
export OPENROUTER_API_KEY=your-api-key-here
```

### 3. Run the Application

```bash
python app.py
```

The application will be available at: http://localhost:5000

## API Endpoints

- `GET /` - Main chat interface
- `POST /api/chat` - Send message to CS agent
- `POST /api/clear` - Clear conversation history
- `GET /api/health` - Health check

## Configuration

### Environment Variables

- `OPENROUTER_API_KEY` - Your OpenRouter API key (required)
- Default model: `anthropic/claude-3.5-sonnet`

### Available Models

You can change the model by modifying the `DEFAULT_MODEL` variable in `app.py`:

- `anthropic/claude-3.5-sonnet` (default)
- `openai/gpt-4`
- `openai/gpt-3.5-turbo`
- `anthropic/claude-3-opus`
- `meta-llama/llama-2-70b-chat`
- `google/palm-2-chat-bison`

## Usage

1. Open your browser and go to http://localhost:5000
2. Start chatting with the CS agent
3. Use the "Clear" button to reset the conversation
4. The agent will maintain context throughout the conversation

## Customization

### System Message

You can customize the CS agent's behavior by modifying the `add_system_message()` method in the `CSAgent` class.

### UI Styling

The HTML template is embedded in the `app.py` file. You can modify the CSS styles to customize the appearance.

## Troubleshooting

### Common Issues

1. **API Key Error**: Make sure your OpenRouter API key is set correctly
2. **Network Error**: Check your internet connection
3. **Port Already in Use**: Change the port in `app.py` or kill the existing process

### Debug Mode

The application runs in debug mode by default. For production, set `debug=False` in the `app.run()` call.

## License

This project is open source and available under the MIT License. 