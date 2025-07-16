import requests
from prompt import format_prompt

def query_lmstudio(context, user_query):
    api_url = "http://192.168.1.121:1234/v1/chat/completions"

    prompt = format_prompt(context, user_query)

    headers = {"Content-Type": "application/json"}
    payload = {
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": 3500,
        "temperature": 0.9,
        "stream": False
    }

    try:
        response = requests.post(api_url, json=payload, headers=headers, timeout=30)
        response.raise_for_status()
        return response.json()['choices'][0]['message']['content']
    except Exception as e:
        return f"Error contacting LLM API: {e}"
