# import os

# key = os.getenv("OPENAI_API_KEY")
# if key:
#     print("API key is set correctly!")
# else:
#     print("API key NOT found.")

# import os
# from openai import OpenAI

# # Load your API key from environment variable
# api_key = os.getenv("OPENAI_API_KEY")

# if not api_key:
#     print("❌ API key not found. Please set OPENAI_API_KEY first.")
#     exit()

# client = OpenAI(api_key=api_key)

# try:
#     response = client.chat.completions.create(
#         model="gpt-4o-mini",
#         messages=[
#             {"role": "system", "content": "You are a helpful assistant."},
#             {"role": "user", "content": "Say 'Hello! My API key works!' if this request is successful."}
#         ]
#     )

#     print("✅ Success! Response from GPT:")
#     print(response.choices[0].message.content)

# except Exception as e:
#     print("❌ Something went wrong:")
#     print(e)

# client = OpenAI()

# models = client.models.list()

# print("Available models:")
# for model in models.data:
#     print(model.id)

from openai import OpenAI

client = OpenAI()

def chat_with_memory():
    """Simple terminal chat with conversation memory."""
    messages = [
        {"role": "system", "content": "You are a friendly and helpful AI assistant."}
    ]

    print("🤖 Chat started! Type 'exit' or 'quit' to stop.\n")

    while True:
        user_input = input("You: ").strip()
        if user_input.lower() in {"exit", "quit"}:
            print("Goodbye! 👋")
            break

        # Add user message
        messages.append({"role": "user", "content": user_input})

        # Send the full conversation so far
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages
        )

        # Get assistant's reply
        reply = response.choices[0].message.content
        print(f"AI: {reply}\n")

        # Add assistant message to memory
        messages.append({"role": "assistant", "content": reply})

if __name__ == "__main__":
    chat_with_memory()
