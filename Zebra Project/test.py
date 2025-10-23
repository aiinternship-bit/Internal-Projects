import anthropic
from dotenv import load_dotenv
load_dotenv()
client = anthropic.Anthropic()
models = client.models.list()
print([m.id for m in models.data])