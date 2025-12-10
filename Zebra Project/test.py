import anthropic
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from centralized .env file in Internal-Projects directory
env_path = Path(__file__).resolve().parents[1] / '.env'
load_dotenv(dotenv_path=env_path)
client = anthropic.Anthropic()
models = client.models.list()
print([m.id for m in models.data])