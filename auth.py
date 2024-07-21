from flask import Blueprint, render_template, request, flash, redirect, url_for
from .models import User, Note, Lecture
from werkzeug.security import generate_password_hash, check_password_hash
from . import db
from flask_login import login_user, login_required, logout_user, current_user
from .capture_image import takeImages
from .recognize import recognize_attendance
import csv
import os
from flask import send_file


auth = Blueprint('auth', __name__)

@auth.route('/signup/', methods=['GET', 'POST'])
def sign_up():
    if request.method == 'POST':
        role = request.form.get('role')
        student_id = request.form.get('student_id') if role == 'student' else None
        email = request.form.get('email')
        first_name = request.form.get('firstname')
        last_name = request.form.get('lastname')
        password1 = request.form.get('password1')
        password2 = request.form.get('password2')

        user = User.query.filter_by(email=email).first()
        if user:
            flash('Email already exists', category='error')
        elif len(email) < 4:
            flash('Email must be greater than 3 characters.', category='error')
        elif len(first_name) < 2 or len(last_name) < 2:
            flash('First name must be greater than 1 character.', category='error')
        elif password1 != password2:
            flash('Passwords don\'t match.', category='error')
        elif len(password1) < 7:
            flash('Password must be at least 7 characters.', category='error')
        elif role == 'student' and len(student_id) == 0:
            flash('Student ID is required for students.', category='error')
        else:
            new_user = User(
                email=email,
                password=generate_password_hash(password1, method='pbkdf2:sha256'),
                first_name=first_name,
                last_name=last_name,
                role=role,
                student_id=student_id
            )
            db.session.add(new_user)
            db.session.commit()
            login_user(new_user, remember=True)
            flash('Account created', category='success')
            if role == 'student':
                return redirect(url_for('views.homeStudent'))
            elif role == 'doctor':
                return redirect(url_for('views.homeDoctor'))

    return render_template("sign_up.html", user=current_user)

@auth.route('/login/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        role = request.form.get('role')
        password = request.form.get('password')

        if role == 'doctor':
            email = request.form.get('email')
            user = User.query.filter_by(email=email).first()
            if user and check_password_hash(user.password, password):
                flash("Successfully logged in!", category='success')
                login_user(user, remember=True)
                return redirect(url_for('views.homeDoctor'))
            else:
                flash('Incorrect credentials, try again', category='error')

        elif role == 'student':
            student_id = request.form.get('student_id')
            user = User.query.filter_by(student_id=student_id).first()
            if user and check_password_hash(user.password, password):
                flash("Successfully logged in!", category='success')
                login_user(user, remember=True)
                return redirect(url_for('views.homeStudent'))
            else:
                flash('Incorrect credentials, try again', category='error')

    return render_template("login.html", user=current_user)

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))

@auth.route('/update/<int:id>', methods=['POST'])
@login_required
def update(id):
    user = User.query.get(id)
    if user:
        user.email = request.form.get('email')
        user.first_name = request.form.get('firstname')
        user.last_name = request.form.get('lastname')
        password1 = request.form.get('password1')
        password2 = request.form.get('password2')
        
        if password1 and password1 == password2:
            user.password = generate_password_hash(password1, method='pbkdf2:sha256')
        elif password1 and password1 != password2:
            flash("Passwords don't match.", category='error')
            return redirect(url_for('views.profile_std', id=id))
        
        db.session.commit()
        flash('Profile has been updated successfully!', category='success')
        return redirect(url_for('views.profile_std'))
    else:
        flash('User not found.', category='error')
        return redirect(url_for('auth.edit_profile_std', id=id))


@auth.route('/CaptureFace/<int:id>', methods=['GET', 'POST'])
@login_required
def capture_face_route(id):
    user = User.query.get(id)
    if user:
        message = takeImages(str(user.student_id), user.first_name)
        flash(message, category='success' if "Saved" in message else 'error')
    else:
        flash('User not found.', category='error')

    return render_template("CaptureFace.html", user=current_user)


@auth.route('/recognize/<int:id>', methods=['GET', 'POST'])
@login_required
def recognize(id):
    course = request.form.get('course')
    time = request.form.get('time')

    message, csv_file = recognize_attendance(time)

    print(course)
    if message:
        return send_file(csv_file, as_attachment=True)
    else:
        flash(message, category='error')
        return render_template("lec.html", user=current_user)

@auth.route('/download_csv/<int:lecture_id>', methods=['GET'])
@login_required
def download_csv(lecture_id):
    lecture = Lecture.query.get_or_404(lecture_id)
    if lecture.csv_path:
        return send_file(lecture.csv_path, as_attachment=True)
    else:
        flash("CSV file not found.", category='error')
        return redirect(url_for('views.home'))