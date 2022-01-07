"""Hackbright Project Tracker.

A front-end for a database that allows users to work with students, class
projects, and the grades students receive in class projects.
"""

from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
db = SQLAlchemy()


def connect_to_db(app):
    """Connect the database to our Flask app."""

    # https://flask-sqlalchemy.palletsprojects.com/en/2.x/quickstart/
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///project-tracker'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.app = app
    db.init_app(app)


def get_student_by_github(github):
    """Given a GitHub account name, print info about the matching student."""

    QUERY = """
        SELECT first_name, last_name, github
        FROM students
        WHERE github = :github
        """

    db_cursor = db.session.execute(QUERY, {'github': github})
    # ...this code binds that result to a variable called db_cursor. 
    # A cursor is very similar to a file handler. 
    # For now, know that it is simply the mechanism that you'll use 
    # to look at the rows contained in the result from our query.

    row = db_cursor.fetchone()
    # returns a database row as a tuple-like object: ('Jane', 'Hacker', 'jhacks')

    first_name, last_name, github = row

    print(f"Student: {first_name} {last_name}\nGitHub account: {github}")


def make_new_student(first_name, last_name, github):
    """Add a new student and print confirmation.

    Given a first name, last name, and GitHub account, add student to the
    database and print a confirmation message.
    """
    
    QUERY = """
        INSERT INTO students (first_name, last_name, github)
            VALUES (:first_name, :last_name, :github)
        """

    db_cursor = db.session.execute(QUERY, {'first_name': first_name,
                                            'last_name': last_name,
                                            'github': github})

    db.session.commit()

    print(f"Successfully added {first_name} {last_name}.")


def get_project_by_title(title):
    """Given a project title, print information about the project.
    
    Here's the projects table schema:
    CREATE TABLE projects (
        id integer NOT NULL,
        title character varying(30),
        description text,
        max_grade integer
    """
    
    QUERY = """
        SELECT title, description, max_grade
        FROM projects
        WHERE title = :title
        """

    db_cursor = db.session.execute(QUERY, {'title': title})

    row = db_cursor.fetchone()

    title, description, max_grade = row

    print(f"{title}: {description}\nMax grade: {max_grade}")


def get_grade_by_github_title(github, title):
    """Print grade student received for a project.
    
    Here's the grades table schema:
    CREATE TABLE grades (
        id integer NOT NULL,
        student_github character varying(30),
        project_title character varying(30),
        grade integer);

    CREATE TABLE students (
        id integer NOT NULL,
        first_name character varying(30),
        last_name character varying(30),
        github character varying(30)

    SELECT students.first_name, students.last_name,
        grades.project_title,
        grades.grade FROM students
        JOIN grades ON (students.github = grades.student_github)
    """
    
    QUERY = """
        SELECT first_name, last_name, grade
        FROM students
        LEFT JOIN grades
        ON (grades.student_github = students.github)
        WHERE grades.project_title = :title AND grades.student_github = :github
        """

    db_cursor = db.session.execute(QUERY, {'github': github, 'title': title})

    row = db_cursor.fetchone()

    first_name, last_name, grade = row

    print(f"{first_name} {last_name}'s {title} project received {grade} points")


def assign_grade(github, title, grade):
    """Assign a student a grade on an assignment and print a confirmation.
    
    Here's the grades table schema:
    CREATE TABLE grades (
        id integer NOT NULL,
        student_github character varying(30),
        project_title character varying(30),
        grade integer);
    """
    
    QUERY = """
        INSERT INTO grades (student_github, project_title, grade)
            VALUES (:student_github, :project_title, :grade)
        """

    db_cursor = db.session.execute(QUERY, {'student_github': github,
                                            'project_title': title,
                                            'grade': grade})

    db.session.commit()

    print(f"Successfully graded {github}'s {title} project {grade} points.")


def handle_input():
    """Main loop.

    Repeatedly prompt for commands, performing them, until 'quit' is received
    as a command.
    """

    command = None

    while command != "quit":
        input_string = input("HBA Database> ")
        tokens = input_string.split()
        command = tokens[0]
        args = tokens[1:]

        if command == "student":
            github = args[0]
            get_student_by_github(github)

        elif command == "new_student":
            first_name, last_name, github = args  # unpack!
            make_new_student(first_name, last_name, github)

        else:
            if command != "quit":
                print("Invalid Entry. Try again.")


if __name__ == "__main__":
    connect_to_db(app)

    # handle_input()

    # To be tidy, we close our database connection -- though,
    # since this is where our program ends, we'd quit anyway.

    db.session.close()
