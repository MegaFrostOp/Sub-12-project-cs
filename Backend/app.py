import os
import requests
from dotenv import load_dotenv
from flask import Flask, jsonify

 


load_dotenv()



app = Flask(__name__)

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")



@app.route("/")
def home():
    return {"message": "Backend is working!"}

table = "teachersmondayfree"
url = f"{SUPABASE_URL}/rest/v1/{table}?select=*"

headers = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json"
}

response = requests.get(url, headers=headers)

if response.status_code == 200:
    data = response.json()
    print("Data fetched:", data)
else:
    print("Error:", response.status_code, response.text)

if __name__ == "__main__":
    app.run(debug=True)
