import mysql.connector
import json

# Connect to the database
try:
    mydb = mysql.connector.connect(
        host="localhost",
        port="3306",
        user="root",
        password="",
        database="cueabot"
    )
    mycursor = mydb.cursor()
except mysql.connector.Error as err:
    print("Error: ", err)

existing_data = {'intents': []}
# load existing JSON data from the file if it exists
try:
    with open('event.json', 'r') as json_file:
        existing_data = json.load(json_file)
except FileNotFoundError:
    pass


def generate_event_json():
    # Fetch data from table, event in the database
    mycursor.execute("SELECT * FROM events")
    myresult = mycursor.fetchall()

    # Create a list to store or update the data
    updated_data = {'intents': []}

    # Loop through the data fetched from the database
    for row in myresult:
        # create parameters for the data
        event_id = row[0]
        event_name = row[1]
        event_campus = row[2]
        event_venue = row[3]
        event_date = row[4]
        event_time = row[5]
        event_description = row[6]

        # create a dictionary to store the data
        event_dict = {
            'tag': f'{event_name}',
            'patterns': [
                f'When is {event_name}?',
                f'What event is happening on {event_date}?',
                f'At what time is {event_name}?',
                f'Where is {event_name}?',
                f'What is {event_name} about?',
                f'What is happening on {event_date}?',
                f'What is happening on {event_date} at {event_campus}?',
                f'Where is {event_name} happening?',
            ],
            'responses': [
                f'{event_name} is happening on {event_date} at {event_time} in {event_campus} at {event_venue}. {event_description}'],
            'context_set': ''
        }

        # check if the data already exists in the JSON file
        existing_entry = next(
            (entry for entry in existing_data['intents'] if entry.get('patterns') == event_dict['patterns']),
            None)
        if existing_entry:
            # update the data if it already exists
            existing_entry.update(event_dict)
            updated_data['intents'].append(existing_entry)
        else:
            # add the data if it doesn't exist
            updated_data['intents'].append(event_dict)

    # Convert the data to JSON format and write it to the file
    json_data = json.dumps(updated_data, indent=4)

    # save the data to the file
    with open('event.json', 'w') as json_file:
        json_file.write(json_data)

    # close the database connection
    mycursor.close()
    mydb.close()
