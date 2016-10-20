from flask import Flask
import os, sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from isams_tools.connectors.isams import iSAMSConnection
from settings import DATABASE, DATABASE_USER, DATABASE_PASS, DATABASE_SERVER
app = Flask(__name__)

@app.route("/")
def hello():
    html = """

<link rel="stylesheet" href="//code.jquery.com/ui/1.12.1/themes/base/jquery-ui.css">
  <script src="https://code.jquery.com/jquery-1.12.4.js"></script>
  <script src="https://code.jquery.com/ui/1.12.1/jquery-ui.js"></script>
  <script>
  $( function() {
    var availableTags = [
      "ActionScript",
      "AppleScript",
      "Asp",
      "BASIC",
      "C",
      "C++",
      "Clojure",
      "COBOL",
      "ColdFusion",
      "Erlang",
      "Fortran",
      "Groovy",
      "Haskell",
      "Java",
      "JavaScript",
      "Lisp",
      "Perl",
      "PHP",
      "Python",
      "Ruby",
      "Scala",
      "Scheme"
    ];
    $( "#tags" ).autocomplete({
      source: availableTags
    });
  } );
  </script>
</head>
<body>

<div class="ui-widget">
  <label for="tags">Tags: </label>
  <input id="tags">
</div>

    <h1>iSAMS Quick Check</h1>
    <p>What <select><option>Form</option><option>Lesson</option></select> is
    <input id="provider-remote" />
     in?</p>
    """


    return html

@app.route('/lookup/<search>')
def show_user_profile(search):
    if len(search) > 2:
        query = """SELECT txtSchoolId, txtForename, txtSurname, txtForm FROM TblPupilManagementPupils
                   WHERE txtForename LIKE '%%%s%%' OR txtSurname LIKE '%%%s%%' """
        connection = iSAMSConnection(DATABASE_SERVER, DATABASE_USER, DATABASE_PASS, DATABASE)
        connection.connect()
        cursor = connection.cursor
        cursor.execute(query % (search, search))

        # show the user profile for that user
        return str(cursor.fetchall())


if __name__ == "__main__":
    app.run()