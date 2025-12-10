# Internal Projects

A collection of AI-powered projects and tools for various applications.

## Projects

- **AI-Interns** - Modern Flask-based chatbot platform with Claude AI integration, featuring:
  - Multi-project chatbot interface with persistent conversations
  - SQLite database for conversation history
  - Custom UI with ACL Digital branding
  - Real-time chat with markdown support
  - Conversation management (create, switch, delete)
  - Auto-generated conversation titles from AI responses

- **GEN AI Agent / Archive** - RAG system using Milvus vector database
  - Reads and processes XLSX files for knowledge base
  - Supports both local files and Google Cloud Storage buckets
  - Cloud Run ready with GCS integration

- **Zebra Project** - Printer recommendation system with ChromaDB
- **AI Initiatives** - React Native mobile app development

## Setup

### 1. Environment Configuration

All projects share a centralized `.env` file located in this directory (`Internal-Projects/.env`).

**Quick Start:**
```bash
# Copy the example file
cp .env.example .env

# Edit with your API keys
nano .env
```

**Required API Keys:**
- `ANTHROPIC_API_KEY` - Get from https://console.anthropic.com/

**Optional API Keys** (depending on which projects you use):
- `OPENAI_API_KEY` - For OpenAI models
- `GOOGLE_API_KEY` - For Google services
- `LANGCHAIN_API_KEY` - For LangSmith tracing

### 2. Virtual Environment

A shared virtual environment is located in the Internal-Projects directory:
```bash
# From the Internal-Projects directory
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

All projects use this shared virtual environment automatically via their startup scripts.

### 3. Running Projects

#### Option A: Local Development

Each project can be run independently:

**AI-Interns (Chatbot):**
```bash
cd AI-Interns
./start_app.sh
# Or: python app.py
```

**GEN AI Agent:**
```bash
cd "GEN AI Agent/Archive"
python main.py
```

**Zebra Project:**
```bash
cd "Zebra Project"
python src/printer_rag.py
```

#### Option B: Docker Deployment

**Using Docker Compose (Recommended):**
```bash
# Make sure .env file exists with your API keys
docker-compose up -d

# View logs
docker-compose logs -f

# Stop the application
docker-compose down
```

**Using Docker directly:**
```bash
# Build the image
docker build -t ai-interns .

# Run the container
docker run -d \
  -p 5001:5001 \
  -e ANTHROPIC_API_KEY=your_api_key_here \
  -v $(pwd)/AI-Interns/conversations.db:/app/AI-Interns/conversations.db \
  --name ai-interns-app \
  ai-interns

# View logs
docker logs -f ai-interns-app

# Stop the container
docker stop ai-interns-app
docker rm ai-interns-app
```

**Access the application:**
- Open your browser to `http://localhost:5001`

## Directory Structure

```
Internal-Projects/
├── .env                    # Centralized environment variables
├── .env.example           # Template for environment setup
├── requirements.txt       # Shared dependencies
├── Dockerfile             # Docker configuration
├── docker-compose.yml     # Docker Compose orchestration
├── .dockerignore          # Docker build exclusions
├── venv/                  # Shared virtual environment
├── AI-Interns/            # Flask chatbot application
│   ├── app.py            # Main Flask app
│   ├── conversations.db  # SQLite database (created on first run)
│   ├── static/           # CSS, JS, images
│   └── templates/        # HTML templates
├── GEN AI Agent/          # RAG system
│   └── Archive/          # Milvus vector database
├── Zebra Project/         # Printer recommendation
│   └── chroma_db/        # ChromaDB vector database
└── AI Initiatives/        # Mobile app development
```

## Portability

All paths in the codebase are **relative** and dynamically resolved, making the entire project structure portable across different systems. You can move the `Internal-Projects` directory anywhere, and all projects will continue to work without modification.

The centralized `.env` file is automatically discovered by each project using relative path resolution from the script location.

## Security

- Never commit the `.env` file to version control
- The `.gitignore` is already configured to exclude it
- Use `.env.example` as a template for other developers
