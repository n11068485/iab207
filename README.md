\# EventSphere — IAB207 Assignment 2



A Flask-based Event Management System developed as part of QUT IAB207 

Rapid Web Application Development.



\## Group Members

\- Sebastian

\- Khas

\- Naadirah



\## Overview

EventSphere allows users to browse, create, and book tickets for events 

across a range of industry sectors. Users can register, log in, post 

comments on events, and manage their bookings through a booking history 

page. Event creators can include an Acknowledgement of Country 

(Generic or Enhanced) on their event page.



\## Features

\- Browse and filter events by sector and status

\- User registration and login with password hashing (bcrypt)

\- Event creation, editing, and cancellation

\- Ticket booking with order ID confirmation

\- Overbooking prevention and automatic Sold Out status

\- Comment system on event detail pages

\- Acknowledgement of Country (None / Generic / Enhanced)

\- Booking history for logged-in users

\- Custom 404 and 500 error pages



\## Tech Stack

\- Python 3

\- Flask, Flask-WTF, Flask-SQLAlchemy, Flask-Login, Bootstrap-Flask, Flask-Bcrypt

\- WTForms with email-validator

\- SQLAlchemy (SQLite)

\- Bootstrap 5

\- Werkzeug



\## Setup Instructions



\### 1. Clone the repository

git clone https://github.com/n11068485/iab207.git

cd iab207

git checkout assessment2



\### 2. Create and activate a virtual environment

python -m venv venv



\# Windows:

venv\\Scripts\\activate



\# Mac/Linux:

source venv/bin/activate



\### 3. Install dependencies

pip install -r requirements.txt



\### 4. Run the application

python main.py



Visit http://127.0.0.1:5000 in your browser.



\## Folder Structure

iab207/

├── website/               # Main application package

│   ├── static/            # CSS, images and other static assets

│   ├── templates/         # Jinja2 HTML templates

│   ├── \_\_init\_\_.py        # App factory and error handlers

│   ├── models.py          # SQLAlchemy database models

│   ├── views.py           # Main routes and blueprint

│   ├── auth.py            # Authentication routes

│   └── forms.py           # WTForms form definitions

├── instance/

│   └── sitedata.sqlite    # SQLite database (auto-generated on first run)

├── main.py                # Application entry point

├── requirements.txt       # Python dependencies

└── README.md              # This file



\## Error Pages

\- 404 Not Found — visit any undefined route e.g. /definitelynotapage

\- 500 Internal Server Error — set debug=False in main.py to test



\## Image Credits

All images sourced from Pexels or used under Creative Commons licence 

for educational purposes.

