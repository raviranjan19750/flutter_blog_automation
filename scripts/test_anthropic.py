import os
import anthropic
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

def test_connection():
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key or "your-key-here" in api_key or "xxxx" in api_key:
        print("❌ Error: Please provide a valid ANTHROPIC_API_KEY in your .env file.")
        return

    client = anthropic.Anthropic(api_key=api_key)

    try:
        print("🚀 Sending test message to Claude...")
        message = client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=100,
            messages=[
                {"role": "user", "content": "Hello, Claude! Confirm you are receiving this message."}
            ]
        )
        print("✅ Connection successful!")
        print(f"Response: {message.content[0].text}")
    except Exception as e:
        print(f"❌ Connection failed: {str(e)}")

if __name__ == "__main__":
    test_connection()