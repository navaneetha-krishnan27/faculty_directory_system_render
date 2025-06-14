from flask import Flask, render_template, request, redirect, session
from flask_mysqldb import MySQL
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY')

# MySQL Configuration
app.config['MYSQL_HOST'] = os.getenv('MYSQL_HOST')
app.config['MYSQL_USER'] = os.getenv('MYSQL_USER')
app.config['MYSQL_PASSWORD'] = os.getenv('MYSQL_PASSWORD')
app.config['MYSQL_DB'] = os.getenv('MYSQL_DB')

mysql = MySQL(app)

@app.route('/')
def faculty_home():
    return render_template('faculty_home.html')

@app.route('/showfaculty')
def show_faculty():
    page = request.args.get('page', default=1, type=int)
    per_page = 6
    offset = (page - 1) * per_page

    cur = mysql.connection.cursor()
    cur.execute("SELECT COUNT(*) FROM faculty")
    total_records = cur.fetchone()[0]
    total_pages = (total_records + per_page - 1) // per_page

    cur.execute("SELECT id, name, title, department, photo FROM faculty LIMIT %s OFFSET %s", (per_page, offset))
    faculty_list = cur.fetchall()

    return render_template('faculty_list.html', faculty=faculty_list, page=page, total_pages=total_pages)

@app.route('/faculty/<int:id>')
def view_profile(id):
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM faculty WHERE id = %s", (id,))
    faculty = cur.fetchone()
    return render_template('faculty_profile.html', faculty=faculty)

@app.route('/about')
def about():
    return render_template('faculty_about.html')

@app.route('/search')
def search():
    query = request.args.get('query', '')
    if not query.strip():
        return redirect('/showfaculty')

    cur = mysql.connection.cursor()
    cur.execute("""
        SELECT id, name, title, department, photo 
        FROM faculty 
        WHERE name LIKE %s OR department LIKE %s
    """, (f"%{query}%", f"%{query}%"))

    results = cur.fetchall()
    return render_template('faculty_list.html', faculty=results, page=1, total_pages=1)

@app.route('/admin_search')
def admin_search():
    if not session.get('admin'):
        return redirect('/login')

    query = request.args.get('query', '')
    if not query.strip():
        return redirect('/admin_dashboard')

    cur = mysql.connection.cursor()
    cur.execute("""
        SELECT id, name, title, department, photo 
        FROM faculty 
        WHERE name LIKE %s OR department LIKE %s
    """, (f"%{query}%", f"%{query}%"))

    results = cur.fetchall()
    return render_template('admin_dasboard.html', faculty=results)

@app.route('/add', methods=['GET', 'POST'])
def add_faculty():
    if not session.get('admin'):
        return redirect('/login')

    if request.method == 'POST':
        name = request.form['name']
        title = request.form['title']
        department = request.form['department']
        email = request.form['email']
        phone = request.form['phone']
        bio = request.form['bio']
        photo = request.files['photo']

        filename = photo.filename
        photo.save(os.path.join('static/photos/', filename))

        cur = mysql.connection.cursor()
        cur.execute("""INSERT INTO faculty 
                       (name, title, department, email, phone, bio, photo) 
                       VALUES (%s, %s, %s, %s, %s, %s, %s)""",
                    (name, title, department, email, phone, bio, filename))
        mysql.connection.commit()
        return redirect('/admin_dashboard')

    return render_template('add_faculty.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if username == 'admin' and password == 'admin123':
            session['admin'] = True
            return redirect('/admin_dashboard')
        else:
            error = 'Invalid credentials'

    return render_template('login.html', error=error)

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/login')

@app.route('/admin_dashboard')
def admin_dashboard():
    if not session.get('admin'):
        return redirect('/login')
    cur = mysql.connection.cursor()
    cur.execute("SELECT id, name, title, department, photo FROM faculty")
    faculty = cur.fetchall()
    return render_template('admin_dasboard.html', faculty=faculty)

@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit_faculty(id):
    if not session.get('admin'):
        return redirect('/login')

    cur = mysql.connection.cursor()

    if request.method == 'POST':
        name = request.form['name']
        title = request.form['title']
        department = request.form['department']
        email = request.form['email']
        phone = request.form['phone']
        bio = request.form['bio']

        cur.execute("""
            UPDATE faculty
            SET name=%s, title=%s, department=%s, email=%s, phone=%s, bio=%s
            WHERE id=%s
        """, (name, title, department, email, phone, bio, id))
        mysql.connection.commit()
        return redirect('/admin_dashboard')

    cur.execute("SELECT * FROM faculty WHERE id = %s", (id,))
    faculty = cur.fetchone()
    return render_template('edit_faculty.html', faculty=faculty)

@app.route('/delete/<int:id>')
def delete_faculty(id):
    if not session.get('admin'):
        return redirect('/login')
    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM faculty WHERE id = %s", (id,))
    mysql.connection.commit()
    return redirect('/admin_dashboard')

if __name__ == '__main__':
    app.run(debug=True)
