import re
with open('src/app/inventory/page.tsx', 'r') as f:
    code = f.read()

# Replace frontend mappings for MaterialAnalysisDTO
code = code.replace('item.quantity', 'item.current_stock')
code = code.replace('i.quantity', 'i.current_stock')
code = code.replace('item.threshold', 'item.minimum_stock')
code = code.replace('i.threshold', 'i.minimum_stock')
code = code.replace('item.status', 'item.risk_level')
code = code.replace('i.status', 'i.risk_level')
code = code.replace('"Current Stock"', '"current_stock"')
code = code.replace("'Current Stock'", "'current_stock'")
code = code.replace('"AI Risk Level"', '"ai_risk_level"')
code = code.replace("'AI Risk Level'", "'ai_risk_level'")

with open('src/app/inventory/page.tsx', 'w') as f:
    f.write(code)
print("Done")
