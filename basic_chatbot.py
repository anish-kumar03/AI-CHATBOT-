import openai
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class FactualChatbot:
    def __init__(self):
        # Initialize OpenAI client (using the newer v1+ syntax)
        self.client = openai.OpenAI(
            api_key=os.getenv('OPENAI_API_KEY')
        )
        
    def get_response(self, question):
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {
                        "role": "system",
                        "content": "You are a helpful assistant that provides accurate factual information. Always be honest about what you know and don't know. For recent events after your training data, suggest checking current sources."
                    },
                    {"role": "user", "content": question}
                ],
                max_tokens=500,
                temperature=0.2  # Lower temperature for more factual responses
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"Sorry, I encountered an error: {str(e)}"

def main():
    chatbot = FactualChatbot()
    
    print("🤖 Factual Chatbot - Ask me anything!")
    print("Type 'quit' to exit\n")
    
    while True:
        question = input("Your question: ")
        if question.lower() in ['quit', 'exit', 'bye']:
            print("Goodbye!")
            break
            
        print("Thinking...", end="")
        answer = chatbot.get_response(question)
        print(f"\n\nAnswer: {answer}\n")
        print("-" * 50)

if __name__ == "__main__":
    main()