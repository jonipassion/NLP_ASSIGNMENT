import os
import json
from datetime import datetime
from openai import OpenAI

client = OpenAI()

CONVO_DIR = "conversations"
os.makedirs(CONVO_DIR, exist_ok=True)

def save_conversation(messages, filename=None):
    """Save conversation to JSON file."""
    if not filename:
        timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S-%f')
        filename = os.path.join(CONVO_DIR, f"chat_{timestamp}.json")
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(messages, f, indent=2, ensure_ascii=False)
    print(f"Conversation saved to {filename}")

def list_conversations():
    """Return list of saved conversation files."""
    files = [f for f in os.listdir(CONVO_DIR) if f.endswith(".json")]
    if not files:
        print("No saved conversations found.")
        return []
    print("Saved conversations:")
    for i, file in enumerate(files, 1):
        print(f"{i}. {file}")
    return files

def load_conversation():
    """Load a conversation from file or start new."""
    files = list_conversations()
    if not files:
        return [{"role": "system", "content": "You are a friendly and helpful AI assistant."}]
    
    choice = input("Enter number to load, or Enter for new chat: ").strip()
    if not choice:
        return [{"role": "system", "content": "You are a friendly and helpful AI assistant."}]
    
    try:
        idx = int(choice) - 1
        if idx < 0 or idx >= len(files):
            raise IndexError
        filename = os.path.join(CONVO_DIR, files[idx])
        with open(filename, "r", encoding="utf-8") as f:
            messages = json.load(f)
        print(f"Loaded conversation: {files[idx]}")
        return messages
    except (ValueError, IndexError):
        print("Invalid choice. Starting new chat.")
        return [{"role": "system", "content": "You are a friendly and helpful AI assistant."}]

def chat_with_memory():
    """Main chat loop with save/load functionality."""
    messages = load_conversation()
    print("\nChat started! Type '/save', '/exit', '/reset', or '/list' anytime.\n")
    
    while True:
        user_input = input("You: ").strip()
        
        if user_input.lower() in {"/exit", "exit", "quit"}:
            save_conversation(messages)
            print("Goodbye!")
            break
        elif user_input.lower() == "/save":
            save_conversation(messages)
            continue
        elif user_input.lower() == "/reset":
            print("Conversation reset.")
            messages = [{"role": "system", "content": "You are a friendly and helpful AI assistant."}]
            continue
        elif user_input.lower() == "/list":
            list_conversations()
            continue

        # Append user message
        messages.append({"role": "user", "content": user_input})
        
        # Call OpenAI API
        try:
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=messages
            )
            reply = response.choices[0].message.content
        except Exception as e:
            reply = f"Error: {e}"
        
        # Print and store AI response
        print(f"AI: {reply}\n")
        messages.append({"role": "assistant", "content": reply})

if __name__ == "__main__":
    chat_with_memory()
