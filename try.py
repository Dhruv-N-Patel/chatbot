import requests
import json

# Set up Groq API
GROQ_API_KEY = "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"
GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"

# Function to interact with Groq API
def get_groq_response(prompt):
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "model": "gpt-3.5-turbo",  # Ensure this model is available via Groq
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": 100,
        "temperature": 0.5
    }
    response = requests.post(GROQ_API_URL, headers=headers, data=json.dumps(data))
    if response.status_code == 200:
        response_data = response.json()
        return response_data["choices"][0]["message"]["content"]
    else:
        print(f"Error with Groq API: {response.status_code} - {response.text}")
        return "Sorry, there was an error processing your request."
