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
    with open('timetable.json', 'r') as json_file:
        existing_data = json.load(json_file)
except FileNotFoundError:
    pass

# Fetch data from table, timetable in the database
mycursor.execute("SELECT * FROM timetable")
myresult = mycursor.fetchall()

# Create a list to store or update the data
updated_data = {'intents': []}

# Loop through the data fetched from the database
for row in myresult:
    # create parameters for the data
    timetable_id = row[0]
    course_code = row[1]
    course_title = row[2]
    course_lecturer = row[3]
    course_venue = row[4]
    course_day = row[5]
    course_time = row[6]

    # create a dictionary to store the data
    timetable_dict = {
        'tag': f'{course_code}',
        'patterns': [
            f'When is {course_code} on my timetable?',
            f'When is {course_title} on my timetable?',
            f'Which class do i have on {course_day} at {course_time}?',
            f'When do i have {course_code}?',
            f'When do i have {course_title}?',
            f'When is {course_code}?',
            f'When is {course_title}?',

        ],
        'responses': [
            f'The class for {course_code}: {course_title} is at  {course_time} on {course_day} at {course_venue} '
            f'by {course_lecturer}'],
        'context_set': ''
    }

    # check if the data already exists in the JSON file
    existing_entry = next(
        (entry for entry in existing_data['intents'] if entry.get('patterns') == timetable_dict['patterns']),
        None)
    if existing_entry:
        # update the data if it already exists
        existing_entry.update(timetable_dict)
        updated_data['intents'].append(existing_entry)
    else:
        # add the data if it doesn't exist
        updated_data['intents'].append(timetable_dict)

# Convert the data to JSON format and write it to the file
json_data = json.dumps(updated_data, indent=4)

# save the data to the file
with open('timetable.json', 'w') as json_file:
    json_file.write(json_data)

# close the database connection
mycursor.close()
mydb.close()
