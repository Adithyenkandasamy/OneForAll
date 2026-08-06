with open("/home/adhi/Adhii/OneForAll/backend/app/mcp_servers/inventory_server.py", "r") as f:
    text = f.read()

old_load = '''def _load_data() -> pd.DataFrame:
    global df
    if df is None:
        records = ws.get_all_records()
        df = pd.DataFrame(records)
        df.columns = (
            df.columns.str.strip()
            .str.lower()
            .str.replace(" ", "_")
            .str.replace("-", "_")
        )
    return df'''

new_load = '''def _load_data() -> pd.DataFrame:
    global df
    # ALWAYS fetch fresh records since this acts as a real-time gateway!
    records = ws.get_all_records()
    df = pd.DataFrame(records)
    df.columns = (
        df.columns.str.strip()
        .str.lower()
        .str.replace(" ", "_")
        .str.replace("-", "_")
    )
    return df'''

if old_load in text:
    text = text.replace(old_load, new_load)
else:
    print("Could not find _load_data chunk")

with open("/home/adhi/Adhii/OneForAll/backend/app/mcp_servers/inventory_server.py", "w") as f:
    f.write(text)
