from chat_memory import chat_with_memory
from interactive_quiz import quiz_flow

def main():
    print("=== GPT Tools Menu ===")
    while True:
        print("\n1. Chat with memory\n2. Take interactive quiz\n3. Exit")
        choice = input("Select an option (1/2/3): ").strip()
        if choice == "1":
            chat_with_memory()
        elif choice == "2":
            quiz_flow()
        elif choice == "3":
            print("Goodbye!")
            break
        else:
            print("Invalid choice.")

if __name__ == "__main__":
    main()
