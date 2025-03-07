from database import conn, cursor  

def create_tables():
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id SERIAL PRIMARY KEY,
        username VARCHAR(50) UNIQUE NOT NULL,
        password TEXT NOT NULL,
        email VARCHAR(100) UNIQUE NOT NULL,
        full_name VARCHAR(100),
        education_level VARCHAR(50),
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );

    CREATE TABLE IF NOT EXISTS quiz_questions (
        id SERIAL PRIMARY KEY,
        user_id INT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
        quiz_id UUID NOT NULL,
        question_text TEXT NOT NULL,
        option_a TEXT NOT NULL,
        option_b TEXT NOT NULL,
        option_c TEXT NOT NULL,
        option_d TEXT NOT NULL,
        option_e TEXT NOT NULL,
        correct_answer CHAR(1) NOT NULL,
        difficulty VARCHAR(10) NOT NULL, 
        topic TEXT NOT NULL, 
        created_at TIMESTAMP DEFAULT NOW()
    );
    
    CREATE TABLE IF NOT EXISTS user_responses (
        id SERIAL PRIMARY KEY,
        user_id INT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
        quiz_id UUID NOT NULL,
        question_id INT NOT NULL REFERENCES quiz_questions(id) ON DELETE CASCADE,
        selected_answer CHAR(1) NOT NULL,
        is_correct BOOLEAN NOT NULL,
        time_taken INT NOT NULL, -- Time in seconds
        topic TEXT NOT NULL,
        difficulty VARCHAR(10) NOT NULL,
        created_at TIMESTAMP DEFAULT NOW()
    );
    """)
    conn.commit()
    print("✅ Tables created successfully!")

if __name__ == "__main__":
    create_tables()
    cursor.close()
    conn.close()
