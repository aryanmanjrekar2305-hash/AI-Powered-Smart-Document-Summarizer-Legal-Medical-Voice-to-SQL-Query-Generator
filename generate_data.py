import sqlite3
import random
from datetime import datetime, timedelta

def populate_bulk_data():
    # Connect to your existing database
    conn = sqlite3.connect("hospital.db")
    cursor = conn.cursor()
    
    # 1. Pools of realistic medical data to mix and match
    first_names = ["Arjun", "Neha", "Amit", "Priya", "Rahul", "Anjali", "Vikram", "Riya", "Rohan", "Siddharth", 
                   "Kiran", "Deepak", "Sunita", "Yash", "Tanvi", "Aditya", "Meera", "Sanjay", "Kavita", "Rajesh"]
    last_names = ["Sharma", "Verma", "Kumar", "Singh", "Joshi", "Mehta", "Das", "Patel", "Reddy", "Nair", 
                  "Gupta", "Rao", "Mishra", "Choudhury", "Pillai", "Sen", "Kapoor", "Malhotra", "Jadhav", "Saxena"]
    
    genders = ["Male", "Female"]
    
    diseases_and_rooms = [
        ("Flu", [101, 102, 103, 104, 105]),
        ("Heart Attack", [201, 202, 203, 204]),
        ("Appendicitis", [301, 302, 303]),
        ("Pneumonia", [106, 107, 108]),
        ("Diabetes Complications", [401, 402, 403]),
        ("Migraine Chronic", [109, 110]),
        ("Kidney Stone", [304, 305]),
        ("Asthma Attack", [111, 112]),
        ("Fracture Surgery", [501, 502, 503]),
        ("Dengue Fever", [114, 115, 116])
    ]
    
    print("⏳ Generating 50 mock patient profiles...")
    
    # Generate 50 unique patient records
    for _ in range(50):
        # Construct Name & Profile
        name = f"{random.choice(first_names)} {random.choice(last_names)}"
        age = random.randint(18, 85)
        gender = random.choice(genders)
        
        # Pick a disease scenario
        disease, rooms = random.choice(diseases_and_rooms)
        room_number = random.choice(rooms)
        
        # Financial metric generation
        bill_amount = round(random.uniform(350.0, 4500.0), 2)
        
        # Map randomly to doctor IDs 1 through 5 (assuming they exist in your doctors table)
        doctor_id = random.randint(1, 5)
        
        # Randomize admission dates over the last 30 days
        random_days_ago = random.randint(0, 30)
        admission_date = (datetime.now() - timedelta(days=random_days_ago)).strftime("%Y-%m-%d")
        
        # Execute the write command
        cursor.execute("""
            INSERT INTO patients (name, age, gender, disease, admission_date, room_number, bill_amount, doctor_id)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (name, age, gender, disease, admission_date, room_number, bill_amount, doctor_id))
    
    # Commit changes permanently to file storage
    conn.commit()
    conn.close()
    print("🚀 Success! 50 randomized medical records successfully injected into hospital.db.")

if __name__ == "__main__":
    populate_bulk_data()