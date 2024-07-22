import os
from dotenv import load_dotenv
load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
TYPESENSE_NODE = os.getenv("TYPESENSE_NODE")
TYPESENSE_API_KEY = os.getenv("TYPESENSE_API_KEY")