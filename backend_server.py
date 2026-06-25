import time
import requests
import json
import sys
import firebase_admin
from firebase_admin import credentials, db

print("🔄 Booting up Persona AI Engine...", flush=True)

# Initialize Firebase Admin SDK
try:
    cred = credentials.Certificate("firebase_key.json")
    firebase_admin.initialize_app(cred, {
        'databaseURL': 'https://persona-ai-studio-6a1d5-default-rtdb.firebaseio.com/'
    })
    print("✅ Cloud Bridge Connection: SUCCESS!", flush=True)
except Exception as e:
    print(f"❌ Initialization failed: {e}", flush=True)
    sys.exit(1)

OLLAMA_URL = "http://localhost:11434/api/generate"
print("🔥 System Ready! Listening for cloud inputs every 2 seconds...\n", flush=True)

# Keep track of the last processed request timestamp to avoid repeating responses
last_processed_timestamp = 0

while True:
    try:
        # Fetch the current data from the user_request endpoint
        request_ref = db.reference('chat_pipeline/user_request')
        data = request_ref.get()

        if data and isinstance(data, dict):
            timestamp = data.get("timestamp", 0)
            
            # If this is a brand new request we haven't answered yet
            if timestamp > last_processed_timestamp:
                last_processed_timestamp = timestamp
                persona = data.get("persona", "General Assistant")
                user_message = data.get("message", "")

                print(f"📥 New message received for [{persona}]: '{user_message}'", flush=True)
                
                system_prompt = f"You are a helpful virtual companion acting as an expert {persona}. Answer clearly and naturally."
                full_prompt = f"{system_prompt}\n\nUser: {user_message}\nAI:"

                payload = {
                    "model": "llama3.2",
                    "prompt": full_prompt,
                    "stream": False
                }

                print("🧠 Local Llama 3.2 is processing text...", flush=True)
                response = requests.post(OLLAMA_URL, json=payload)
                ai_reply = response.json().get("response", "Processing error.")

                print(f"📤 Uploading response to Cloud: {ai_reply[:40]}...", flush=True)
                
                # Write response back to cloud
                db.reference('chat_pipeline/ai_response').set({
                    'text': ai_reply,
                    'timestamp': int(time.time() * 1000)
                })
                print("✨ Done! Awaiting next query...\n", flush=True)

    except Exception as loop_error:
        print(f"⚠️ Loop Warning: {loop_error}", flush=True)
        
    # Rest for 2 seconds before checking the database again to save CPU power
    time.sleep(2)