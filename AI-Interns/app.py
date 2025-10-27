from flask import Flask, render_template, jsonify, request
import os
import sys
import subprocess
import json
from pathlib import Path
from dotenv import load_dotenv
import anthropic
import time

# Load environment variables from centralized .env file at AI-Practice root
# Path: /Users/pranoy/Desktop/AI-Practice/.env
env_path = Path(__file__).resolve().parents[1] / '.env'
load_dotenv(dotenv_path=env_path)

# Clean up any stale milvus processes on startup
print("Cleaning up stale processes...")
subprocess.run(['killall', '-9', 'milvus'], stderr=subprocess.DEVNULL)
time.sleep(1)
print("✓ Cleanup complete")

# Add Archive to Python path for importing query engine
archive_path = Path(__file__).resolve().parents[1] / 'GEN AI Agent' / 'Archive'
sys.path.insert(0, str(archive_path))

# Add Zebra Project to Python path for importing RAG system
zebra_path = Path(__file__).resolve().parents[1] / 'Zebra Project'
sys.path.insert(0, str(zebra_path / 'src'))

# Global variables to hold initialized instances (lazy loading)
archive_query_engine = None
archive_llm = None
zebra_rag = None

def get_archive_engine():
    """Lazy initialization of Archive query engine - only loads when first used"""
    global archive_query_engine, archive_llm

    if archive_query_engine is not None:
        return archive_query_engine, archive_llm

    print("Initializing Archive query engine...")
    try:
        from src.query_engine import QueryEngine
        from src.llm_layer import LLMLayer
        from src import config as archive_config

        # Initialize Archive components with absolute database path
        archive_db_path = str(archive_path / 'milvus_edelivery.db')
        archive_query_engine = QueryEngine(db_path=archive_db_path)
        archive_llm = LLMLayer(model_name=archive_config.LLM_MODEL)
        print(f"✓ Archive query engine initialized successfully (DB: {archive_db_path})")
        return archive_query_engine, archive_llm
    except Exception as e:
        print(f"✗ Could not initialize Archive query engine: {e}")
        raise

def get_zebra_rag():
    """Lazy initialization of Zebra Project RAG - only loads when first used"""
    global zebra_rag

    if zebra_rag is not None:
        return zebra_rag

    print("Initializing Zebra Project RAG...")
    try:
        from printer_rag import PrinterRAG

        # Initialize Zebra RAG with ChromaDB path
        zebra_db_path = str(zebra_path / 'chroma_db')
        zebra_rag = PrinterRAG(db_path=zebra_db_path, collection_name='printer_specs')
        print(f"✓ Zebra Project RAG initialized successfully (DB: {zebra_db_path})")
        return zebra_rag
    except Exception as e:
        print(f"✗ Could not initialize Zebra Project RAG: {e}")
        raise

app = Flask(__name__)

# Initialize Anthropic client
ANTHROPIC_API_KEY = os.getenv('ANTHROPIC_API_KEY')
if not ANTHROPIC_API_KEY:
    print("Warning: ANTHROPIC_API_KEY not found in environment variables")
    client = None
else:
    client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

# Store conversation history per session (in-memory, will reset on server restart)
conversation_histories = {}

