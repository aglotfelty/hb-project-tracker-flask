from flask import Flask, request, render_template

import hackbright

app = Flask(__name__)


@app.route("/student")
def get_student():
    """Show information about a student."""

    github = request.args.get("github", "jhacks")

    first, last, github = hackbright.get_student_by_github(github)
    grades = hackbright.get_grades_by_github(github)

    html = render_template("student_info.html",
                           first=first,
                           last=last,
                           github=github,
                           grades=grades)

    return html


@app.route("/student-search")
def get_student_form():
    """Show form for searching for a student."""

    return render_template("student_search.html")



@app.route("/student-adder")
def add_a_student():
    """Shows a form for adding a new student to database."""

    return render_template("student_add.html")


@app.route("/student-added", methods=['POST'])
def student_added():
    """Add a student."""

    first_name = request.form.get("first_name")
    last_name = request.form.get("last_name")
    github = request.form.get("github")

    hackbright.make_new_student(first_name, last_name, github)

    return render_template("student_add_success.html", first_name=first_name,
                                                       last_name=last_name,
                                                       github=github)


@app.route("/project")
def display_project_info():
    """Display project information.

    Displays the title, description, and maximum grade of a project.
    """

    title = request.args.get("title")
    
    project_info = hackbright.get_project_by_title(title)
    student_grades = hackbright.get_grades_by_project(title)

    return render_template("project_info.html", project_info=project_info,
                                                student_grades=student_grades)


if __name__ == "__main__":
    hackbright.connect_to_db(app)
    app.run(debug=True)
