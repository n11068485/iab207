from flask import Blueprint, flash, render_template, request, url_for, redirect
from flask_bcrypt import generate_password_hash, check_password_hash
from flask_login import login_user, login_required, logout_user
from .models import User
from .forms import LoginForm, RegisterForm
from . import db

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    login_form = LoginForm()
    error = None
    if login_form.validate_on_submit():
        email = login_form.email.data
        password = login_form.password.data
        user = db.session.scalar(db.select(User).where(User.email == email))
        if user is None:
            error = 'No account found with that email'
        elif not check_password_hash(user.password_hash, password):
            error = 'Incorrect password'
        if error is None:
            login_user(user)
            nextp = request.args.get('next')
            if nextp is None or not nextp.startswith('/'):
                return redirect(url_for('main.index'))
            return redirect(nextp)
        else:
            flash(error, 'danger')
    return render_template('user.html', form=login_form, heading='Login')


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    # next is threaded through from the nav link so that after registering
    # and then logging in, the user lands back on the page they came from.
    nextp = request.args.get('next')
    register_form = RegisterForm()
    if register_form.validate_on_submit():
        existing = db.session.scalar(
            db.select(User).where(User.email == register_form.email.data))
        if existing:
            flash('An account with that email already exists.', 'danger')
            return render_template('user.html', form=register_form, heading='Register')
        hashed_pw = generate_password_hash(register_form.password.data)
        user = User(
            first_name=register_form.first_name.data,
            surname=register_form.surname.data,
            email=register_form.email.data,
            password_hash=hashed_pw,
            contact_number=register_form.contact_number.data,
            street_address=register_form.street_address.data,
        )
        db.session.add(user)
        db.session.commit()
        flash('Registration successful. Please log in.', 'success')
        if nextp and nextp.startswith('/'):
            return redirect(url_for('auth.login', next=nextp))
        return redirect(url_for('auth.login'))
    return render_template('user.html', form=register_form, heading='Register')


@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.index'))
