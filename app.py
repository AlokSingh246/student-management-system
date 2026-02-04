from flask import Flask, render_template, request, redirect, url_for, session
import mysql.connector

app = Flask(__name__)
app.secret_key = "replace_with_a_strong_secret_key"  # used for sessions
# Database connection helper
def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",      # or 'root' if that's what you used
        password="Alok@246",    # update accordingly
        database="student_db"
    )

# ----- Auth routes -----
@app.route('/')
def home():
    # Show login page
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def login():
    username = request.form['username'].strip()
    password = request.form['password'].strip()

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM users WHERE username=%s AND password=%s", (username, password))
    user = cursor.fetchone()
    cursor.close()
    conn.close()

    if user:
        session['username'] = username
        return redirect(url_for('dashboard'))
    return render_template('login.html', error="Invalid credentials")

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('home'))

# ----- Protected pages -----
@app.route('/dashboard')
def dashboard():
    if 'username' not in session:
        return redirect(url_for('home'))
    # Dashboard links to student management
    return render_template('dashboard.html')

@app.route('/students')
def students():
    if 'username' not in session:
        return redirect(url_for('home'))

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, age, course FROM students")
    data = cursor.fetchall()
    cursor.close()
    conn.close()

    return render_template('students.html', students=data)
@app.route('/add_student', methods=['POST'])
def add_student():
    if 'username' not in session:
        return redirect(url_for('home'))

    name = request.form.get('name', '').strip()
    age = request.form.get('age', '').strip()
    course = request.form.get('course', '').strip()

    # Validation
    if not name or not age.isdigit() or not course:
        # Always return something
        return redirect(url_for('students'))

    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO students (name, age, course) VALUES (%s, %s, %s)",
            (name, int(age), course)
        )
        conn.commit()
        cursor.close()
        conn.close()
    except Exception as e:
        # Return an error message instead of None
        return f"Error adding student: {e}"

# Always return a response
    return redirect(url_for('students'))

@app.route('/update_student/<int:id>', methods=['POST'])
def update_student(id):
    if 'username' not in session:
        return redirect(url_for('home'))

    new_course = request.form['course'].strip()

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE students SET course=%s WHERE id=%s", (new_course, id))
    conn.commit()
    cursor.close()
    conn.close()

    return redirect(url_for('students'))

@app.route('/delete_student/<int:id>', methods=['POST'])
def delete_student(id):
    if 'username' not in session:
        return redirect(url_for('home'))

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM students WHERE id=%s", (id,))
    conn.commit()
    cursor.close()
    conn.close()

    return redirect(url_for('students'))

if __name__ == '__main__':
    app.run(debug=True)


