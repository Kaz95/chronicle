from app import db
from app.auth import bp
from app.auth.forms import LoginForm, RegistrationForm
from app.models import User
from flask import render_template, redirect, url_for, flash, request
from werkzeug.urls import url_parse
from flask_login import current_user, login_user, logout_user


def auth_creds(username, password):
    user = User.query.filter_by(username=username).first()

    if user is None or not user.verify_password(password):
        return False
    return user


def validate_next_page(next_page):
    if not next_page or url_parse(next_page).netloc != '':
        return False
    return True


# TODO: RIP out logic
@bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))

    form = LoginForm()

    if form.validate_on_submit():
        # user = User.query.filter_by(username=form.username.data).first()

        # if user is None or not user.verify_password(form.password.data):
        user = auth_creds(form.username.data, form.password.data)
        if not user:
            flash('Invalid Username or Password')
            return redirect(url_for('auth.login'))

        login_user(user, remember=form.remember.data)
        next_page = request.args.get('next')

        # if not next_page or url_parse(next_page).netloc != '':
        #     next_page = url_for('main.home')

        if not validate_next_page(next_page):
            next_page = url_for('main.home')

        flash(f'User: {form.username.data} has logged in!')
        return redirect(next_page)

    return render_template('auth/login.html', title='Sign In', form=form)


# TODO: Test
@bp.route('/logout')
def logout():
    flash(f'User: {current_user.username} has logged out!')
    logout_user()
    return redirect(url_for('main.home'))


def create_user(username, password, conn):
    user = User()
    user.username = username
    user.hash_password(password)
    conn.session.add(user)
    conn.session.commit()


# TODO: RIP out logic
@bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))

    form = RegistrationForm()

    if form.validate_on_submit():
        # user = User()
        # user.username = form.username.data
        # user.hash_password(form.password.data)
        # db.session.add(user)
        # db.session.commit()
        create_user(form.username.data, form.password.data, db)
        flash('Congratulations, you are now a registered user!')
        return redirect(url_for('auth.login'))

    return render_template('auth/register.html', title='Register', form=form)
