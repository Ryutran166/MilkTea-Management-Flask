import requests

# Replace BASE_URL and ACCESS_TOKEN
BASE_URL = "http://localhost:5000"
ACCESS_TOKEN = "REPLACE_ME"

payload = {
    "name": "Chi nhánh test",
    "phone": None,
    "address": "Địa chỉ test",
    "status": True,
}

r = requests.post(
    f"{BASE_URL}/branches",
    headers={
        "Authorization": f"Bearer {ACCESS_TOKEN}",
        "Content-Type": "application/json",
    },
    json=payload,
)

print("status:", r.status_code)
print("body:", r.text)

