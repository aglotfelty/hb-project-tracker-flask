"""Hackbright Project Tracker.

A front-end for a database that allows users to work with students, class
projects, and the grades students receive in class projects.
"""

from flask import Flask
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


def connect_to_db(app):
    """Connect the database to our Flask app."""

    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///hackbright'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.app = app
    db.init_app(app)


def get_student_by_github(github):
    """Given a github account name, print information about the matching student."""

    QUERY = """
        SELECT first_name, last_name, github
        FROM students
        WHERE github = :github2
        """
    db_cursor = db.session.execute(QUERY, {'github2': github})
    row = db_cursor.fetchone()
    print "Student: %s %s\nGithub account: %s" % (row[0], row[1], row[2])

    return row


def make_new_student(first_name, last_name, github):
    """Add a new student and print confirmation.

    Given a first name, last name, and GitHub account, add student to the
    database and print a confirmation message.
    """

    QUERY = """
            INSERT INTO students
                VALUES (:first_name, :last_name, :github)
            """

    db.session.execute(QUERY, {'first_name': first_name,
                               'last_name': last_name,
                               'github': github})

    db.session.commit()

    print "Successfully added student: %s %s" % (first_name, last_name)


def make_new_project(title, description, max_grade):
    """Add a new project and print confirmation.

    Given a title, description, and max grade, add project to the
    database and print a confirmation message.
    """

    QUERY = """
            INSERT INTO projects (title, description, max_grade)
                VALUES (:title, :description, :max_grade)
            """

    db.session.execute(QUERY, {'title': title,
                               'description': description,
                               'max_grade': max_grade})

    db.session.commit()

    print "Successfully added project: %s" % (title)


def get_project_by_title(title):
    """Given a project title, print information about the project."""

    QUERY = """
            SELECT title, description, max_grade
                FROM projects
                WHERE title = :title
            """

    db_cursor = db.session.execute(QUERY, {'title': title})
    row = db_cursor.fetchone()

    print "Here's information about your %s project:" % row[0]
    print "Description: %s" % row[1]
    print "Max Grade: %s" % row[2]

    return row


def get_grade_by_github_title(github, title):
    """Return grade student received for a project."""

    QUERY = """
            SELECT s.first_name, s.last_name, g.grade
                FROM students AS s
                JOIN grades AS g ON (s.github = g.student_github)
                WHERE s.github = :github AND g.project_title = :title
            """

    db_cursor = db.session.execute(QUERY, {'title': title,
                                           'github': github})
    row = db_cursor.fetchone()

    print "%s %s's grade on %s is %s." % (row[0], row[1], title, row[2])

    return row


def get_grades_by_github(github):
    """Print grade student received for a project."""

    QUERY = """
            SELECT project_title, grade
                FROM grades
                WHERE student_github = :github
            """

    db_cursor = db.session.execute(QUERY, {'github': github})
    rows = db_cursor.fetchall()

    return rows


def get_grades_by_project(project):
    """Return students and grades they received for given project."""

    QUERY = """
            SELECT s.first_name, s.last_name, s.github, g.grade
                FROM students AS s
                JOIN grades AS g
                ON (s.github=g.student_github)
                WHERE g.project_title = :project
            """

    db_cursor = db.session.execute(QUERY, {'project': project})
    rows = db_cursor.fetchall()

    return rows


def assign_grade(github, title, grade):
    """Assign a student a grade on an assignment and print a confirmation.

    Github is the student's github and title is the project's title.
    If the student already has a grade for the project, the grade will be
    updated.
    """

    INSERT_QUERY = """
                   INSERT INTO grades (student_github, project_title, grade)
                   VALUES (:github, :title, :grade)
                   """
    UPDATE_QUERY = """
                   UPDATE grades
                   SET grade = :grade
                   WHERE student_github = :github
                   AND project_title = :title
                   """
    try:
        # Update grade if it already exists, insert a new record if it does not
        get_grade_by_github_title(github, title)
        db.session.execute(UPDATE_QUERY, {'grade': grade,
                                          'github': github,
                                          'title': title})
        db.session.commit()

        print "Successfully updated %s's grade for %s as %s." % (github,
                                                                 title,
                                                                 grade)
    except TypeError:
        db.session.execute(INSERT_QUERY, {'github': github,
                                          'title': title,
                                          'grade': grade})
        db.session.commit()

        print "Successfully added %s's grade for %s as %s." % (github,
                                                               title,
                                                               grade)



def get_students():
    """Gets a list of student names."""

    QUERY = """
            SELECT first_name, last_name, github
            FROM students
            """

    db_cursor = db.session.execute(QUERY)

    return db_cursor.fetchall()


def get_projects():
    """Gets a list of all project titles."""

    QUERY = """
            SELECT title FROM projects
            """

    db_cursor = db.session.execute(QUERY)

    return db_cursor.fetchall()


def handle_input():
    """Main loop.

    Repeatedly prompt for commands, performing them, until 'quit' is received as a
    command."""

    command = None

    while command != "quit":
        input_string = raw_input("HBA Database> ")
        tokens = input_string.split()
        command = tokens[0]
        args = tokens[1:]

        if command == "student":
            github = args[0]
            get_student_by_github(github)

        elif command == "new_student":
            first_name, last_name, github = args   # unpack!
            make_new_student(first_name, last_name, github)

        elif command == "get_project":
            title = " ".join(args[:])  # handle multi-word titles
            get_project_by_title(title)

        elif command == "get_grade":
            github = args[0]
            title = " ".join(args[1:])  # handle multi-word titles
            get_grade_by_github_title(github, title)

        elif command == "assign_grade":
            github = args[0]
            title = " ".join(args[1:-1])  # handle multi-word titles
            grade = args[-1]
            assign_grade(github, title, grade)

        else:
            if command != "quit":
                print "Invalid Entry. Try again."

if __name__ == "__main__":
    app = Flask(__name__)
    connect_to_db(app)

    # handle_input()

    db.session.close()
