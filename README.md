iSAMS Tools README
==================

**Register Reminder**
Sends emails to tutors who have not registered all students.

Requirements: iSAMS (with Batch API key setup, see below), Python 3, modules from requirements.txt, postfix/sendmail

1. Edit `settings_example.py` and rename it to `settings.py`
1. Add the modules in the Batch API settings as shown below
1. Add entries to crontab, e.g. 

**iSAMS Requirements**
In your Batch methods, you need to enable the following:
* HRManager:CurrentStaff
* PupilManager:CurrentPupils
* RegistrationManager:RegistrationStatuses
* SchoolManager:Forms