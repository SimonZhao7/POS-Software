# POS-Software
Tabulation software that is connected through Google Sheets

## WARNING: Make sure you create only ONE USER (Excluding Admin Superuser)
Creating more than one user will break the system

There is an error to prevent creating through the forms but not through the admin panel

# Setup
1. Open up the terminal 

2. Clone the repo with "git clone https://github.com/SimonZhao7/POS-Software.git"

3. cd into the project directory

4. pip install -r requirements.txt to install required dependencies

5. python manage.py migrate

6. python manage.py createsuperuser to create an admin superuser

7. python manage.py runserver
