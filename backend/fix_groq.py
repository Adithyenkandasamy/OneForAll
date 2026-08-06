with open("/home/adhi/Adhii/OneForAll/backend/app/agents/quality/llm/agent.py", "r") as f:
    text = f.read()

text = text.replace("settings.GROQ_CENTRAL_API_KEY", "settings.groq_central_api_key")

with open("/home/adhi/Adhii/OneForAll/backend/app/agents/quality/llm/agent.py", "w") as f:
    f.write(text)
