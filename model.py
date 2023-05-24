import mysql.connector

# Connect to Database
# try except block to handle connection errors
try:
    mydb = mysql.connector.connect(
        host="localhost",
        port="3306",
        user="root",
        password="K1pk0r1r!",
        database="cueabot"
    )
    print("Connection Successful at Model.py")
    mycursor = mydb.cursor()
except mysql.connector.Error as err:
    print("Error: ", err)


# Create Cursor


# Create Tables
def createTables():
    usersTB = """
    CREATE TABLE IF NOT EXISTS users (
        full_name VARCHAR(100) NOT NULL,
        dob DATE NOT NULL,
        mobile_no VARCHAR(13) NOT NULL UNIQUE,
        campus VARCHAR(10) NOT NULL,
        faculty VARCHAR(50) NOT NULL,
        program VARCHAR(200) NOT NULL,
        email VARCHAR(20) NOT NULL UNIQUE,
        school_id INT NOT NULL PRIMARY KEY,
        date_joined DATE NOT NULL,
        recovery_question VARCHAR(500) NOT NULL,
        recovery_answer VARCHAR(100) NOT NULL,
        password VARCHAR(50) NOT NULL
    )"""

    conversationsTB = """
    CREATE TABLE IF NOT EXISTS conversations (
        conversation_no INT AUTO_INCREMENT,
        user_id INT NOT NULL,
        message_sent VARCHAR(500) NOT NULL,
        message_received VARCHAR(500) NOT NULL,
        date_sent DATE NOT NULL,
        time_sent TIME NOT NULL,
        PRIMARY KEY(conversation_no),
        FOREIGN KEY(user_id) REFERENCES users(school_id)
    )"""

    lecturersTB = """
    CREATE TABLE IF NOT EXISTS lecturers (
        lecturer_no INT AUTO_INCREMENT,
        lecturer_name VARCHAR(100) NOT NULL UNIQUE,
        lecturer_email VARCHAR(100) NOT NULL UNIQUE,
        lecturer_phone VARCHAR(13) NOT NULL UNIQUE,
        lecturer_campus VARCHAR(10) NOT NULL,
        lecturer_office VARCHAR(100) NOT NULL,
        lecturer_department VARCHAR(100) NOT NULL,
        lecturer_faculty VARCHAR(100) NOT NULL,
        PRIMARY KEY(lecturer_no)
    )"""

    timetableTB = """
    CREATE TABLE IF NOT EXISTS timetable (
        timetable_no INT AUTO_INCREMENT,
        course_code VARCHAR(10) NOT NULL,
        course_title VARCHAR(100) NOT NULL,
        course_lecturer VARCHAR(100) NOT NULL,
        course_venue VARCHAR(100) NOT NULL,
        course_day VARCHAR(10) NOT NULL,
        course_time VARCHAR(10) NOT NULL,
        PRIMARY KEY(timetable_no),
        FOREIGN KEY(course_lecturer) REFERENCES lecturers(lecturer_name)
    )"""

    eventsTB = """
    CREATE TABLE IF NOT EXISTS events (
        event_no INT AUTO_INCREMENT,
        event_name VARCHAR(100) NOT NULL,
        event_venue VARCHAR(100) NOT NULL,
        event_date DATE NOT NULL,
        event_time TIME NOT NULL,
        event_description VARCHAR(500) NOT NULL,
        PRIMARY KEY(event_no)
    )"""

    # execute table creation
    # tries except block to catch errors
    try:
        mycursor.execute(usersTB)
        mycursor.execute(conversationsTB)
        mycursor.execute(lecturersTB)
        mycursor.execute(timetableTB)
        mycursor.execute(eventsTB)
        print("Tables Created Successfully")
    except mysql.connector.Error as sqlerror:
        print("Error Creating Tables: {}".format(sqlerror))

    # insert test double data into lectures table
    lecturer_sql = "INSERT IGNORE INTO lecturers (lecturer_no, lecturer_name, lecturer_email, lecturer_phone, " \
                   "lecturer_campus, lecturer_office, lecturer_department, lecturer_faculty) " \
                   "VALUES (NULL, %(lecturer_name)s, %(lecturer_email)s, %(lecturer_phone)s, %(lecturer_campus)s, " \
                   "%(lecturer_office)s, %(lecturer_department)s, %(lecturer_faculty)s)"

    lecturer_val = [
        {'lecturer_name': 'Mr. Kioko', 'lecturer_email': 'kioko@cuea.edu', 'lecturer_phone': '+254722989342',
         'lecturer_campus': 'Langata', 'lecturer_office': 'OH 12', 'lecturer_department': 'Computer Science',
         'lecturer_faculty': 'Science'},
        {'lecturer_name': 'Mr. Mwangi', 'lecturer_email': 'mwangi@cuea.edu', 'lecturer_phone': '+254718273645',
         'lecturer_campus': 'Langata', 'lecturer_office': 'OH 15', 'lecturer_department': 'Computer Science',
         'lecturer_faculty': 'Science'},
        {'lecturer_name': 'Mr. Mirugi', 'lecturer_email': 'mirugi@cuea.edu', 'lecturer_phone': '+254712345678',
         'lecturer_campus': 'Gaba', 'lecturer_office': 'OH 12', 'lecturer_department': 'Computer Science',
         'lecturer_faculty': 'Science'},
        {'lecturer_name': 'Mr. Nichodemus', 'lecturer_email': 'nichodemus@cuea.edu', 'lecturer_phone': '+254777237541',
         'lecturer_campus': 'Langata', 'lecturer_office': 'OH 12', 'lecturer_department': 'Computer Science',
         'lecturer_faculty': 'Science'},
        {'lecturer_name': 'Mrs. Doreen', 'lecturer_email': 'doreen@cuea.edu', 'lecturer_phone': '+254722090899',
         'lecturer_campus': 'Langata', 'lecturer_office': 'OH 12', 'lecturer_department': 'Computer Science',
         'lecturer_faculty': 'Science'},
        {'lecturer_name': 'Mr. Wafula', 'lecturer_email': 'wafula@cuea.edu', 'lecturer_phone': '+254718654453',
         'lecturer_campus': 'Gaba', 'lecturer_office': 'TH 11', 'lecturer_department': 'Law',
         'lecturer_faculty': 'Law'},
        {'lecturer_name': 'Mr. Kibet', 'lecturer_email': 'kibet@cuea.edu', 'lecturer_phone': '+254777300929',
         'lecturer_campus': 'Langata', 'lecturer_office': 'RH 02', 'lecturer_department': 'Finance',
         'lecturer_faculty': 'Commerce and Business'},
        {'lecturer_name': 'Ms. Wangui', 'lecturer_email': 'wangui@cuea.edu', 'lecturer_phone': '+254728908809',
         'lecturer_campus': 'Gaba', 'lecturer_office': 'OH 12', 'lecturer_department': 'Actuarial Science',
         'lecturer_faculty': 'Science'},
        {'lecturer_name': 'Mr. Chalo', 'lecturer_email': 'chalo@cuea.edu', 'lecturer_phone': '+254792788873',
         'lecturer_campus': 'Langata', 'lecturer_office': 'TH 12', 'lecturer_department': 'Finance',
         'lecturer_faculty': 'Commerce and Business'},
    ]

    timetable_sql = "INSERT IGNORE INTO timetable (timetable_no, course_code, course_title, course_lecturer, " \
                    "course_venue, course_day, course_time) VALUES (NULL,%(course_code)s, %(course_title)s, " \
                    "%(course_lecturer)s, %(course_venue)s, %(day)s, %(time)s)"

    timetable_val = [
        {
            'course_code': 'CSC 101',
            'course_title': 'Introduction to Computer Science',
            'course_lecturer': 'Mr. Kioko',
            'course_venue': 'OH 12',
            'day': 'Monday',
            'time': '8:00 AM'
        },
        {
            'course_code': 'CSC 101',
            'course_title': 'Introduction to Computer Science',
            'course_lecturer': 'Mr. Kioko',
            'course_venue': 'OH 12',
            'day': 'Wednesday',
            'time': '8:00 AM'
        },
        {
            'course_code': 'CSC 101',
            'course_title': 'Introduction to Computer Science',
            'course_lecturer': 'Mr. Kioko',
            'course_venue': 'OH 12',
            'day': 'Friday',
            'time': '8:00 AM'
        },
        {
            'course_code': 'CSC 102',
            'course_title': 'Introduction to Programming',
            'course_lecturer': 'Mr. Mwangi',
            'course_venue': 'OH 15',
            'day': 'Monday',
            'time': '10:00 AM'
        },
        {
            'course_code': 'CSC 102',
            'course_title': 'Introduction to Programming',
            'course_lecturer': 'Mr. Mwangi',
            'course_venue': 'OH 15',
            'day': 'Wednesday',
            'time': '10:00 AM'
        },
        {
            'course_code': 'CSC 102',
            'course_title': 'Introduction to Programming',
            'course_lecturer': 'Mr. Mwangi',
            'course_venue': 'OH 15',
            'day': 'Friday',
            'time': '10:00 AM'
        },
        {
            'course_code': 'CSC 103',
            'course_title': 'Introduction to Computer Systems',
            'course_lecturer': 'Mr. Mirugi',
            'course_venue': 'OH 12',
            'day': 'Monday',
            'time': '2:00 PM'
        },
    ]

    events_sql = "INSERT IGNORE INTO events (event_no, event_name, event_venue, event_date, event_time, " \
                 "event_description) VALUES (NULL,%(event_name)s, %(event_location)s, %(event_date)s, " \
                 "%(event_time)s, %(event_description)s)"

    events_val = [
        {
            'event_name': 'CUEA Hackathon',
            'event_location': 'Langata',
            'event_date': '2023-04-11',
            'event_time': '4:00 PM',
            'event_description': 'A hackathon is a design sprint-like event; often, in which computer programmers and'
                                 ' others involved in software development, including graphic designers, interface '
                                 'designers, project managers, domain experts, and others collaborate intensively on '
                                 'software projects.'
        },
        {
            'event_name': 'CUEA Open Day',
            'event_location': 'Langata',
            'event_date': '2023-01-12',
            'event_time': '8:00 AM',
            'event_description': 'An open day (or open evening or open house) is an event held at an institution where '
                                 'its doors are open to the general public, allowing people to look around the '
                                 'institution and learn about it.'
        },
        {
            'event_name': 'CUEA Career Fair',
            'event_location': 'Gaba',
            'event_date': '2022-10-10',
            'event_time': '2:00 PM',
            'event_description': 'A career fair, also referred commonly as a career expo or career exhibition, is an '
                                 'event in which employers, recruiters, and schools give information to potential '
                                 'employees. Job seekers attend these while trying to make a good impression to '
                                 'potential coworkers by speaking face-to-face with one another, filling out resumes, '
                                 'and asking questions in attempt to get a good feel on the work needed. Career '
                                 'expositions usually include company or organization tables or booths where '
                                 'resumes can be collected and business cards can be exchanged. Often sponsored by '
                                 'career centers, job fairs provide a convenient location for students to meet '
                                 'employers and perform first interviews.'
        },
        {
            'event_name': 'CUEA Sports Day',
            'event_location': 'Gaba',
            'event_date': '2023-03-10',
            'event_time': '11:00 AM',
            'event_description': 'A sports day, also known as field day, is a day on which people participate in '
                                 'competitive sporting activities, often with the aim of winning trophies or prizes. '
                                 'Though often held at the beginning of summer, many schools hold their sports days in '
                                 'late spring or in autumn, especially in countries where the summer is very harsh. '
                                 'Schools stage many sports days in which children participate in the sporting events. '
                                 'It is usually held in elementary schools, or grades Kindergarten-8th Grade. In '
                                 'schools which use a house system a feature of the school is the competition between '
                                 'the houses; this is especially brought out during sporting events such as an '
                                 'inter-house sports day.'
        },
        {
            'event_name': 'CUEA Cultural Day',
            'event_location': 'Langata',
            'event_date': '2023-02-15',
            'event_time': '8:00 AM',
            'event_description': 'A cultural day is a day set aside to celebrate the culture of a people. It is a '
                                 'day to showcase the culture of a people through various activities such as '
                                 'traditional dances, traditional food, traditional clothing, traditional music, etc.'
        },
    ]

    users_sql = "INSERT IGNORE INTO users(full_name, dob, mobile_no, campus, faculty,program, email, school_id, " \
                "date_joined, recovery_question, recovery_answer, password) VALUES (%(full_name)s, %(dob)s, " \
                "%(mobile_no)s, %(campus)s, %(faculty)s, %(program)s, %(email)s, %(school_id)s, %(date_joined)s, " \
                "%(recovery_question)s, %(recovery_answer)s, %(password)s)"

    users_val = [
        {
            'full_name': 'John Doe',
            'dob': '1998-01-01',
            'mobile_no': '+254721345589',
            'campus': 'Langata',
            'faculty': 'Science',
            'program': 'Computer Science',
            'email': 'johndoe@cuea.edu',
            'school_id': '12345678',
            'date_joined': '2021-01-01',
            'recovery_question': 'What is your favourite color?',
            'recovery_answer': 'Blue',
            'password': '1234567'
        }
    ]

    # try except block to insert data into the tables
    try:
        for lecturer in lecturer_val:
            mycursor.execute(lecturer_sql, lecturer)
        for timetable in timetable_val:
            mycursor.execute(timetable_sql, timetable)
        for events in events_val:
            mycursor.execute(events_sql, events)
        for users in users_val:
            mycursor.execute(users_sql, users)

        print("Data Inserted Successfully")

    except mysql.connector.Error as sqlerror:
        print("Error Inserting Data: {}".format(sqlerror))

    mydb.commit()
    mydb.close()
