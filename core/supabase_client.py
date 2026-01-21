import os
from dotenv import load_dotenv
from supabase import create_client, Client

load_dotenv()

url: str = os.environ.get("SUPABASE_URL")
key: str = os.environ.get("SUPABASE_KEY")

def get_supabase() -> Client:
    if not url or not key:
        raise ValueError("SUPABASE_URL or SUPABASE_KEY is not set in environment variables")
    return create_client(url, key)
