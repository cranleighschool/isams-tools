iSAMS Tools README
==================

**Register Reminder**
Sends emails to tutors who have not registered all students.

Requirements: iSAMS (with Batch API key setup, see below), Python 3, modules from requirements.txt, postfix/sendmail

1. Edit `settings_example.py` and rename it to `settings.py`
1. Add the modules in the Batch API settings as shown below
1. Add entries to crontab, as shown below

**iSAMS Requirements**
In your Batch methods, you need to enable the following:
* HRManager:CurrentStaff
* PupilManager:CurrentPupils
* RegistrationManager:RegistrationStatuses
* SchoolManager:Forms

**Example Crontab**
```bash
# runs the first reminder at 8am Monday-Friday
0 8 * * 1-5 /usr/bin/python3 /path/to/isams-tools/bin/isams_tools register_reminder 1 >/dev/null 2>&1 

# runs the second reminder at 8:30am Monday-Friday
30 8 * * 1-5 /usr/bin/python3 /path/to/isams-tools/bin/isams_tools register_reminder 2 >/dev/null 2>&1 

# runs the final reminder at 8:45am Monday-Friday
45 8 * * 1-5 /usr/bin/python3 /path/to/isams-tools/bin/isams_tools register_reminder 3 >/dev/null 2>&1
```