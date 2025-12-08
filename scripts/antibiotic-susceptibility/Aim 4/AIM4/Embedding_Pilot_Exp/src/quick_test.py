import requests
import json

my_key = "5f57674c921c459aa144c7e35360a735"
my_question = """First, state what specific model of LLM you are based on.  Next, answer the following hard physics question.
What is the difference between the cosmological constant and the vacuum energy?"""

# Common Headers (Used for all models)
headers = {'Ocp-Apim-Subscription-Key': my_key, 'Content-Type': 'application/json'}

# url = "https://apim.stanfordhealthcare.org/openai-eastus2/deployments/o3-mini/chat/completions?api-version=2025-01-01-preview" 
# payload = json.dumps({
#     "model": "o3-mini", 
#     "messages": [{"role": "user", "content": my_question}]
# })


# url = "https://apim.stanfordhealthcare.org/gemini-25-pro/gemini-25-pro"
# payload = json.dumps({
#     "contents": [{"role": "user", "parts": [{"text": my_question}]}]
# })
url = "https://apim.stanfordhealthcare.org/gcp-gem20flash-fa/apim-gcp-gem20flash-fa" 
payload = json.dumps({
    "contents": {"role": "user", "parts": {"text": my_question}}, 
    # "safety_settings": {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"}, 
    # "generation_config": {"temperature": 0.2, "topP": 0.8, "topK": 40}
})
response = requests.request("POST", url, headers=headers, data=payload) 
response_data = response.json()

# Extract the complete answer by concatenating all text parts
full_answer = ""
for response_obj in response_data:
    if "candidates" in response_obj:
        for candidate in response_obj["candidates"]:
            if "content" in candidate and "parts" in candidate["content"]:
                for part in candidate["content"]["parts"]:
                    if "text" in part:
                        full_answer += part["text"]

print("Complete Answer:")
print(full_answer)

# response = requests.request("POST", url, headers=headers, data=payload)
# message_content = response.json()["choices"][0]["message"]["content"]
# print(message_content)