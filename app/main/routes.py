from flask import render_template, redirect, url_for, flash, request, jsonify, current_app
from app import db
from app.models import Strain
from flask_login import current_user, login_required
from app.main import bp


@bp.route('/')
@bp.route('/home')
@login_required
def home():
    return render_template('home.html', title='Home')


@bp.route('/strains')
@login_required
def strains_list():
    page = request.args.get('page', 1, type=int)

    # strains = Strain.query.paginate(page, app.config['STRAINS_PER_PAGE'], False)
    strains = Strain.paginate_all(page, current_app)
    next_url = url_for('main.strains_list', page=strains.next_num) if strains.has_next else None
    prev_url = url_for(' main.strains_list', page=strains.prev_num) if strains.has_prev else None
    return render_template('strains_list.html', title='Strains', strains_list=strains.items, next_url=next_url, prev_url=prev_url)


# TODO: Change to query string
@bp.route('/strains/tried')
@login_required
def tried_strains():
    page = request.args.get('page', 1, type=int)

    strains = current_user.tried.paginate(page, current_app.config['STRAINS_PER_PAGE'], False)
    next_url = url_for('main.tried_strains', page=strains.next_num) if strains.has_next else None
    prev_url = url_for('main.tried_strains', page=strains.prev_num) if strains.has_prev else None
    return render_template('strains_list.html', title='Tried', strains_list=strains.items, next_url=next_url, prev_url=prev_url)


# TODO: Change to query string
@bp.route('/strains/not_tried')
@login_required
def not_tried_strains():
    page = request.args.get('page', 1, type=int)
    strains = current_user.has_not_tried(page, current_app)
    next_url = url_for('main.not_tried_strains', page=strains.next_num) if strains.has_next else None
    prev_url = url_for('main.not_tried_strains', page=strains.prev_num) if strains.has_prev else None
    return render_template('strains_list.html', title='Not Tried', strains_list=strains.items, next_url=next_url, prev_url=prev_url)


# TODO: Change to query string
@bp.route('/search/<strain>')
@login_required
def searched_strains(strain):
    page = request.args.get('page', 1, type=int)
    strains = Strain.query.filter(Strain.name.like('%' + strain + '%')).paginate(page, current_app.config['STRAINS_PER_PAGE'], False)
    next_url = url_for('main.searched_strains', strain=strain, page=strains.next_num) if strains.has_next else None
    prev_url = url_for('main.searched_strains', strain=strain,  page=strains.prev_num) if strains.has_prev else None
    return render_template('strains_list.html', title='Search:' + strain, strains_list=strains.items, next_url=next_url, prev_url=prev_url)


@bp.route('/strains/<strain_name>')
@login_required
def some_strain(strain_name):
    strain = Strain.query.filter_by(index=strain_name).first_or_404()
    return render_template('strain.html', title=strain.name, strain=strain)


# TODO: Combine try and untry via query string, maybe even combine both into a query string on some_strain
@bp.route('/try/<strain_name>')
@login_required
def try_strain(strain_name):
    strain = Strain.query.filter_by(name=strain_name).first()
    if strain is None:
        flash(f'Strain: {strain_name} not found')
        return redirect(url_for('main.home'))

    current_user.try_strain(strain)
    db.session.commit()
    flash(f'Strain: {strain_name} has been tried')
    return redirect(url_for('main.some_strain', strain_name=strain.index))


# TODO: Combine try and untry via query string
@bp.route('/untry/<strain_name>')
@login_required
def untry_strain(strain_name):
    strain = Strain.query.filter_by(name=strain_name).first()
    if strain is None:
        flash(f'Strain: {strain_name} not found')
        return redirect(url_for('main.home'))

    current_user.untry_strain(strain)
    db.session.commit()
    flash(f'Strain: {strain_name} has been tried')
    return redirect(url_for('main.some_strain', strain_name=strain.index))


# @app.route('/remote/<query>')
# def remote(query):
#     return flask.jsonify([i for i, in db.session.query(Strain.name).filter(Strain.name.like('%' + query + '%')).limit(5)])


# TODO: Change to query string
@bp.route('/remote/<query>')
def remote(query):
    print(query)
    q = db.session.query(Strain.name).filter(Strain.name.like(query + '%'))
    count = q.count()
    if count >= current_app.config['SEARCH_RESULTS']:
        return jsonify([i for i, in q.limit(current_app.config['SEARCH_RESULTS']).all()])
    else:
        first_query = [i for i, in q.all()]
        q2 = db.session.query(Strain.name).filter(Strain.name.like('%' + query + '%'))
        # results = q.all() + q2.limit(app.config['SEARCH_RESULTS'] - count).all()
        results = first_query + [i for i, in q2.limit(current_app.config['SEARCH_RESULTS'] - count).all() if i not in first_query]

        print(results)
        return jsonify(results)


@bp.route('/name_to_index')
def name_to_index():
    strain_name = request.args.get("name")
    strain_index = db.session.query(Strain.index).filter(Strain.name == strain_name).first_or_404()
    print(strain_index)
    return redirect(url_for('main.some_strain', strain_name=strain_index[0]))
