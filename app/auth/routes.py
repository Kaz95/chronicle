from app import db
from app.auth import bp
from app.auth.forms import LoginForm, RegistrationForm
from flask import render_template, redirect, url_for, flash, request
from flask_login import current_user, login_user, logout_user
from app import helper


# TODO: RIP out logic
@bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))

    form = LoginForm()

    if form.validate_on_submit():
        user = helper.auth_creds(form.username.data, form.password.data)
        if not user:
            flash('Invalid Username or Password')
            return redirect(url_for('auth.login'))

        login_user(user, remember=form.remember.data)
        next_page = request.args.get('next')

        if not helper.validate_next_page(next_page):
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


# TODO: RIP out logic
@bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))

    form = RegistrationForm()

    if form.validate_on_submit():
        u = helper.create_user(form.username.data, form.password.data)
        db.session.add(u)
        db.session.commit()
        flash('Congratulations, you are now a registered user!')
        return redirect(url_for('auth.login'))

    return render_template('auth/register.html', title='Register', form=form)