# Project configuration
PROJECTS = [
    {
        'id': 'ai-initiatives',
        'name': 'AppDevReport',
        'description': 'AI-powered solutions for React Native mobile apps',
        'icon': '🚀',
        'path': '../AI Initiatives',
        'color': '#4A90E2'
    },
    {
        'id': 'gen-ai-agent',
        'name': 'ACLVectorNexus',
        'description': 'Reusable AI RAG System',
        'icon': '🤖',
        'path': '../GEN AI Agent/Archive',
        'color': '#7B68EE'
    },
    {
        'id': 'zebra-project',
        'name': 'ZPrinterScout',
        'description': 'Search Zebra Printers Specifications',
        'icon': '🖨️',
        'path': '../Zebra Project',
        'color': '#E74C3C'
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

@app.route('/api/add-project', methods=['POST'])
def add_project():
    """API endpoint to add a new project"""
    try:
        data = request.get_json()

        # Validate required fields
        required_fields = ['name', 'description', 'icon', 'path', 'color']
        for field in required_fields:
            if field not in data or not data[field]:
                return jsonify({'error': f'Missing required field: {field}'}), 400

        # Generate project ID from name
        project_id = data['name'].lower().replace(' ', '-').replace('#', '')

        # Check if project ID already exists
        if any(p['id'] == project_id for p in PROJECTS):
            return jsonify({'error': 'A project with this name already exists'}), 400

        # Create new project
        new_project = {
            'id': project_id,
            'name': data['name'],
            'description': data['description'],
            'icon': data['icon'],
            'path': data['path'],
            'color': data['color']
        }

        # Add to projects list
        PROJECTS.append(new_project)

        return jsonify({
            'success': True,
            'project': new_project
        }), 200

    except Exception as e:
        print(f"Error adding project: {str(e)}")
        return jsonify({'error': str(e)}), 500

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

@app.route('/api/run-script', methods=['POST'])
def run_script():
    """Execute a Python script from a project"""
    try:
        data = request.get_json()
        project_id = data.get('project_id')
        filename = data.get('filename')

        if not project_id or not filename:
            return jsonify({'error': 'Missing project_id or filename'}), 400

        # Find the project
        project = next((p for p in PROJECTS if p['id'] == project_id), None)
        if not project:
            return jsonify({'error': 'Project not found'}), 404

        # Build the file path
        base_path = os.path.join(os.path.dirname(__file__), project['path'])
        file_path = os.path.join(base_path, filename)

        # Security check - ensure file is within project directory
        if not os.path.abspath(file_path).startswith(os.path.abspath(base_path)):
            return jsonify({'error': 'Invalid file path'}), 403

        # Check if file exists and is a Python file
        if not os.path.exists(file_path):
            return jsonify({'error': 'File not found'}), 404

        if not filename.endswith('.py'):
            return jsonify({'error': 'Only Python files can be executed'}), 400

        # Execute the script
        try:
            result = subprocess.run(
                ['python3', file_path],
                capture_output=True,
                text=True,
                timeout=30,  # 30 second timeout
                cwd=base_path
            )

            return jsonify({
                'success': True,
                'stdout': result.stdout,
                'stderr': result.stderr,
                'returncode': result.returncode
            })

        except subprocess.TimeoutExpired:
            return jsonify({'error': 'Script execution timeout (30 seconds)'}), 408
        except Exception as e:
            return jsonify({'error': f'Execution error: {str(e)}'}), 500

    except Exception as e:
        print(f"Error in run-script endpoint: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/chat', methods=['POST'])
def chat():
    """Handle chatbot conversations using Claude AI"""
    try:
        data = request.get_json()
        message = data.get('message', '')
        project_id = data.get('project_id')
        session_id = data.get('session_id', 'default')

        # Find the project
        project = next((p for p in PROJECTS if p['id'] == project_id), None)
        if not project:
            return jsonify({
                'response': 'Project not found. Please select a valid project.'
            })

        # Check if this is the Zebra Project and initialize RAG lazily
        if project_id == 'zebra-project':
            try:
                print(f"Using Zebra RAG for query: {message}")

                # Lazy load Zebra RAG
                rag = get_zebra_rag()

                # Query the Zebra RAG system
                recommendation = rag.recommend_printer(
                    requirements=message,
                    n_results=5
                )

                # Extract response text
                if 'llm_response' in recommendation:
                    response_text = recommendation['llm_response']
                elif 'explanation' in recommendation:
                    response_text = recommendation['explanation']
                else:
                    # Fallback: format results manually
                    results = recommendation.get('results', [])
                    if results:
                        response_text = f"Found {len(results)} printer(s):\n\n"
                        for i, printer in enumerate(results[:3], 1):
                            response_text += f"{i}. {printer.get('model', 'Unknown')}\n"
                            response_text += f"   {printer.get('text', '')[:200]}...\n\n"
                    else:
                        response_text = "No printers found matching your requirements."

                return jsonify({
                    'response': response_text,
                    'session_id': session_id,
                    'zebra_query': True,
                    'metadata': {
                        'printers_found': len(recommendation.get('results', []))
                    }
                })

            except Exception as e:
                print(f"Error querying Zebra RAG: {str(e)}")
                import traceback
                traceback.print_exc()
                return jsonify({
                    'response': f'Error querying Zebra printer database: {str(e)}'
                }), 500

        # Check if this is the Archive project and initialize lazily
        if project_id == 'gen-ai-agent':
            try:
                print(f"Using Archive query engine for query: {message}")

                # Lazy load Archive query engine
                query_engine, llm = get_archive_engine()

                # Query the Archive vector database
                results = query_engine.query(message)

                # Generate answer using Archive LLM
                response = llm.generate_answer(results["context"], message)

                # Return only the answer (matching interactive mode behavior)
                return jsonify({
                    'response': response['answer'],
                    'session_id': session_id,
                    'archive_query': True,
                    'metadata': {
                        'sheets_retrieved': len(results['structure_results']),
                        'rows_retrieved': len(results['content_results']),
                        'model': response['model'],
                        'tokens': response['token_usage'],
                        'backend': response.get('backend', 'unknown')
                    }
                })

            except Exception as e:
                print(f"Error querying Archive: {str(e)}")
                return jsonify({
                    'response': f'Error querying Archive database: {str(e)}\n\nPlease ensure the database has been built using the build command.'
                }), 500

        # Check if Anthropic client is initialized for non-Archive projects
        if not client:
            return jsonify({
                'response': 'Anthropic API is not configured. Please add your ANTHROPIC_API_KEY to the .env file.'
            }), 500

        # Get project context
        base_path = os.path.join(os.path.dirname(__file__), project['path'])
        project_files = []
        project_description_content = ""
        file_contents = {}

        # Helper function to read file content safely
        def read_file_safely(file_path, max_size=10000):
            """Read file content with size limit"""
            try:
                # Skip binary files
                binary_extensions = ['.png', '.jpg', '.jpeg', '.gif', '.pdf', '.zip', '.tar', '.gz',
                                   '.exe', '.bin', '.so', '.dylib', '.dll', '.pyc', '.pyo']
                if any(file_path.lower().endswith(ext) for ext in binary_extensions):
                    return None

                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read(max_size)
                    if len(content) >= max_size:
                        content += "\n...[truncated - file too large]"
                    return content
            except (UnicodeDecodeError, PermissionError, FileNotFoundError):
                return None
            except Exception as e:
                print(f"Error reading file {file_path}: {str(e)}")
                return None

        if os.path.exists(base_path):
            try:
                items = os.listdir(base_path)
                for item in items:
                    if not item.startswith('.'):
                        item_path = os.path.join(base_path, item)
                        is_dir = os.path.isdir(item_path)
                        project_files.append({
                            'name': item,
                            'type': 'directory' if is_dir else 'file'
                        })

                        # Read file contents for text files (not directories)
                        if not is_dir:
                            content = read_file_safely(item_path)
                            if content:
                                file_contents[item] = content

                # Look for description files (README.md, description.txt, DESCRIPTION.md, etc.)
                description_files = ['README.md', 'readme.md', 'README.txt', 'readme.txt',
                                   'DESCRIPTION.md', 'description.md', 'DESCRIPTION.txt', 'description.txt',
                                   'INFO.md', 'info.md', 'INFO.txt', 'info.txt']

                for desc_file in description_files:
                    desc_path = os.path.join(base_path, desc_file)
                    if os.path.exists(desc_path) and os.path.isfile(desc_path):
                        try:
                            with open(desc_path, 'r', encoding='utf-8') as f:
                                project_description_content = f.read()
                                # Limit to first 3000 characters to avoid token limits
                                if len(project_description_content) > 3000:
                                    project_description_content = project_description_content[:3000] + "\n...[truncated]"
                                break
                        except Exception as e:
                            print(f"Error reading description file {desc_file}: {str(e)}")
                            pass
            except Exception:
                pass

        # Initialize conversation history for this session if not exists
        if session_id not in conversation_histories:
            conversation_histories[session_id] = []

        # Build system prompt with project context
        description_section = ""
        if project_description_content:
            description_section = f"\n\nProject Documentation:\n{project_description_content}\n"

        # Build file contents section
        file_contents_section = ""
        if file_contents:
            file_contents_section = "\n\nFile Contents:\n"
            for filename, content in file_contents.items():
                file_contents_section += f"\n--- {filename} ---\n{content}\n"

        system_prompt = f"""You are a helpful AI assistant for the project "{project['name']}".
Project description: {project['description']}
Project location: {project['path']}
{description_section}
Available files and directories in this project:
{json.dumps(project_files, indent=2) if project_files else 'No files found or directory not accessible.'}
{file_contents_section}

You have access to the actual file contents above. You can:
- Understand the project structure and purpose
- Explain what the project does based on the documentation and code
- Answer specific questions about the code
- Provide guidance on development tasks
- Explain concepts and features
- Debug issues and suggest improvements
- RUN PYTHON SCRIPTS - When the user asks to run a file, respond with: RUN_SCRIPT:filename.py
- General programming assistance

IMPORTANT: When the user asks to run/execute a Python file, respond ONLY with:
RUN_SCRIPT:filename.py

For example:
- User: "run main.py" -> You respond: RUN_SCRIPT:main.py
- User: "execute test.py" -> You respond: RUN_SCRIPT:test.py

When referencing code, be specific about which file you're talking about.
Be conversational, helpful, and concise. Format code with proper markdown when needed."""

        # Add user message to conversation history
        conversation_histories[session_id].append({
            "role": "user",
            "content": message
        })

        # Keep only last 10 messages to avoid token limits
        if len(conversation_histories[session_id]) > 20:
            conversation_histories[session_id] = conversation_histories[session_id][-20:]

        # Call Claude AI
        response = client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=2048,
            system=system_prompt,
            messages=conversation_histories[session_id]
        )

        # Extract assistant response
        assistant_message = response.content[0].text

        # Check if Claude wants to run a script
        script_output = None
        if assistant_message.startswith('RUN_SCRIPT:'):
            filename = assistant_message.replace('RUN_SCRIPT:', '').strip()

            # Execute the script
            file_path = os.path.join(base_path, filename)
            if os.path.exists(file_path) and filename.endswith('.py'):
                try:
                    result = subprocess.run(
                        ['python3', file_path],
                        capture_output=True,
                        text=True,
                        timeout=30,
                        cwd=base_path
                    )

                    script_output = {
                        'filename': filename,
                        'stdout': result.stdout,
                        'stderr': result.stderr,
                        'returncode': result.returncode
                    }

                    # Update assistant message to be more conversational
                    assistant_message = f"Running {filename}...\n\nOutput:\n```\n{result.stdout}\n```"
                    if result.stderr:
                        assistant_message += f"\n\nErrors:\n```\n{result.stderr}\n```"

                except subprocess.TimeoutExpired:
                    assistant_message = f"Script {filename} execution timed out (30 seconds limit)."
                except Exception as e:
                    assistant_message = f"Error executing {filename}: {str(e)}"
            else:
                assistant_message = f"Could not find or execute {filename}. Please make sure it's a valid Python file in the project."

        # Add assistant response to conversation history
        conversation_histories[session_id].append({
            "role": "assistant",
            "content": assistant_message
        })

        return jsonify({
            'response': assistant_message,
            'session_id': session_id,
            'script_output': script_output
        })

    except anthropic.APIError as e:
        print(f"Anthropic API error: {str(e)}")
        return jsonify({
            'response': f'Sorry, there was an error with the AI service: {str(e)}'
        }), 500
    except Exception as e:
        print(f"Error in chat endpoint: {str(e)}")
        return jsonify({
            'response': f'Sorry, I encountered an error: {str(e)}'
        }), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)
