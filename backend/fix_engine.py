with open("/home/adhi/Adhii/OneForAll/backend/app/database/session.py", "r") as f:
    text = f.read()

text = text.replace(
    'connect_args = {"check_same_thread": False} if url.startswith("sqlite") else {}',
    'connect_args = {"check_same_thread": False} if url.startswith("sqlite") else {"prepared_statement_cache_size": 0}'
)

with open("/home/adhi/Adhii/OneForAll/backend/app/database/session.py", "w") as f:
    f.write(text)
