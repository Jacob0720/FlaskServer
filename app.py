import csv
import os
import python_utils
from flask import Flask, render_template, redirect, url_for, request
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from sqlalchemy.sql import func

from mysql.connector import connect, Error
from datetime import datetime, timedelta

app = Flask(__name__)
app.config['TEMPLATES_AUTO_RELOAD'] = True

## SQL DATA BASE GETS INSERTED HERE
##app.config['SQLALCHEMY_DATABASE_URI'] = " "

##db = SQLAlchemy(app)


login_manager = LoginManager(app)
login_manager.init_app(app)


class User(UserMixin):
    def __init__(self, id):
        self.id = id


def load_users():
    users = {}
    with open('users.csv', 'r') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            users[row['username']] = row['password']
    return users


users = load_users()

def user_loader(self, callback):
    self._user_callback = callback
    return self._user_callback

def request_loader(self, callback):
    self._request_callback = callback
    return self._request_callback


def load_user(user_id):
    return User.get(int(user_id))


@app.route('/')
def home():
    ## THIS WILL BE THE HOME TEMPLATE OF HTML PAGE
    return "WELCOME TO AIRES TESTING HOME PAGE"
    ##return render_template('home.html')


@app.route('/<login>', methods=['GET', 'POST'])
def login(login):
    if request.method == 'POST':
        user_id = request.form['username']
        password = request.form['password']

        if user_id in users and password == users[user_id]:
            user = User(user_id)
            login_user(user)
            return redirect(url_for('profile'))
        else:
            return 'Login Failed'

    return "LOGIN FUNCTIONS TO BE IMPLEMENTED"
    ##return render_template('login.html')


def create_db_connection():
    try:
        #connection = connect(
         #   host="localhost",
         #   user="ADMIN",
         #   password="password",
         #   database="parku",
        #)
        connection = connect(
            host="10.31.33.29",
            user="gabriel",
            password="Torres0826",
            database="parku",
        )
        print("Successfully connected to database")
        return connection
    except Error as e:
        print(e)
        return None


def add_entry_to_parking_lots(connection, lot_id, name, location, capacity):
    try:
        cursor = connection.cursor()
        insert_query = """
        INSERT INTO ParkingLots (lot_id, name, location, capacity) 
        VALUES (%s, %s, %s, %s)
        """
        data_to_insert = (lot_id, name, location, capacity)

        cursor.execute(insert_query, data_to_insert)
        connection.commit()
        print("Entry added to ParkingLots successfully!")

    except Error as e:
        print(e)


def add_entry_to_parking_spots(connection, spot_id, lot_id, status, type):
    try:
        cursor = connection.cursor()
        insert_query = """
        INSERT INTO ParkingSpots (spot_id, lot_id, status, type) 
        VALUES (%s, %s, %s, %s)
        """
        data_to_insert = (spot_id, lot_id, status, type)

        cursor.execute(insert_query, data_to_insert)
        connection.commit()
        print("Entry added to ParkingSpots successfully!")

    except Error as e:
        print(e)

def update_parking_spot(connection, spot_id, new_status):
    try:
        cursor = connection.cursor()

        # Get the current timestamp as a Python datetime object
        current_timestamp = datetime.now()

        # Fetch the last timestamp from the database for the spot
        select_last_timestamp_query = """
        SELECT last_time_in
        FROM ParkingSpots
        WHERE spot_id = %(spot_id)s
        """
        cursor.execute(select_last_timestamp_query, {'spot_id': spot_id})
        result = cursor.fetchone()

        if result:
            last_timestamp = result[0]
        else:
            last_timestamp = None

        # Calculate the duration if last_timestamp is not None
        if last_timestamp:
            duration = current_timestamp - last_timestamp
        else:
            duration = timedelta(seconds=0)  # Default to 0 if no last_timestamp

        # Define your SQL UPDATE statement with named placeholders
        update_query = """
        UPDATE ParkingSpots
        SET status = %(new_status)s,
            current_time_in = IF(%(new_status)s = 1, %(current_timestamp)s, current_time_in),
            current_time_out = IF(%(new_status)s = 0, %(current_timestamp)s, current_time_out),
            last_time_in = IF(CAST(%(new_status)s AS SIGNED) <> 1 AND current_time_in IS NOT NULL, %(current_timestamp)s, last_time_in),
            last_time_out = IF(CAST(%(new_status)s AS SIGNED) <> 0 AND current_time_out IS NOT NULL, %(current_timestamp)s, last_time_out),
            current_duration = %(duration)s
        WHERE spot_id = %(spot_id)s
        """

        # Conditionally set new_status as 1 or 0
        new_status_value = 1 if new_status else 0

        # Define a dictionary of values to replace the named placeholders
        data_to_update = {
            'new_status': new_status_value,
            'current_timestamp': current_timestamp,
            'duration': duration.total_seconds(),
            'spot_id': spot_id
        }

        # Print the generated query for debugging
        print("Generated Query:")
        print(update_query)

        # Execute the UPDATE statement with the provided values
        cursor.execute(update_query, data_to_update)

        # Commit the transaction to save the changes to the database
        connection.commit()

        print("Parking spot updated successfully!")

    except Error as e:
        print(e)


def update_spots_in_use_and_available(connection):
    try:
        cursor = connection.cursor()

        # Update the spots_in_use column in ParkingLots table
        update_spots_in_use_query = """
        UPDATE ParkingLots
        SET spots_in_use = (
            SELECT COUNT(*) 
            FROM ParkingSpots 
            WHERE ParkingSpots.lot_id = ParkingLots.lot_id
            AND ParkingSpots.status = 1
        )
        """
        cursor.execute(update_spots_in_use_query)

        # Update the spots_available column in ParkingLots table
        update_spots_available_query = """
        UPDATE ParkingLots
        SET spots_available = (capacity - spots_in_use)
        """
        cursor.execute(update_spots_available_query)

        # Commit the transaction to save the changes to the database
        connection.commit()

        print("Database has been updated!")

    except Error as e:
        print(e)


# Begin database entry
connection = create_db_connection()

if connection:
    update_parking_spot(connection, 1, False)
    update_parking_spot(connection, 2, False)
    update_spots_in_use_and_available(connection)

if connection:
    connection.close()


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
