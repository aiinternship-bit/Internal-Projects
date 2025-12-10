# AI-Interns Dashboard

A modern Flask-based web application that provides a beautiful tile-based interface to navigate between different AI projects with an AI-powered chatbot assistant featuring persistent conversations and intelligent conversation management.

## Features

### Interface & Design
- **Modern, responsive tile-based interface** (3 tiles per row on desktop, square-shaped)
- **ACL Digital branding** with custom logo and gradient theme
- **Adaptive theme**: White header on homepage, gradient header in chat windows
- **Apple-inspired UI** with smooth animations and glassmorphism effects
- **Mobile-friendly responsive design**

### AI Chatbot
- **Powered by Claude AI** (Anthropic Claude 3.5 Sonnet) for intelligent project assistance
- **Persistent conversation history** with SQLite database storage
- **Multi-project support**: Separate conversations for each AI project
- **Conversation sidebar** with conversation management
- **Auto-generated titles**: Conversations automatically named from first AI response
- **Markdown rendering** support for rich text responses
- **Message bubbles** for user messages with proper formatting

### Conversation Management
- **Create unlimited conversations** per project
- **Switch between conversations** seamlessly
- **Delete conversations** with custom confirmation modal
- **Conversation preview** showing last message
- **Auto-save**: All messages automatically saved to database
- **Persistent storage**: Conversations survive server restarts

### Project Integration
- **RAG Integration**: Connects to GEN AI Agent and Zebra Project
- **Context-aware responses**: AI has knowledge of project files and structure
- **Multiple project types**: AppDevReport, Archive, and Z Printer Scout

## Prerequisites

- Python 3.8 or higher
- pip (Python package installer)

## Installation

1. Navigate to the AI-Interns directory:
```bash
cd AI-Interns
```

2. Create a virtual environment (recommended):
```bash
python3 -m venv venv
```

3. Activate the virtual environment:
   - On macOS/Linux:
     ```bash
     source venv/bin/activate
     ```
   - On Windows:
     ```bash
     venv\Scripts\activate
     ```

4. Install the required dependencies:
```bash
pip install -r requirements.txt
```

5. Configure Anthropic API Key:
   - Get your API key from [Anthropic Console](https://console.anthropic.com/)
   - Create a `.env` file in the project root:
     ```bash
     cp .env.example .env
     ```
   - Edit the `.env` file and add your API key:
     ```
     ANTHROPIC_API_KEY=your_actual_api_key_here
     ```

## Running the Application

1. Make sure you're in the AI-Interns directory with the virtual environment activated

2. Run the Flask application:
```bash
python app.py
```

3. Open your web browser and navigate to:
```
http://localhost:5001
```

The application will be accessible on your local network at `http://0.0.0.0:5001`

## Project Structure

```
AI-Interns/
├── app.py                 # Main Flask application
├── requirements.txt       # Python dependencies
├── README.md             # This file
├── templates/            # HTML templates
│   ├── index.html        # Main dashboard page
│   └── project_detail.html # Project detail page
└── static/               # Static assets
    ├── css/
    │   └── style.css     # Stylesheet
    └── js/
        └── main.js       # JavaScript functionality
```

## Usage

### Main Dashboard
- View all available projects as interactive square tiles (3 per row on desktop)
- Click the "Add New Project" tile to create new projects

### AI Chatbot
1. Click on any project tile to open the AI chatbot
2. The chatbot has context about the project and its files
3. Ask questions like:
   - "What files are in this project?"
   - "Explain what this project does"
   - "Help me understand the code structure"
   - General programming questions
4. The chatbot maintains conversation history within the session

### Adding New Projects
1. Click on the "Add New Project" tile
2. Fill in the project details:
   - **Project Name**: e.g., "Solution #3"
   - **Description**: Brief description of your project
   - **Icon**: An emoji to represent your project (e.g., 🎨)
   - **Project Path**: Relative path to your project folder (e.g., "../My New Project")
   - **Theme Color**: Pick a color for your project
3. Click "Add Project"

### Navigation
- Use the close button or press ESC to exit the chatbot or modal

## Customization

To add or modify projects, edit the `PROJECTS` list in [app.py](app.py):

```python
PROJECTS = [
    {
        'id': 'project-id',
        'name': 'Project Name',
        'description': 'Project description',
        'icon': '🚀',
        'path': '../Project Path',
        'color': '#HEX_COLOR'
    }
]
```

## Technologies Used

- **Backend**: Flask 3.0.0
- **AI**: Anthropic Claude API (Claude 3.5 Sonnet)
- **Frontend**: HTML5, CSS3, Vanilla JavaScript
- **Design**: Apple-inspired UI with glassmorphism effects and responsive grid layout

## Troubleshooting

- **Import errors for `anthropic` or `dotenv`**:
  - Make sure your virtual environment is activated
  - Run `pip install -r requirements.txt` again
  - If you get an "externally-managed-environment" error, make sure you're using a virtual environment

- **"ANTHROPIC_API_KEY not found" error**:
  - Check that your `.env` file exists in the project root
  - Verify the API key is correctly set in the `.env` file (no quotes needed)
  - Make sure the `.env` file is in the same directory as `app.py`

- **Chatbot not responding**:
  - Check the server console for error messages
  - Verify your API key is valid at [Anthropic Console](https://console.anthropic.com/)
  - Check your internet connection

- **Port already in use**: The app runs on port 5001. If this port is in use, modify it in `app.py`:
  ```python
  app.run(debug=True, host='0.0.0.0', port=5002)
  ```

- **Module not found**: Make sure you've activated the virtual environment and installed dependencies:
  ```bash
  source venv/bin/activate  # or venv\Scripts\activate on Windows
  pip install -r requirements.txt
  ```

## Notes

- Conversation history is stored in memory and will reset when the server restarts
- Projects added via the UI are temporary and will reset on server restart
- Maximum of 20 messages are kept in conversation history to manage token usage

## License

This project is part of the AI-Interns initiative.