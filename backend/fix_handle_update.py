with open("/home/adhi/Adhii/OneForAll/frontend/src/app/inventory/page.tsx", "r") as f:
    page = f.read()

import re

# We simply want to remove the Optimistic update block inside handleUpdate
# and insert `await loadInventory(true);` just before `setEditingCell(null);`
old_content = '''      // Optimistic update in UI
      setInventory(prev => prev.map(item => {
        if (item.sku === sku) {
          if (editingCell.column === 'current_stock') {
            return { ...item, current_stock: Number(editValue) };
          }
          if (editingCell.column === 'ai_risk_level') {
            return { ...item, risk_level: editValue };
          }
        }
        return item;
      }));

      setEditingCell(null);'''

new_content = '''      // Trigger dynamic refresh instantly!
      await loadInventory(true);
      
      setEditingCell(null);'''

page = page.replace(old_content, new_content)

with open("/home/adhi/Adhii/OneForAll/frontend/src/app/inventory/page.tsx", "w") as f:
    f.write(page)
