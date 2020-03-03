from flask import render_template, redirect, url_for, flash, request
import flask
from app import app, db
from app.forms import LoginForm, RegistrationForm
from app.models import User, Strain
from flask_login import current_user, login_user, logout_user, login_required
from werkzeug.urls import url_parse


@app.route('/')
@app.route('/home')
@login_required
def home():
    return render_template('home.html', title='Home')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.verify_password(form.password.data):
            flash('Invalid Username or Password')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('home')
        flash(f'User: {form.username.data} has logged in!')
        print(next_page, '<----------------')
        return redirect(next_page)
    return render_template('login.html', title='Sign In', form=form)


@app.route('/logout')
def logout():
    flash(f'User: {current_user.username} has logged out!')
    logout_user()
    return redirect(url_for('home'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User()
        user.username = form.username.data
        user.hash_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, you are now a registered user!')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)


@app.route('/strains')
@login_required
def strains_list():
    page = request.args.get('page', 1, type=int)

    # strains = Strain.query.paginate(page, app.config['STRAINS_PER_PAGE'], False)
    strains = Strain.paginate_all(page, app)
    next_url = url_for('strains_list', page=strains.next_num) if strains.has_next else None
    prev_url = url_for('strains_list', page=strains.prev_num) if strains.has_prev else None
    return render_template('strains_list.html', title='Strains', strains_list=strains.items, next_url=next_url, prev_url=prev_url)


@app.route('/strains/tried')
@login_required
def tried_strains():
    page = request.args.get('page', 1, type=int)

    strains = current_user.tried.paginate(page, app.config['STRAINS_PER_PAGE'], False)
    next_url = url_for('tried_strains', page=strains.next_num) if strains.has_next else None
    prev_url = url_for('tried_strains', page=strains.prev_num) if strains.has_prev else None
    return render_template('strains_list.html', title='Tried', strains_list=strains.items, next_url=next_url, prev_url=prev_url)


@app.route('/strains/not_tried')
@login_required
def not_tried_strains():
    page = request.args.get('page', 1, type=int)
    strains = current_user.has_not_tried(page, app)
    next_url = url_for('not_tried_strains', page=strains.next_num) if strains.has_next else None
    prev_url = url_for('not_tried_strains', page=strains.prev_num) if strains.has_prev else None
    return render_template('strains_list.html', title='Not Tried', strains_list=strains.items, next_url=next_url, prev_url=prev_url)


@app.route('/search/<strain>')
@login_required
def searched_strains(strain):
    page = request.args.get('page', 1, type=int)
    strains = Strain.query.filter(Strain.name.like('%' + strain + '%')).paginate(page, app.config['STRAINS_PER_PAGE'], False)
    next_url = url_for('searched_strains', strain=strain, page=strains.next_num) if strains.has_next else None
    prev_url = url_for('searched_strains', strain=strain,  page=strains.prev_num) if strains.has_prev else None
    return render_template('strains_list.html', title='Search:' + strain, strains_list=strains.items, next_url=next_url, prev_url=prev_url)


@app.route('/strains/<strain_name>')
@login_required
def some_strain(strain_name):
    strain = Strain.query.filter_by(index=strain_name).first_or_404()
    return render_template('strain.html', title=strain.name, strain=strain)


@app.route('/try/<strain_name>')
@login_required
def try_strain(strain_name):
    strain = Strain.query.filter_by(name=strain_name).first()
    if strain is None:
        flash(f'Strain: {strain_name} not found')
        return redirect(url_for('home'))

    current_user.try_strain(strain)
    db.session.commit()
    flash(f'Strain: {strain_name} has been tried')
    return redirect(url_for('some_strain', strain_name=strain.index))


@app.route('/untry/<strain_name>')
@login_required
def untry_strain(strain_name):
    strain = Strain.query.filter_by(name=strain_name).first()
    if strain is None:
        flash(f'Strain: {strain_name} not found')
        return redirect(url_for('home'))

    current_user.untry_strain(strain)
    db.session.commit()
    flash(f'Strain: {strain_name} has been tried')
    return redirect(url_for('some_strain', strain_name=strain.index))


# @app.route('/remote/<query>')
# def remote(query):
#     return flask.jsonify([i for i, in db.session.query(Strain.name).filter(Strain.name.like('%' + query + '%')).limit(5)])


@app.route('/remote/<query>')
def remote(query):
    print(query)
    q = db.session.query(Strain.name).filter(Strain.name.like(query + '%'))
    count = q.count()
    if count >= app.config['SEARCH_RESULTS']:
        return flask.jsonify([i for i, in q.limit(app.config['SEARCH_RESULTS']).all()])
    else:
        first_query = [i for i, in q.all()]
        q2 = db.session.query(Strain.name).filter(Strain.name.like('%' + query + '%'))
        # results = q.all() + q2.limit(app.config['SEARCH_RESULTS'] - count).all()
        results = first_query + [i for i, in q2.limit(app.config['SEARCH_RESULTS'] - count).all() if i not in first_query]

        print(results)
        return flask.jsonify(results)


# @app.route('/test')
# def test():
#     query = request.args.get('query')
#     q = db.session.query(Strain.name).filter(Strain.name.like(query + '%'))
#     count = q.count()
#     if count >= app.config['SEARCH_RESULTS']:
#         return flask.jsonify([i for i, in q.limit(app.config['SEARCH_RESULTS']).all()])
#     else:
#         first_query = [i for i, in q.all()]
#         q2 = db.session.query(Strain.name).filter(Strain.name.like('%' + query + '%'))
#         results = q.all() + q2.limit(app.config['SEARCH_RESULTS'] - count).all()
        # results = first_query + [i for i, in q2.limit(app.config['SEARCH_RESULTS'] - count).all() if
        #                          i not in first_query]
        #
        # print(results)
        # return flask.jsonify(results)


@app.route('/name_to_index')
def name_to_index():
    strain_name = request.args.get("name")
    strain_index = db.session.query(Strain.index).filter(Strain.name == strain_name).first_or_404()
    print(strain_index)
    return redirect(url_for('some_strain', strain_name=strain_index[0]))
