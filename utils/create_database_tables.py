import mysql.connector
import toml
from mysql.connector import errorcode
import uuid
from datetime import datetime
from typing import Dict, Any
import json

# Load database credentials from secrets.toml
def load_db_config():
    with open('.streamlit/secrets.toml', 'r') as file:
        secrets = toml.load(file)
        db_config = secrets['connections']['mysql']
        return {
            'host': db_config['host'],
            'port': db_config['port'],
            'database': db_config['database'],
            'user': db_config['username'],
            'password': db_config['password']
        }

# Define the SQL statements to create the tables
TABLES = {}

TABLES['Trainer'] = (
    "CREATE TABLE IF NOT EXISTS Trainer ("
    "  trainer_id INT PRIMARY KEY,"
    "  trainer_questions_responses JSON,"
    "  survey_id CHAR(36),"
    "  INDEX idx_survey_id (survey_id)"
    ") ENGINE=InnoDB"
)

TABLES['Survey'] = (
    "CREATE TABLE IF NOT EXISTS Survey ("
    "  survey_id CHAR(36) PRIMARY KEY,"
    "  trainer_id INT,"
    "  generated_questions JSON,"
    "  expiration_datetime DATETIME,"
    "  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,"
    "  INDEX idx_trainer_id (trainer_id),"
    "  FOREIGN KEY (trainer_id) REFERENCES Trainer(trainer_id)"
    ") ENGINE=InnoDB"
)

TABLES['Response'] = (
    "CREATE TABLE IF NOT EXISTS Response ("
    "  survey_id CHAR(36),"
    "  trainee_email VARCHAR(255),"
    "  trainee_responses JSON,"
    "  submission_datetime TIMESTAMP DEFAULT CURRENT_TIMESTAMP,"
    "  PRIMARY KEY (survey_id, trainee_email),"
    "  FOREIGN KEY (survey_id) REFERENCES Survey(survey_id)"
    ") ENGINE=InnoDB"
)

def create_tables():
    """Create or update the tables"""
    db_config = load_db_config()
    
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()

        # Temporarily disable foreign key checks
        cursor.execute("SET FOREIGN_KEY_CHECKS = 0")

        # Drop existing tables if they exist
        for table in ['Response', 'Survey', 'Trainer']:
            cursor.execute(f"DROP TABLE IF EXISTS {table}")
            print(f"Dropped table {table} if it existed")

        # Create tables in correct order
        table_order = ['Trainer', 'Survey', 'Response']
        
        for table_name in table_order:
            print(f"Creating table {table_name}")
            cursor.execute(TABLES[table_name])
            print(f"Table {table_name} created successfully")

        # Re-enable foreign key checks
        cursor.execute("SET FOREIGN_KEY_CHECKS = 1")

        conn.commit()
        print("All tables created successfully!")

    except mysql.connector.Error as err:
        print(f"Error: {err}")
        if conn:
            conn.rollback()
    finally:
        if cursor:
            cursor.close()
        if conn and conn.is_connected():
            conn.close()

# Add after the create_tables() function

