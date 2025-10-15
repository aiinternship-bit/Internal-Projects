# AI-Interns Dashboard

A Flask-based web application that provides a beautiful tile-based interface to navigate between different AI projects.

## Features

- Modern, responsive tile-based interface
- Navigate between AI Initiatives, GEN AI Agent, and AI-Interns projects
- Dark theme with smooth animations
- Project detail pages showing directory contents
- Mobile-friendly design

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

## Running the Application

1. Make sure you're in the AI-Interns directory with the virtual environment activated

2. Run the Flask application:
```bash
python app.py
```

3. Open your web browser and navigate to:
```
http://localhost:5000
```

The application will be accessible on your local network at `http://0.0.0.0:5000`

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

- **Main Dashboard**: View all available projects as interactive tiles
- **Project Details**: Click on any tile to view project information and directory contents
- **Navigation**: Use the back button or press ESC to return to the dashboard

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
- **Frontend**: HTML5, CSS3, JavaScript
- **Design**: Custom CSS with animations and responsive grid layout

## Troubleshooting

- **Port already in use**: If port 5000 is already in use, modify the port in `app.py`:
  ```python
  app.run(debug=True, host='0.0.0.0', port=5001)
  ```

- **Module not found**: Make sure you've activated the virtual environment and installed dependencies:
  ```bash
  source venv/bin/activate  # or venv\Scripts\activate on Windows
  pip install -r requirements.txt
  ```

## License

This project is part of the AI-Interns initiative.