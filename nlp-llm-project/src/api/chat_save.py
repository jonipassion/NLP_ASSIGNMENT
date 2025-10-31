# import os
# from datetime import datetime
# from openai import OpenAI

# client = OpenAI()

# def save_conversation(messages, filename):
#     """Save the conversation history to a text file."""
#     with open(filename, "w", encoding="utf-8") as f:
#         for msg in messages:
#             role = msg["role"].capitalize()
#             content = msg["content"]
#             f.write(f"{role}: {content}\n\n")
#     print(f"💾 Conversation saved to: {filename}")

# def chat_with_memory_and_save():
#     """Chat with GPT that remembers context and saves conversation."""
#     messages = [
#         {"role": "system", "content": "You are a friendly and helpful AI assistant."}
#     ]

#     # Create a timestamped filename for each chat
#     os.makedirs("conversations", exist_ok=True)
#     filename = f"conversations/chat_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.txt"

#     print("🤖 Chat started! Type 'exit' or 'quit' to stop.\n")

#     while True:
#         user_input = input("You: ").strip()
#         if user_input.lower() in {"exit", "quit"}:
#             save_conversation(messages, filename)
#             print("Goodbye! 👋")
#             break

#         # Add user message
#         messages.append({"role": "user", "content": user_input})

#         # Get GPT response
#         response = client.chat.completions.create(
#             model="gpt-4o-mini",
#             messages=messages
#         )

#         reply = response.choices[0].message.content
#         print(f"AI: {reply}\n")

#         # Save assistant response
#         messages.append({"role": "assistant", "content": reply})

# if __name__ == "__main__":
#     chat_with_memory_and_save()

import os
import json
from datetime import datetime
from openai import OpenAI

client = OpenAI()

CONVO_DIR = "conversations"
os.makedirs(CONVO_DIR, exist_ok=True)

def save_conversation(messages, filename):
    """Save conversation to JSON for easy reload."""
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(messages, f, indent=2, ensure_ascii=False)
    print(f"💾 Conversation saved to {filename}")

def load_conversation():
    """List available conversations and let user pick one to load."""
    files = [f for f in os.listdir(CONVO_DIR) if f.endswith(".json")]
    if not files:
        print("No saved conversations found. Starting a new one.\n")
        return [
            {"role": "system", "content": "You are a friendly and helpful AI assistant."}
        ]

    print("📁 Saved conversations:")
    for i, file in enumerate(files, 1):
        print(f"{i}. {file}")

    choice = input("\nEnter number to load, or press Enter for a new chat: ").strip()
    if not choice:
        return [
            {"role": "system", "content": "You are a friendly and helpful AI assistant."}
        ]

    try:
        idx = int(choice) - 1
        filename = os.path.join(CONVO_DIR, files[idx])
        with open(filename, "r", encoding="utf-8") as f:
            messages = json.load(f)
        print(f"✅ Loaded conversation: {files[idx]}\n")
        return messages
    except (ValueError, IndexError):
        print("❌ Invalid choice. Starting a new chat.\n")
        return [
            {"role": "system", "content": "You are a friendly and helpful AI assistant."}
        ]

def chat_with_reload():
    """Chat that can load previous memory and save progress."""
    messages = load_conversation()
    filename = os.path.join(CONVO_DIR, f"chat_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.json")

    print("🤖 Chat started! Type '/save', '/exit', or '/reset' anytime.\n")

    while True:
        user_input = input("You: ").strip()

        if user_input.lower() in {"/exit", "exit", "quit"}:
            save_conversation(messages, filename)
            print("👋 Goodbye!")
            break
        elif user_input.lower() in {"/save"}:
            save_conversation(messages, filename)
            continue
        elif user_input.lower() in {"/reset"}:
            print("🔄 Conversation reset.\n")
            messages = [
                {"role": "system", "content": "You are a friendly and helpful AI assistant."}
            ]
            continue

        # Add user message
        messages.append({"role": "user", "content": user_input})

        # Get GPT response
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages
        )

        reply = response.choices[0].message.content
        print(f"AI: {reply}\n")

        # Add assistant response to memory
        messages.append({"role": "assistant", "content": reply})

if __name__ == "__main__":
    chat_with_reload()
