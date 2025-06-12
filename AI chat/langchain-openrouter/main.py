import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain.memory import ConversationBufferMemory
from langchain.chains import ConversationChain
from langchain.prompts import PromptTemplate
from langchain.callbacks import StreamingStdOutCallbackHandler

def main():
    # Load environment variables
    load_dotenv()
    
    # Get API key from environment
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        print("Error: OPENROUTER_API_KEY not found in environment variables")
        print("Please create a .env file with your OpenRouter API key")
        return
    
    # Initialize the chat model
    llm = ChatOpenAI(
        api_key=api_key,
        base_url="https://openrouter.ai/api/v1",
        model="deepseek/deepseek-chat-v3-0324:free",
        default_headers={
            "HTTP-Referer": "http://localhost:8000",
            "X-Title": "LangChain OpenRouter Chat"
        },
        streaming=True,
        callbacks=[StreamingStdOutCallbackHandler()]
    )
    
    # Initialize conversation memory
    memory = ConversationBufferMemory()
    
    # Create conversation chain
    conversation = ConversationChain(
        llm=llm,
        memory=memory,
        verbose=True  # This will show the prompt being sent to the LLM
    )
    
    print("\nWelcome to LangChain OpenRouter Chat!")
    print("Type 'quit' to exit\n")
    
    # Main chat loop
    while True:
        # Get user input
        user_input = input("You: ").strip()
        
        if user_input.lower() == 'quit':
            print("\nGoodbye!")
            break
        
        try:
            # Get response using the conversation chain
            response = conversation.predict(input=user_input)
            print("\n")  # Add a newline after the streamed response
            
        except Exception as e:
            print(f"\nError: {str(e)}\n")

if __name__ == "__main__":
    main()