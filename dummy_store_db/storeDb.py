import mysql.connector

# Establish the database connection
conn = mysql.connector.connect(
    host="52.221.212.231",
    user="infra",
    password="3dp)J>Q=1=QzYpgb",
    database="genai"
)

# Create a cursor object
cursor = conn.cursor()

# Define the SQL query with placeholders for data
query = "INSERT INTO surveys (id, survey_form_id) VALUES (%s, %s)"
data = ("991", "hello_world")  # Replace with actual values

try:
    # Execute the query with the data
    cursor.execute(query, data)
    
    # Commit the transaction
    conn.commit()
    print("Data inserted successfully.")
except mysql.connector.Error as error:
    print(f"Error: {error}")
    conn.rollback()  # Rollback in case of error
finally:
    # Close the cursor and connection
    cursor.close()
    conn.close()