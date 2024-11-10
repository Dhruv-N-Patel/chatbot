import sqlite3

def initialize_database():
    # Connect to SQLite database
    conn = sqlite3.connect('mumbai_attractions.db')
    cursor = conn.cursor()

    # Create the attractions table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS attractions (
            id INTEGER PRIMARY KEY,
            name TEXT,
            type TEXT,
            fee REAL,
            popularity INTEGER,
            location TEXT
        )
    ''')

    # Insert sample attractions
    attractions = [
        ("Gateway of India", "historical", 0, 5, "Gateway of India, Mumbai"),
        ("Chhatrapati Shivaji Maharaj Vastu Sangrahalaya", "museum", 10, 4, "CSMVS Museum, Mumbai"),
        ("Marine Drive", "relaxing", 0, 5, "Marine Drive, Mumbai"),
        ("Haji Ali Dargah", "religious", 0, 4, "Haji Ali Dargah, Mumbai"),
        ("Juhu Beach", "relaxing", 0, 4, "Juhu Beach, Mumbai"),
        ("Siddhivinayak Temple", "religious", 0, 5, "Siddhivinayak Temple, Mumbai"),
        # Add more attractions as needed
    ]

    cursor.executemany('''
        INSERT INTO attractions (name, type, fee, popularity, location)
        VALUES (?, ?, ?, ?, ?)
    ''', attractions)

    # Commit changes and close connection
    conn.commit()
    conn.close()

# Initialize the database
if __name__ == "__main__":
    initialize_database()
