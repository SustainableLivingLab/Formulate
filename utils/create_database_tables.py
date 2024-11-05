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
    "  custom_questions_data JSON"
    ") ENGINE=InnoDB;"
)

TABLES['Surveys'] = (
    "CREATE TABLE IF NOT EXISTS Surveys ("
    "  survey_id CHAR(36) PRIMARY KEY,"
    "  trainer_id CHAR(36),"
    "  survey_questions JSON,"
    "  expiration_datetime DATETIME,"
    "  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,"
    "  FOREIGN KEY (trainer_id) REFERENCES Trainer(trainer_id)"
    ") ENGINE=InnoDB;"
)

TABLES['Responses'] = (
    "CREATE TABLE IF NOT EXISTS Responses ("
    "  response_id CHAR(36) PRIMARY KEY,"
    "  survey_id CHAR(36),"
    "  trainee_email VARCHAR(255),"
    "  response_content JSON,"
    "  FOREIGN KEY (survey_id) REFERENCES Surveys(survey_id)"
    ") ENGINE=InnoDB;"
)

# Function to connect to the MySQL database and create tables
def create_tables():
    db_config = load_db_config()
    
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()

        # Loop through the TABLES dictionary and create each table
        for table_name, ddl in TABLES.items():
            try:
                print(f"Creating table `{table_name}`...")
                cursor.execute(ddl)
                print(f"Table `{table_name}` created successfully.")
            except mysql.connector.Error as err:
                if err.errno == errorcode.ER_TABLE_EXISTS_ERROR:
                    print(f"Table `{table_name}` already exists.")
                else:
                    print(f"Error creating table `{table_name}`: {err}")

        cursor.close()
        conn.close()
        print("All tables created successfully (or verified if they already exist).")

    except mysql.connector.Error as err:
        print(f"Error: {err}")
        exit(1)

# Run the function to create tables
create_tables()

def insert_survey_data(survey_id: str, survey_questions: str, expiration_datetime: datetime) -> bool:
    """
    Insert a new survey into the database.
    Returns True if successful, False otherwise.
    """
    db_config = load_db_config()
    
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()

        # First, insert into Trainer table (using a default trainer_id for now)
        trainer_id = str(uuid.uuid4())
        trainer_query = "INSERT INTO Trainer (trainer_id, custom_questions_data) VALUES (%s, %s)"
        cursor.execute(trainer_query, (trainer_id, None))

        # Then, insert into Surveys table
        survey_query = """
        INSERT INTO Surveys (survey_id, trainer_id, survey_questions, expiration_datetime)
        VALUES (%s, %s, %s, %s)
        """
        cursor.execute(survey_query, (
            survey_id,
            trainer_id,
            survey_questions,
            expiration_datetime
        ))

        conn.commit()
        cursor.close()
        conn.close()
        return True

    except mysql.connector.Error as err:
        print(f"Database Error: {err}")
        if conn:
            conn.rollback()
        return False
    except Exception as e:
        print(f"Unexpected Error: {e}")
        if conn:
            conn.rollback()
        return False
    finally:
        if conn and conn.is_connected():
            conn.close()

def insert_response_data(survey_id: str, trainee_email: str, response_content: Dict[str, Any]) -> bool:
    """
    Insert a survey response into the database.
    Returns True if successful, False otherwise.
    """
    db_config = load_db_config()
    
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()

        response_id = str(uuid.uuid4())
        query = """
        INSERT INTO Responses (response_id, survey_id, trainee_email, response_content)
        VALUES (%s, %s, %s, %s)
        """
        cursor.execute(query, (
            response_id,
            survey_id,
            trainee_email,
            json.dumps(response_content)
        ))

        conn.commit()
        cursor.close()
        conn.close()
        return True

    except mysql.connector.Error as err:
        print(f"Database Error: {err}")
        if conn:
            conn.rollback()
        return False
    except Exception as e:
        print(f"Unexpected Error: {e}")
        if conn:
            conn.rollback()
        return False
    finally:
        if conn and conn.is_connected():
            conn.close()
            
def parsed_response_content(survey_id: str, trainee_email: str) -> Dict[str, Any]:
    db_config = load_db_config()
    
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()

        query = "SELECT response_content FROM Responses WHERE survey_id = %s AND trainee_email = %s"
        cursor.execute(query, (survey_id, trainee_email))

        response_content = cursor.fetchone()[0]
        cursor.close()
        conn.close()
        return response_content

    except mysql.connector.Error as err:
        print(f"Database Error: {err}")
        if conn:
            conn.rollback()
        return None
    except Exception as e:
        print(f"Error: {e}")
        return None