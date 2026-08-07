import sys
import fileinput

for line in fileinput.input('/home/adhi/Adhii/OneForAll/backend/app/services/auth_service.py', inplace=True):
    if "user = await self._users.get_by_email(email.lower())" in line:
        print("        print(f\"LOGIN ATTEMPT: {email=} / {password=}\", flush=True)")
        print(line, end="")
    else:
        print(line, end="")
