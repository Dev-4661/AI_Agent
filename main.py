import sys
import os

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))

from src.chatbot import CompanyChatbot

def main():
    """Main function to run the company chatbot"""
    print("🤖 Welcome to the Company Information Chatbot!")
    print("=" * 50)
    print("I can help you find information about any company.")
    print("Type 'help' for more information or 'exit' to quit.")
    print("=" * 50)
    
    try:
        # Initialize chatbot
        chatbot = CompanyChatbot()
        print("✅ Chatbot initialized successfully!")
        print("\n💬 You can start asking questions about companies...\n")
        
        while True:
            try:
                # Get user input
                user_input = input("You: ").strip()
                
                if not user_input:
                    continue
                
                # Get chatbot response
                response = chatbot.chat(user_input)
                print(f"\n🤖 Chatbot: {response}\n")
                
                # Check if user wants to exit
                if user_input.lower() in ['exit', 'quit', 'bye']:
                    break
                    
            except KeyboardInterrupt:
                print("\n\n👋 Goodbye! Thank you for using the Company Chatbot!")
                break
            except Exception as e:
                print(f"\n❌ Error: {str(e)}")
                print("Please try again.\n")
                
    except Exception as e:
        print(f"❌ Failed to initialize chatbot: {str(e)}")
        print("\n📝 Please check your configuration:")
        print("1. Make sure you have created a .env file with your API keys")
        print("2. Ensure all required packages are installed (run: pip install -r requirements.txt)")
        print("3. Verify your Google API key and Tavily API key are valid")
        print("4. Get Google API key from: https://aistudio.google.com/")
        print("5. Get Tavily API key from: https://tavily.com/")

if __name__ == "__main__":
    main()
