import mysql.connector
import toml
from mysql.connector import errorcode

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
