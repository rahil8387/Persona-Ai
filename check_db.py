import database

print("🔍 Checking Persona AI Database Logs...\n")

try:
    # Fetch all logs from the database file
    logs = database.get_all_chats()
    
    if not logs:
        print("📁 Database is working perfectly, but it is currently empty.")
        print("Go chat with Persona AI first, then run this script again!")
    else:
        print(f"✅ Success! Found {len(logs)} conversation(s) stored:\n")
        for index, row in enumerate(logs, 1):
            persona, user_msg, ai_res, timestamp = row
            print(f"--- Chat #{index} [{timestamp}] ---")
            print(f"Role: {persona}")
            print(f"You: {user_msg}")
            print(f"AI: {ai_res}\n")
            
except Exception as e:
    print(f"❌ Database Error: {e}")