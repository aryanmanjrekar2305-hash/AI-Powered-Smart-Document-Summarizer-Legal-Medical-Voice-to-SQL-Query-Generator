import sqlite3

def init_db():
    conn = sqlite3.connect("hospital.db")
    cursor = conn.cursor()
    
    # 🔥 ADD THESE TWO LINES TO CLEAR OUT THE OLD STRUCTURE:
    cursor.execute("DROP TABLE IF EXISTS patients")
    cursor.execute("DROP TABLE IF EXISTS doctors")
    
    # 1. Create Doctors Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS doctors (
        doctor_id INTEGER PRIMARY KEY AUTOINCREMENT,
        doctor_name TEXT NOT NULL,
        department TEXT NOT NULL,
        consultation_fee REAL NOT NULL
    )
    """)
    
    # 2. Create Patients Table with Foreign Key
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS patients (
        patient_id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        age INTEGER NOT NULL,
        gender TEXT NOT NULL,
        disease TEXT NOT NULL,
        admission_date TEXT NOT NULL,
        room_number INTEGER NOT NULL,
        bill_amount REAL NOT NULL,
        doctor_id INTEGER,
        FOREIGN KEY (doctor_id) REFERENCES doctors(doctor_id)
    )
    """)
    
    # ... (rest of your insert data code stays exactly the same)
    
    # 3. Seed Sample Data (Clear old data first to avoid duplicates)
    cursor.execute("DELETE FROM patients")
    cursor.execute("DELETE FROM doctors")
    
    # Insert Doctors
    doctors_data = [
        ("Dr. Alok Sharma", "Cardiology", 1500.0),
        ("Dr. Priya Mehta", "Neurology", 2000.0),
        ("Dr. Rohan Das", "General Medicine", 800.0)
    ]
    cursor.executemany("INSERT INTO doctors (doctor_name, department, consultation_fee) VALUES (?, ?, ?)", doctors_data)
    
    # Insert Patients linked to Doctor IDs
    patients_data = [
        ("Rahul Verma", 45, "Male", "Heart Attack", "2026-05-10", 101, 15000.0, 1),
        ("Aditi Rao", 34, "Female", "Migraine", "2026-06-02", 204, 4500.0, 2),
        ("Amit Patel", 62, "Male", "Heart Attack", "2026-05-15", 102, 22000.0, 1),
        ("Sneha Reddy", 29, "Female", "Viral Fever", "2026-06-18", 305, 1200.0, 3)
    ]
    cursor.executemany("""
        INSERT INTO patients (name, age, gender, disease, admission_date, room_number, bill_amount, doctor_id) 
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, patients_data)
    
    conn.commit()
    conn.close()
    print("✨ Database successfully upgraded to 2 tables with multi-relational sample data!")

if __name__ == "__main__":
    init_db()