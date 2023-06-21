import mysql.connector
import json

# connect to database
mydb = mysql.connector.connect(
    host="localhost",
    port="3306",
    user="root",
    password="K1pk0r1r!",
    database="cueabot"
)

mycursor = mydb.cursor()

existing_data = {'intents': []}
# load existing JSON data from the file if it exists
try:
    with open('lecturer.json', 'r') as json_file:
        existing_data = json.load(json_file)
except FileNotFoundError:
    pass

# Fetch data from table, lecturer in the database
mycursor.execute("SELECT * FROM lecturers")
myresult = mycursor.fetchall()

# Create a list to store or update the data
updated_data = {'intents': []}

# Loop through the data fetched from the database
for row in myresult:
    # create parameters for the data
    lecturer_id = row[0]
    lecturer_name = row[1]
    lecturer_email = row[2]
    lecturer_phone = row[3]
    lecturer_campus = row[4]
    lecturer_office = row[5]
    lecturer_department = row[6]
    lecturer_faculty = row[7]

    # create a dictionary to store the data
    lecturer_dict = {
        'tag': f'{lecturer_name}',
        'patterns': [
            f'Give me the details on {lecturer_name}',
            f'Where is {lecturer_name} office?',
            f'What is {lecturer_name} email address?',
            f'What is {lecturer_name} phone number?',
            f'What is {lecturer_name} department?',
            f'What is {lecturer_name} faculty?',
            f'What is {lecturer_name} campus?',
            f'Give me the details of {lecturer_name} office',
            f'Give me the details of {lecturer_name} email address',
            f'Give me the details of {lecturer_name} phone number',
            f'Give me the details of {lecturer_name} department',
            f'Give me the details of {lecturer_name} faculty',
            f'Give me the details of {lecturer_name} campus',
            f'Where is {lecturer_name} office located?',
        ],
        'responses': [
            f'Here are the details of {lecturer_name}:'
            f'Email: {lecturer_email}, '
            f'Phone: {lecturer_phone}, '
            f'Office: {lecturer_office}, '
            f'Department: {lecturer_department}, '
            f'Faculty: {lecturer_faculty}, '
            f'Campus: {lecturer_campus}.', ],
        'context_set': ''
    }

    # check if the data already exists in the JSON file
    existing_entry = next(
        (entry for entry in existing_data['intents'] if entry.get('patterns') == lecturer_dict['patterns']),
        None)
    if existing_entry:
        # update the data if it already exists
        existing_entry.update(lecturer_dict)
        updated_data['intents'].append(existing_entry)
    else:
        # add the data if it doesn't exist
        updated_data['intents'].append(lecturer_dict)

# Convert the data to JSON format and write it to the file
json_data = json.dumps(updated_data, indent=4)

# save the data to the file
with open('lecturer.json', 'w') as json_file:
    json_file.write(json_data)

# close the database connection
mycursor.close()
mydb.close()
