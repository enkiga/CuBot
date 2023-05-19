import mysql.connector

# Connect to Database
mydb = mysql.connector.connect(
    host="localhost",
    port="3306",
    user="root",
    password="K1pk0r1r!",
    database="cueabot"
)

# Create Cursor
mycursor = mydb.cursor()


# Create Tables
def createTables():
    usersTB = "create table if not exists users"
    "(user_no int auto_increment,"
    "username varchar(20) not null unique, "
    "full_name varchar(100) not null,"
    "dob date not null,"
    "mobile_no varchar(13) not null unique,"
    "campus varchar(10)  not null,"
    "faculty varchar(50) not null,"
    "program varchar(200) not null,"
    "email varchar(20) not null unique,"
    "school_id int not null primary key unique,"
    "date_joined date not null,"
    "recovery_question varchar(500) not null,"
    "recovery_answer varchar(100) not null,"
    "password varchar(50)  not null)"

    conversationsTB = "create table if not exists conversations"
    "(conversation_no int auto_increment,"
    "user_id int not null,"
    "message_sent varchar(500) not null,"
    "message_received varchar(500) not null,"
    "date_sent date not null,"
    "time_sent time not null,"
    "primary key(conversation_no),"
    "foreign key(user_id) references usersTB(school_id))"

    lecturersTB = "create table if not exists lecturers"
    "(lecturer_no int auto_increment,"
    "lecturer_name varchar(100) not null,"
    "lecturer_email varchar(100) not null unique,"
    "lecturer_phone varchar(13) not null unique,"
    "lecturer_campus varchar(10) not null,"
    "lecturer_office varchar(100) not null,"
    "lecturer_department varchar(100) not null,"
    "lecturer_faculty varchar(100) not null,"
    "primary key(lecturer_no))"

    timetableTB = "create table if not exists timetable"
    "(timetable_no int auto_increment,"
    "course_code varchar(10) not null,"
    "course_title varchar(100) not null,"
    "course_lecturer varchar(100) not null,"
    "course_venue varchar(100) not null,"
    "course_day varchar(10) not null,"
    "course_time varchar(10) not null,"
    "primary key(timetable_no),"
    "foreign key(course_lecturer) references lecturerTB(lecturer_name))"

    eventsTB = "create table if not exists events"
    "(event_no int auto_increment,"
    "event_name varchar(100) not null,"
    "event_venue varchar(100) not null,"
    "event_date date not null,"
    "event_time time not null,"
    "event_description varchar(500) not null,"
    "primary key(event_no))"