def insert_survey_data(trainer_id: int, trainer_questions_responses: str, expiration_datetime: datetime, ai_generated_questions: str) -> tuple[bool, str]:
    """Insert data into both Trainer and Survey tables."""
    db_config = load_db_config()
    print(f"DEBUG: Starting survey data insertion for trainer_id: {trainer_id}")
    
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()

        # Generate survey_id
        survey_id = str(uuid.uuid4())
        print(f"DEBUG: Generated survey_id: {survey_id}")

        # Check if trainer exists
        check_query = "SELECT trainer_id FROM Trainer WHERE trainer_id = %s"
        cursor.execute(check_query, (trainer_id,))
        trainer_exists = cursor.fetchone()

        if not trainer_exists:
            trainer_query = """
            INSERT INTO Trainer (trainer_id, trainer_questions_responses, survey_id)
            VALUES (%s, %s, %s)
            """
            cursor.execute(trainer_query, (trainer_id, trainer_questions_responses, survey_id))
            print("DEBUG: Inserted new trainer")
        else:
            update_query = """
            UPDATE Trainer 
            SET trainer_questions_responses = %s, survey_id = %s
            WHERE trainer_id = %s
            """
            cursor.execute(update_query, (trainer_questions_responses, survey_id, trainer_id))
            print("DEBUG: Updated existing trainer")

        # Insert into Survey table with AI generated questions
        survey_query = """
        INSERT INTO Survey (survey_id, trainer_id, generated_questions, expiration_datetime)
        VALUES (%s, %s, %s, %s)
        """
        cursor.execute(survey_query, (
            survey_id,
            trainer_id,
            ai_generated_questions,  # Use the AI generated questions
            expiration_datetime
        ))
        print("DEBUG: Inserted into Survey table")

        conn.commit()
        return True, survey_id

    except mysql.connector.Error as err:
        print(f"Database Error: {err}")
        if conn:
            conn.rollback()
        return False, ""
    finally:
        if cursor:
            cursor.close()
        if conn and conn.is_connected():
            conn.close()

def insert_response_data(survey_id: str, trainee_email: str, trainee_responses: Dict) -> bool:
    """Insert a survey response into the database."""
    db_config = load_db_config()
    
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()

        query = """
        INSERT INTO Response (survey_id, trainee_email, trainee_responses)
        VALUES (%s, %s, %s)
        """
        
        cursor.execute(query, (
            survey_id,
            trainee_email,
            json.dumps(trainee_responses)
        ))

        conn.commit()
        return True

    except mysql.connector.Error as err:
        print(f"Database Error: {err}")
        if conn:
            conn.rollback()
        return False
    finally:
        if cursor:
            cursor.close()
        if conn and conn.is_connected():
            conn.close()

def get_survey_data(survey_id: str) -> Dict:
    """Retrieve survey data from Survey table."""
    db_config = load_db_config()
    print(f"DEBUG: Fetching survey data for ID: {survey_id}")
    
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor(dictionary=True)

        query = """
        SELECT survey_id, generated_questions, created_at, expiration_datetime
        FROM Survey
        WHERE survey_id = %s 
        AND expiration_datetime > NOW()
        AND created_at <= NOW()
        """
        
        cursor.execute(query, (survey_id,))
        result = cursor.fetchone()
        
        print(f"DEBUG: Query result: {result}")
        
        if result is None:
            print("DEBUG: No survey found or survey has expired")
            return None
            
        # Parse the JSON string of generated questions
        if result and 'generated_questions' in result:
            result['generated_questions'] = json.loads(result['generated_questions'])
            print(f"DEBUG: Survey created at: {result['created_at']}")
            print(f"DEBUG: Survey expires at: {result['expiration_datetime']}")
            
        return result

    except mysql.connector.Error as err:
        print(f"DEBUG: Database Error: {err}")
        return None
    finally:
        if cursor:
            cursor.close()
        if conn and conn.is_connected():
            conn.close()

def update_survey_questions(survey_id: str, generated_questions: str) -> bool:
    """Update Survey table with AI-generated questions."""
    db_config = load_db_config()
    
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()

        query = """
        UPDATE Survey 
        SET generated_questions = %s
        WHERE survey_id = %s
        """
        
        cursor.execute(query, (generated_questions, survey_id))
        conn.commit()
        print(f"DEBUG: Updated Survey table with generated questions for survey_id: {survey_id}")
        return True

    except mysql.connector.Error as err:
        print(f"Database Error: {err}")
        if conn:
            conn.rollback()
        return False
    finally:
        if cursor:
            cursor.close()
        if conn and conn.is_connected():
            conn.close()

# Run this to create/update tables
if __name__ == "__main__":
    print("Creating/Updating tables...")
    create_tables()
