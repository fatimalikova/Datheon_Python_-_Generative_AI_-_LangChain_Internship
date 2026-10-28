from google import genai
from config import GOOGLE_API_KEY

client = genai.Client(api_key=GOOGLE_API_KEY)
for m in client.models.list():
    if "flash" in m.name:
        print(m.name)