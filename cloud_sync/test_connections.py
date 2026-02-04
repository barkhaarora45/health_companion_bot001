import gspread
from oauth2client.service_account import ServiceAccountCredentials

scope = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/drive"
]

creds = ServiceAccountCredentials.from_json_keyfile_name(
    r"D:\robot_system\credentials\service_account.json",
    scope
)

client = gspread.authorize(creds)

sheet = client.open("HCB").sheet1
data = sheet.get_all_records()

print("Connection successful")
print(data)
