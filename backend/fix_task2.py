with open("/home/adhi/.gemini/antigravity/brain/829584aa-e4d2-415f-9b83-a8a3de33f807/task.md", "r") as f:
    text = f.read()

text = text.replace("- [ ] Build the Background 10-second Scheduler to fetch the external sensor telemetry stream.", "- [x] Build the Background 10-second Scheduler to fetch the external sensor telemetry stream.")
text = text.replace("- [ ] Develop deterministic Rule Engine to classify sensory values (Vibe, Temp) into Health Risk %.", "- [x] Develop deterministic Rule Engine to classify sensory values (Vibe, Temp) into Health Risk %.")

with open("/home/adhi/.gemini/antigravity/brain/829584aa-e4d2-415f-9b83-a8a3de33f807/task.md", "w") as f:
    f.write(text)
