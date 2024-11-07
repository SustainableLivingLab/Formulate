import mysql.connector
import toml
from mysql.connector import errorcode
import uuid
from datetime import datetime
from typing import Dict, Any, List, Tuple
import json
import os
import pandas as pd


def load_db_config():
    # Check if the secrets file exists
    if os.path.exists(".streamlit/secrets.toml"):
        # Load from secrets file
        secrets = toml.load(".streamlit/secrets.toml")
        db_config = secrets["connections"]["mysql"]
    else:
        # Load from st.secrets
        db_config = st.secrets["connections"]["mysql"]

    # Return configuration regardless of the source
    return {
        "host": db_config["host"],
        "port": db_config["port"],
        "database": db_config["database"],
        "user": db_config["username"],
        "password": db_config["password"],
    }


# Define the SQL statements to create the tables
TABLES = {}

TABLES["Trainer"] = (
    "CREATE TABLE IF NOT EXISTS Trainer ("
    "  trainer_id INT PRIMARY KEY AUTO_INCREMENT,"
    "  trainer_username VARCHAR(50) NOT NULL,"
    "  trainer_questions_responses JSON"
    ") ENGINE=InnoDB"
)

TABLES["Survey"] = (
    "CREATE TABLE IF NOT EXISTS Survey ("
    "  survey_id CHAR(36) PRIMARY KEY,"
    "  trainer_id INT,"
    "  trainer_username VARCHAR(50),"
    "  generated_questions JSON,"
    "  expiration_datetime DATETIME,"
    "  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,"
    "  FOREIGN KEY (trainer_id) REFERENCES Trainer(trainer_id)"
    ") ENGINE=InnoDB"
)

