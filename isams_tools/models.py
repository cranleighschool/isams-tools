class Teacher():
    id = ""
    forename = ""
    surname = ""
    username = ""
    email = ""
    status = 0

    def __init__(self, forename, surname, email, title=None, sync_value=None, status=1, username=None, id=None):
        self.id = id
        self.sync_value = sync_value
        self.forename = forename
        self.surname = surname
        self.username = username
        self.title = title
        self.email = email
        if status < 1 or status == 'False':
            self.status = False
        else:
            self.status = True


    def __str__(self):
        return("forename={0}, surname={1}, title={2}, email={3}, sync_value={4}, status={5}".format(self.forename, self.surname, self.title, self.email, self.sync_value, self.status))

    def __eq__(self, other):
        equal = True
        if self.forename != other.forename:
            equal = False
        
        if self.surname != other.surname:
            equal = False
        
        # if self.title != other.forename:
        #     equal = False
        
        # if self.email != other.forename:
        #     equal = False
        
        if self.sync_value != other.sync_value:
            equal = False
        
        if self.status != other.status:
            equal = False

        return equal

    def __ne__(self, other):
        equal = True
        if self.forename != other.forename:
            equal = False
        
        if self.surname != other.surname:
            equal = False
        
        # if self.title != other.forename:
        #     equal = False
        
        # if self.email != other.forename:
        #     equal = False
        
        if self.sync_value != other.sync_value:
            equal = False
        
        if self.status != other.status:
            equal = False

        return not equal
        


class Student():
    sync_value = None
    forename = None
    surname = None
    username = None
    email = None
    nc_year = None
    form = None
    gender = None
    id = None
    status = None

    def __init__(self, forename, surname, nc_year, form=None, username=None, email=None,
                 date_of_birth=None, gender=None, sync_value=None, status=None, id=None):
        self.forename = forename
        self.surname = surname
        self.username = username
        self.email = email
        self.nc_year = nc_year
        self.form = form
        self.date_of_birth = date_of_birth
        self.gender = gender
        self.sync_value = sync_value
        self.id = id
        self.status = status

    def __str__(self):
        return "(sv:{0}, f:{1}, s:{2}, u:{3}, e:{4}, ay:{5} form:{6})".\
            format(self.sync_value, self.forename, self.surname, self.username, self.email, self.nc_year, self.form)

class Form():
    name = None
    teacher = None
    nc_year = None

    def __init__(self, name, teacher, nc_year):
        self.name = name
        self.teacher = teacher
        self.nc_year = nc_year

    def __str__(self):
        return ("({0}, {1}, {2})".format(self.name, self.teacher, self.nc_year))

class YearGroup():
    name = None
    code = None
    nc_year = None
    head_of_year = None

    def __init__(self, name, code, nc_year, head_of_year=None):
        self.name = name
        self.code = code
        self.nc_year = nc_year
        self.head_of_year = head_of_year

class Set():
    name = None
    teacher = None
    nc_year = None
    sync_value = None
    subject = None

    def __init__(self, name, teacher=None, nc_year=None, subject=None, sync_value=None):
        self.name = name
        self.teacher = teacher
        self.nc_year = nc_year
        self.subject = subject
        self.sync_value = sync_value


class Setlist():
    sync_value = None
    set = None
    student = None
    submitted_by = None
    submitted_date = None

    def __init__(self, set, student, submitted_by=None, submitted_date=None, sync_value=None):
        self.set = set
        self.student = student
        self.submitted_by = submitted_by
        self.submitted_date submitted_date
        self.sync_value = sync_value


class Department():
    name = None
    code = None
    head_of_department = None
    sync_value = None

    def __init__(self, name, code, head_of_department=None, sync_value=None):
        self.name = name
        self.code = code
        self.head_of_department = head_of_department
        self.sync_value = sync_value

class Subject():
    name = None
    code = None
    department_sync_value = None
    sync_value = None
    department = None

    def __init__(self, name, code=None, subject_leaders=None, department=None, sync_value=None):
        self.name = name
        self.code = code
        self.subject_leaders = subject_leaders
        self.department = department
        self.sync_value = sync_value

