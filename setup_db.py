import sqlite3

def create_hospital_database():
    # Connect to SQLite (creates a hospital.db file automatically)
    conn = sqlite3.connect("hospital.db")
    cursor = conn.cursor()

    # 1. Create Patients Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS patients (
        patient_id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        age INTEGER,
        gender TEXT,
        disease TEXT,
        admission_date DATE,
        room_number INTEGER,
        bill_amount REAL
    )
    """)

    # 2. Insert dummy records if the table is empty
    cursor.execute("SELECT COUNT(*) FROM patients")
    if cursor.fetchone()[0] == 0:
        dummy_patients = [
            ('Amit Sharma', 45, 'Male', 'Heart Attack', '2026-05-10', 102, 15000.50),
            ('Priya Nair', 29, 'Female', 'Appendicitis', '2026-05-12', 204, 8500.00),
            ('John Doe', 65, 'Male', 'Pneumonia', '2026-05-14', 105, 12000.00),
            ('Sneha Patel', 34, 'Female', 'Diabetes', '2026-05-15', 301, 4500.25),
            ('Raj Malhotra', 72, 'Male', 'Heart Attack', '2026-05-18', 101, 22000.00)
        ]
        cursor.executemany("""
        INSERT INTO patients (name, age, gender, disease, admission_date, room_number, bill_amount)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """, dummy_patients)
        
        conn.commit()
        print("Database initialized successfully with sample patient data!")
    else:
        print("Database already exists.")

    conn.close()

if __name__ == "__main__":
    create_hospital_database()