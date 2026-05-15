from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import (
    LoginManager,
    UserMixin,
    login_user,
    login_required,
    logout_user,
    current_user
)
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)

app.config['SECRET_KEY'] = 'secretkey'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///employees.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# LOGIN MANAGER
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'


# ---------------- ADMIN MODEL ----------------

class Admin(UserMixin, db.Model):

    id = db.Column(db.Integer, primary_key=True)

    username = db.Column(db.String(100), unique=True)

    password = db.Column(db.String(300))


# ---------------- EMPLOYEE MODEL ----------------

class Employee(db.Model):

    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(db.String(100), nullable=False)

    email = db.Column(db.String(100), unique=True, nullable=False)

    department = db.Column(db.String(100), nullable=False)

    salary = db.Column(db.Integer, nullable=False)


# ---------------- CREATE DATABASE ----------------

with app.app_context():

    db.create_all()

    # Default admin
    if not Admin.query.filter_by(username='admin').first():

        admin = Admin(
            username='admin',
            password=generate_password_hash('admin123')
        )

        db.session.add(admin)
        db.session.commit()


# ---------------- LOGIN MANAGER ----------------

@login_manager.user_loader
def load_user(user_id):

    return Admin.query.get(int(user_id))


# ---------------- LOGIN ----------------

@app.route('/', methods=['GET', 'POST'])
def login():

    if request.method == 'POST':

        username = request.form['username']

        password = request.form['password']

        admin = Admin.query.filter_by(username=username).first()

        if admin and check_password_hash(admin.password, password):

            login_user(admin)

            return redirect(url_for('dashboard'))

        else:

            flash("Invalid username or password")

    return render_template('login.html')


# ---------------- DASHBOARD ----------------

@app.route('/dashboard')
@login_required
def dashboard():

    employees = Employee.query.all()

    return render_template(
        'dashboard.html',
        employees=employees
    )


# ---------------- ADD EMPLOYEE ----------------

@app.route('/add', methods=['GET', 'POST'])
@login_required
def add_employee():

    if request.method == 'POST':

        name = request.form['name']

        email = request.form['email']

        department = request.form['department']

        salary = request.form['salary']

        # VALIDATION
        if Employee.query.filter_by(email=email).first():

            flash("Email already exists")

            return redirect(url_for('add_employee'))

        employee = Employee(
            name=name,
            email=email,
            department=department,
            salary=salary
        )

        db.session.add(employee)

        db.session.commit()

        return redirect(url_for('dashboard'))

    return render_template('add_employee.html')


# ---------------- EDIT EMPLOYEE ----------------

@app.route('/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_employee(id):

    employee = Employee.query.get_or_404(id)

    if request.method == 'POST':

        employee.name = request.form['name']

        employee.email = request.form['email']

        employee.department = request.form['department']

        employee.salary = request.form['salary']

        db.session.commit()

        return redirect(url_for('dashboard'))

    return render_template(
        'edit_employee.html',
        employee=employee
    )


# ---------------- DELETE EMPLOYEE ----------------

@app.route('/delete/<int:id>')
@login_required
def delete_employee(id):

    employee = Employee.query.get_or_404(id)

    db.session.delete(employee)

    db.session.commit()

    return redirect(url_for('dashboard'))


# ---------------- LOGOUT ----------------

@app.route('/logout')
@login_required
def logout():

    logout_user()

    return redirect(url_for('login'))


# ---------------- RUN ----------------

if __name__ == '__main__':

    app.run(debug=True)