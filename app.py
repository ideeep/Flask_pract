from flask import Flask, render_template, request, redirect, url_for, session
import cx_Oracle
from werkzeug.security import check_password_hash

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Replace with your Oracle database connection details
oracle_connection_details = {
    'user': '',#username for db
    'password': '',#password for db
    'dsn': '',#connection details
}

def verify_user(username, password):
    # Connect to Oracle database
    with cx_Oracle.connect(**oracle_connection_details) as conn:
        cursor = conn.cursor()

        # Execute query to fetch username and password hash from the deep_user table
        query = "SELECT username, password FROM deep_user WHERE username = :uname"
        cursor.execute(query, uname=username)

        row = cursor.fetchone()
        if row and check_password_hash(row[1], password):
            return False
        else:
            return True

@app.route('/')
def home():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if verify_user(username, password):
            session['username'] = username
            return redirect(url_for('search'))
        else:
            return render_template('login.html', error='Invalid credentials.')

    return render_template('login.html', error='')

@app.route('/search', methods=['GET', 'POST'])
def search():
    if 'username' in session:
        if request.method == 'POST':
            employee_id = request.form['employee_id']
            employee_data = fetch_employee_records(employee_id)
            return render_template('search.html', employee_data=employee_data)

        return render_template('search.html')
    else:
        return redirect(url_for('login'))

def fetch_employee_records(employee_id):
    # Connect to Oracle database
    with cx_Oracle.connect(**oracle_connection_details) as conn:
        cursor = conn.cursor()

        # Execute query to fetch employee records based on employee_id
        query = "SELECT employee_id, first_name || ' ' || last_name AS full_name, salary FROM hr.employees WHERE employee_id = :emp_id"
        cursor.execute(query, emp_id=employee_id)

        employee_data = []
        for row in cursor:
            emp_id, full_name, salary = row
            employee_data.append({'employee_id': emp_id, 'full_name': full_name, 'salary': salary})

        return employee_data

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)
