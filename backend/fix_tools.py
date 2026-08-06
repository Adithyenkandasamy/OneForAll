with open("/home/adhi/Adhii/OneForAll/backend/app/agents/executive/service.py", "r") as f:
    code = f.read()

header = 'from app.shared.llm.base import ToolDefinition\n'
code = code.replace("from app.shared.llm.groq import GroqProvider", "from app.shared.llm.groq import GroqProvider\n" + header)

old_def = '''    def _get_domain_tools(self) -> list[dict]:
        return [
            {
                "type": "function",
                "function": {
                    "name": "get_inventory_health",
                    "description": "Get the current overall inventory health score and risk distribution.",
                    "parameters": {"type": "object", "properties": {}}
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "get_inventory_dashboard",
                    "description": "Get the top critical materials, supplier stats, and health overview.",
                    "parameters": {"type": "object", "properties": {}}
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "get_inventory_analytics",
                    "description": "Get detailed ABC analysis, dead stock, and fast/slow movers.",
                    "parameters": {"type": "object", "properties": {}}
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "search_inventory_materials",
                    "description": "Search for specific materials or get all materials if query is empty.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "query": {"type": "string", "description": "Search term (e.g. MAT or Steel). Leave empty for all."}
                        }
                    }
                }
            }
        ]'''

new_def = '''    def _get_domain_tools(self) -> list[ToolDefinition]:
        return [
            ToolDefinition(
                name="get_inventory_health",
                description="Get the current overall inventory health score and risk distribution.",
                input_schema={"type": "object", "properties": {}}
            ),
            ToolDefinition(
                name="get_inventory_dashboard",
                description="Get the top critical materials, supplier stats, and health overview.",
                input_schema={"type": "object", "properties": {}}
            ),
            ToolDefinition(
                name="get_inventory_analytics",
                description="Get detailed ABC analysis, dead stock, and fast/slow movers.",
                input_schema={"type": "object", "properties": {}}
            ),
            ToolDefinition(
                name="search_inventory_materials",
                description="Search for specific materials or get all materials if query is empty.",
                input_schema={
                    "type": "object",
                    "properties": {
                        "query": {"type": "string", "description": "Search term (e.g. MAT). Leave empty for all."}
                    }
                }
            )
        ]'''

code = code.replace(old_def, new_def)

with open("/home/adhi/Adhii/OneForAll/backend/app/agents/executive/service.py", "w") as f:
    f.write(code)

