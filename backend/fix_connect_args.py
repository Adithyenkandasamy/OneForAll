with open("/home/adhi/Adhii/OneForAll/backend/app/database/session.py", "r") as f:
    text = f.read()

text = text.replace(
    '{"prepared_statement_cache_size": 0}',
    '{"statement_cache_size": 0, "prepared_statement_cache_size": 0}'
)

with open("/home/adhi/Adhii/OneForAll/backend/app/database/session.py", "w") as f:
    f.write(text)
