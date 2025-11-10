open ai chatgpt api call example:
curl https://api.openai.com/v1/chat/completions \
-H "Content-Type: application/json" \
-H "Authorization: Bearer sk-proj-1234567890" \
-d '{
    "model": "gpt-4o-mini",
    "messages": [
        {
            "role": "user",
            "content": "Hello, how are you?"
        }
    ]
}'
