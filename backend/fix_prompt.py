import re
with open("/home/adhi/Adhii/OneForAll/backend/app/agents/inventory/prompt.py", "r") as f:
    prompt = f.read()

rule_9 = "9. You may only call the tools that were provided to you."
rule_10 = """9. You may only call the tools that were provided to you.
10. INTERACTION STYLE: If the user simply says a greeting like 'Hello' or 'Hi', respond naturally and professionally (e.g. "Hello! How can I assist you with the inventory today?"). DO NOT dump or summarize the [STRUCTURED INVENTORY DATA] unless the user explicitly asks for an update, status, or report."""

prompt = prompt.replace(rule_9, rule_10)

with open("/home/adhi/Adhii/OneForAll/backend/app/agents/inventory/prompt.py", "w") as f:
    f.write(prompt)

print("Done")
