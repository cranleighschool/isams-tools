iSAMS Tools README
==================

**Register Reminder**

Sends emails to tutors who have not registered all students.

**Requirements**: iSAMS (with Batch API key setup, see below), Python 3, python packages from requirements.txt, postfix/sendmail
**Recommended**: Linux (but should work with any OS with Python and a command-line scheduler)

1. `iSAMS > Control Panel > API Services Manager > Manage Batch API Keys > Request Batch API Key`
1. Once you have a new API key, edit the Batch methods to include those in the *iSAMS Batch Method Requirements* section
1. Run `pip install -r requirements.txt` to install the required python packages (or `pip3` if you have Python 2 & 3 installed)
1. Edit `settings_example.py` and rename it to `settings.py`
1. Add entries to crontab, as shown below (for Windows you will probably need AT: https://support.microsoft.com/en-us/kb/313565)

**iSAMS Batch Method Requirements**

In your Batch API methods, you need to enable the following:

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