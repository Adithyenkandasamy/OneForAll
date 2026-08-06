with open("/home/adhi/.gemini/antigravity/brain/829584aa-e4d2-415f-9b83-a8a3de33f807/task.md", "r") as f:
    text = f.read()

text = text.replace("- [ ] Scaffold `app/agents/quality` modular directory structure (api, services, tools).", "- [x] Scaffold `app/agents/quality` modular directory structure (api, services, tools).")
text = text.replace("- [ ] Implement V2 Pydantic schemas mapping the Mockaroo JSON specification.", "- [x] Implement V2 Pydantic schemas mapping the Mockaroo JSON specification.")
text = text.replace("- [ ] Create Async SQLAlchemy tables for telemetry persistence.", "- [x] Create Async SQLAlchemy tables for telemetry persistence.")

with open("/home/adhi/.gemini/antigravity/brain/829584aa-e4d2-415f-9b83-a8a3de33f807/task.md", "w") as f:
    f.write(text)
