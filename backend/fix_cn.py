import re
with open("/home/adhi/Adhii/OneForAll/frontend/src/app/page.tsx", "r") as f:
    page = f.read()

# Target and delete the local cn function
old_cn = '''function cn(...classes: (string | undefined)[]) {
  return classes.filter(Boolean).join(" ");
}'''

if old_cn in page:
    page = page.replace(old_cn, "")
else:
    print("Could not find local cn function")

with open("/home/adhi/Adhii/OneForAll/frontend/src/app/page.tsx", "w") as f:
    f.write(page)
