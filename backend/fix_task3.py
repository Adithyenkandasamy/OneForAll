with open("/home/adhi/.gemini/antigravity/brain/829584aa-e4d2-415f-9b83-a8a3de33f807/task.md", "r") as f:
    text = f.read()

text = text.replace("- [ ] Instantiate the standalone Quality AI explainer agent.", "- [x] Instantiate the standalone Quality AI explainer agent.")
text = text.replace("- [ ] Wire up dashboard routes to expose metrics to Next.js.", "- [x] Wire up dashboard routes to expose metrics to Next.js.")

with open("/home/adhi/.gemini/antigravity/brain/829584aa-e4d2-415f-9b83-a8a3de33f807/task.md", "w") as f:
    f.write(text)
