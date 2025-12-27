
import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv('GEMINI_API_KEY')
if not api_key:
    print("❌ API Key not found.")
    exit()

genai.configure(api_key=api_key)
model = genai.GenerativeModel('gemini-2.0-flash')

print("Testing simple generation to check quota...")
try:
    response = model.generate_content("Hello! This is a quota test.")
    print(f"✅ Success! AI responded: {response.text}")
except Exception as e:
    print(f"❌ Error Detail: {str(e)}")
    if "429" in str(e):
        print("\n💡 This is a Rate Limit error. Even with a subscription, you might need to enable 'Pay-as-you-go' in AI Studio for higher limits.")
    elif "quota" in str(e).lower():
        print("\n💡 Quota reached. Please check: https://aistudio.google.com/app/plan_billing")
