with open("/home/adhi/Adhii/OneForAll/frontend/src/app/inventory/page.tsx", "r") as f:
    page = f.read()

old_filter = 'return s.includes("critical") || s.includes("high") || i.current_stock <= i.minimum_stock;'
new_filter = 'return s.includes("critical") || s.includes("high");'

page = page.replace(old_filter, new_filter)

with open("/home/adhi/Adhii/OneForAll/frontend/src/app/inventory/page.tsx", "w") as f:
    f.write(page)
