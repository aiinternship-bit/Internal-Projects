from flask import Flask, render_template, jsonify
import os

app = Flask(__name__)

# Project configuration
PROJECTS = [
    {
        'id': 'ai-initiatives',
        'name': 'AI Initiatives',
        'description': 'React Native mobile apps and AI-powered solutions',
        'icon': '🚀',
        'path': '../AI Initiatives',
        'color': '#4A90E2'
    },
    {
        'id': 'gen-ai-agent',
        'name': 'GEN AI Agent',
        'description': 'Generative AI agent projects and implementations',
        'icon': '🤖',
        'path': '../GEN AI Agent',
        'color': '#7B68EE'
    }
]

@app.route('/')
def index():
    """Render the main dashboard with project tiles"""
    return render_template('index.html', projects=PROJECTS)

@app.route('/api/projects')
def get_projects():
    """API endpoint to get all projects"""
    return jsonify(PROJECTS)

@app.route('/project/<project_id>')
def project_detail(project_id):
    """Display details for a specific project"""
    project = next((p for p in PROJECTS if p['id'] == project_id), None)
    if project:
        # Get project files/folders
        base_path = os.path.join(os.path.dirname(__file__), project['path'])
        try:
            items = []
            if os.path.exists(base_path):
                for item in os.listdir(base_path):
                    if not item.startswith('.'):
                        item_path = os.path.join(base_path, item)
                        items.append({
                            'name': item,
                            'is_dir': os.path.isdir(item_path)
                        })
            project['items'] = sorted(items, key=lambda x: (not x['is_dir'], x['name']))
        except Exception as e:
            project['items'] = []
            project['error'] = str(e)

        return render_template('project_detail.html', project=project)
    else:
        return "Project not found", 404

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)
