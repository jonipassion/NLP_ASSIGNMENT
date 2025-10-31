from openai import OpenAI

client = OpenAI()

def chat(prompt, model="gpt-4o-mini"):
    """Send a prompt to the GPT model and return its response."""
    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": "You are a helpful AI assistant."},
            {"role": "user", "content": prompt}
        ]
    )
    return response.choices[0].message.content

# Example usage
if __name__ == "__main__":
    while True:
        user_input = input("You: ")
        if user_input.lower() in {"exit", "quit"}:
            print("Goodbye!")
            break
        reply = chat(user_input)
        print("AI:", reply)
