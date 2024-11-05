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
    "  trainer_id CHAR(36) PRIMARY KEY,"
    "  trainer_questions_responses JSON,"
    "  survey_id CHAR(36),"
    "  expiration_datetime DATETIME,"
    "  INDEX idx_survey_id (survey_id)"
    ") ENGINE=InnoDB"
)

TABLES['Survey'] = (
    "CREATE TABLE IF NOT EXISTS Survey ("
    "  survey_id CHAR(36) PRIMARY KEY,"
    "  trainer_id CHAR(36),"
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
    "  profile_questions_responses JSON,"
    "  survey_questions_responses JSON,"
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

def insert_survey_data(trainer_questions_responses: str, expiration_datetime: datetime) -> tuple[bool, str]:
    """
    Insert data into both Trainer and Survey tables.
    Returns (success: bool, survey_id: str)
    """
    db_config = load_db_config()
    
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()

        # Generate UUIDs
        trainer_id = str(uuid.uuid4())
        survey_id = str(uuid.uuid4())
        print(f"DEBUG: Generated IDs - Trainer: {trainer_id}, Survey: {survey_id}")

        # Insert into Trainer table
        trainer_query = """
        INSERT INTO Trainer (trainer_id, trainer_questions_responses, survey_id, expiration_datetime)
        VALUES (%s, %s, %s, %s)
        """
        cursor.execute(trainer_query, (
            trainer_id,
            trainer_questions_responses,
            survey_id,
            expiration_datetime
        ))
        print(f"DEBUG: Inserted into Trainer table")

        # Insert into Survey table
        survey_query = """
        INSERT INTO Survey (survey_id, trainer_id, generated_questions, expiration_datetime)
        VALUES (%s, %s, %s, %s)
        """
        cursor.execute(survey_query, (
            survey_id,
            trainer_id,
            trainer_questions_responses,  # Initially store the same data
            expiration_datetime
        ))
        print(f"DEBUG: Inserted into Survey table")

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

def insert_response_data(survey_id: str, trainee_email: str, profile_responses: Dict, survey_responses: Dict) -> bool:
    """Insert a survey response into the database."""
    db_config = load_db_config()
    
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()

        query = """
        INSERT INTO Response (survey_id, trainee_email, profile_questions_responses, survey_questions_responses)
        VALUES (%s, %s, %s, %s)
        """
        
        cursor.execute(query, (
            survey_id,
            trainee_email,
            json.dumps(profile_responses),
            json.dumps(survey_responses)
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
    """Retrieve survey data and check expiration."""
    db_config = load_db_config()
    print(f"Attempting to fetch survey data for ID: {survey_id}")  # Debug log
    
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor(dictionary=True)

        # Modified query to get data from Trainer table instead of Survey
        query = """
        SELECT trainer_id, trainer_questions_responses, expiration_datetime
        FROM Trainer
        WHERE survey_id = %s AND expiration_datetime > NOW()
        """
        
        cursor.execute(query, (survey_id,))
        result = cursor.fetchone()
        
        print(f"Query result: {result}")  # Debug log
        
        if result is None:
            print("No survey found or survey has expired")  # Debug log
            return None
            
        # Parse the JSON string back to dictionary
        if result and 'trainer_questions_responses' in result:
            result['trainer_questions_responses'] = json.loads(result['trainer_questions_responses'])
            
        return result

    except mysql.connector.Error as err:
        print(f"Database Error: {err}")  # Debug log
        if conn:
            conn.rollback()
        return None
    finally:
        if cursor:
            cursor.close()
        if conn and conn.is_connected():
            conn.close()

# Run this to create/update tables
if __name__ == "__main__":
    print("Creating/Updating tables...")
    create_tables()