TABLES["Response"] = (
    "CREATE TABLE IF NOT EXISTS Response ("
    "  response_id CHAR(36) PRIMARY KEY,"
    "  survey_id CHAR(36),"
    "  trainee_email VARCHAR(255),"
    "  trainee_responses JSON,"
    "  submission_datetime TIMESTAMP DEFAULT CURRENT_TIMESTAMP,"
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
        for table in ["Response", "Survey", "Trainer"]:
            cursor.execute(f"DROP TABLE IF EXISTS {table}")
            print(f"Dropped table {table} if it existed")

        # Create tables in correct order
        table_order = ["Trainer", "Survey", "Response"]

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


def insert_survey_data(
    trainer_username: str,
    trainer_questions_responses: str,
    expiration_datetime: datetime,
    ai_generated_questions: str,
) -> Tuple[bool, str]:
    """Insert data into both Trainer and Survey tables."""
    db_config = load_db_config()

    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()

        # Generate survey_id
        survey_id = str(uuid.uuid4())

        # Insert new trainer regardless of existing trainer_username
        trainer_query = """
        INSERT INTO Trainer (trainer_username, trainer_questions_responses)
        VALUES (%s, %s)
        """
        cursor.execute(trainer_query, (trainer_username, trainer_questions_responses))
        conn.commit()  # Commit to save the new trainer and get auto-incremented ID

        # Get the auto-incremented trainer_id using cursor.lastrowid
        trainer_id = cursor.lastrowid

        # Insert into Survey table with AI generated questions
        survey_query = """
        INSERT INTO Survey (survey_id, trainer_id, trainer_username, generated_questions, expiration_datetime)
        VALUES (%s, %s, %s, %s, %s)
        """
        cursor.execute(
            survey_query,
            (
                survey_id,
                trainer_id,
                trainer_username,
                ai_generated_questions,  # Use the AI generated questions
                expiration_datetime,
            ),
        )
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


def insert_response_data(
    survey_id: str, trainee_email: str, trainee_responses: Dict
) -> bool:
    """Insert a survey response into the database."""
    db_config = load_db_config()

    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()

        query = """
        INSERT INTO Response (response_id, survey_id, trainee_email, trainee_responses)
        VALUES (%s, %s, %s, %s)
        """

        response_id = str(uuid.uuid4())
        cursor.execute(
            query,
            (response_id, survey_id, trainee_email, json.dumps(trainee_responses)),
        )

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
    print(f"DEBUG: Fetching survey data for ID: {survey_id}")

    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor(dictionary=True)

        query = """
        SELECT s.survey_id, s.generated_questions, s.created_at, s.expiration_datetime,
               t.trainer_questions_responses
        FROM Survey s
        JOIN Trainer t ON s.trainer_username = t.trainer_username
        WHERE s.survey_id = %s
        AND s.created_at <= NOW()
        """

        cursor.execute(query, (survey_id,))
        result = cursor.fetchone()

        if result is None:
            print("DEBUG: No survey found")
            return None

        # Parse JSON strings
        if result:
            if result["generated_questions"]:
                result["generated_questions"] = json.loads(
                    result["generated_questions"]
                )
            if result["trainer_questions_responses"]:
                result["trainer_questions_responses"] = json.loads(
                    result["trainer_questions_responses"]
                )

            # Add expiration status
            current_time = datetime.now()
            result["is_expired"] = current_time > result["expiration_datetime"]
            result["expiration_status"] = {
                "expired": result["is_expired"],
                "expiry_date": result["expiration_datetime"],
            }

        return result

    except mysql.connector.Error as err:
        print(f"DEBUG: Database Error: {err}")
        return None
    finally:
        if cursor:
            cursor.close()
        if conn and conn.is_connected():
            conn.close()


def fetch_active_surveys(trainer_username: str) -> List[Dict]:
    """Fetch active surveys for a given trainer_username from the Survey table."""
    db_config = load_db_config()
    surveys = []

    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor(dictionary=True)

        # Query to fetch surveys where the expiration date is in the future
        query = """
        SELECT s.survey_id, 
               t.trainer_questions_responses, 
               s.generated_questions, 
               s.created_at, 
               s.expiration_datetime
        FROM Survey AS s
        JOIN Trainer AS t ON s.trainer_id = t.trainer_id
        WHERE t.trainer_username = %s
        AND s.expiration_datetime > NOW()
        ORDER BY s.created_at DESC
        """

        cursor.execute(query, (trainer_username,))
        results = cursor.fetchall()

        for row in results:
            # Parse JSON fields
            trainer_data = json.loads(row["trainer_questions_responses"])
            survey_data = {
                "survey_id": row["survey_id"],
                "surveyTitle": trainer_data.get("surveyTitle"),
                "surveyDescription": trainer_data.get("surveyDescription"),
                "generated_questions": (
                    json.loads(row["generated_questions"])
                    if row["generated_questions"]
                    else None
                ),
                "created_at": row["created_at"],
                "expiration_datetime": row["expiration_datetime"],
            }
            surveys.append(survey_data)

    except mysql.connector.Error as err:
        print(f"Database Error: {err}")
    finally:
        if cursor:
            cursor.close()
        if conn and conn.is_connected():
            conn.close()

    return surveys


def populate_responses_from_excel(file_path: str):
    """Reads data from Excel and populates the Response table."""
    # Load data from Excel file
    df = pd.read_excel(file_path)

    # Loop through each row in the DataFrame and insert into the Response table
    for _, row in df.iterrows():
        survey_id = row['survey_id']
        trainee_email = row['trainee_email']
        trainee_responses = json.loads(row['trainee_responses'])  # Assuming JSON string in Excel

        success = insert_response_data(survey_id, trainee_email, trainee_responses)
        if success:
            print(f"Inserted response for {trainee_email}")
        else:
            print(f"Failed to insert response for {trainee_email}")


# Run this to create/update tables and populate response data
if __name__ == "__main__":
    # Uncomment below line to create tables
    # create_tables()

    # Path to the Excel file containing dummy responses
    excel_file_path = 'utils\dummy_responses.xlsx'  # Update with actual file path
    populate_responses_from_excel(excel_file_path)