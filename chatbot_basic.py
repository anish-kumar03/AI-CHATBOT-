import openai
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class FactualChatbot:
    def __init__(self):
        # Set up OpenAI API key
        openai.api_key = os.getenv('OPENAI_API_KEY')
    
    def get_response(self, question):
        try:
            response = openai.ChatCompletion.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are a helpful assistant that provides accurate factual information. Always cite your sources when possible and admit if you're not certain about something."},
                    {"role": "user", "content": question}
                ],
                max_tokens=500,
                temperature=0.3  # Lower temperature for more factual responses
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"Sorry, I encountered an error: {str(e)}"

# Example usage
if __name__ == "__main__":
    chatbot = FactualChatbot()
    
    while True:
        question = input("Ask me anything (or type 'quit' to exit): ")
        if question.lower() == 'quit':
            break
        
        answer = chatbot.get_response(question)
        print(f"Answer: {answer}\n")