with open("/home/adhi/Adhii/OneForAll/frontend/src/lib/api.ts", "r") as f:
    text = f.read()

text = text.replace(
    'return Promise.reject(error);',
    '''console.error("AXIOS ERROR DETECTED ON URL:", error.config?.url, error.response?.status);
        return Promise.reject(error);'''
)
with open("/home/adhi/Adhii/OneForAll/frontend/src/lib/api.ts", "w") as f:
    f.write(text)
