class Teacher():
    id = ""
    forename = ""
    surname = ""
    username = ""
    email = ""

    def __init__(self, id, forename, surname, username, email):
        self.id = id
        self.forename = forename
        self.surname = surname
        self.username = username
        self.email = email


    def __str__(self):
        return ("({0}, {1}, {2})".format(self.forename, self.surname, self.email))


class Student():
    isams_id = None
    forename = None
    surname = None
    username = None
    email = None
    academic_year = None
    form = None

    def __init__(self, isams_id, forename, surname, username, email, academic_year, form, date_of_birth, gender, sync_id):
        self.isams_id = isams_id
        self.forename = forename
        self.surname = surname
        self.username = username
        self.email = email
        self.academic_year = academic_year
        self.form = form
        self.date_of_birth = date_of_birth
        self.gender = gender
        self.sync_id = sync_id

    def __str__(self):
        return "({0}, {1}, {2}, {3}, {4}, {5})".\
            format(self.isams_id, self.forename, self.surname, self.username, self.email, self.academic_year)

class Form():
    name = None
    teacher = None
    academic_year = None

    def __init__(self, name, teacher, academic_year):
        self.name = name
        self.teacher = teacher
        self.academic_year = academic_year

    def __str__(self):
        return ("({0}, {1}, {2})".format(self.name, self.teacher, self.academic_year))


class Set():
    name = None
    teacher = None
    nc_year = None
    sync_id = None
    subject_id = None


class SetList():
    sync_id = None
    set = None
    set_list = []
