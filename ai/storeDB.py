from ai.config import conn
import mysql.connector

# Create a cursor object


def insert_data(survey_id, survey_data):
    # Define the SQL query with placeholders for data
    cursor = conn.cursor()
    query = "INSERT INTO surveys (id, survey_form_id, survey_data) VALUES (%s, %s, %s)"
    data = (survey_id, survey_id, survey_data)

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