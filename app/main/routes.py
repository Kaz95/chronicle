from app import db
from app.main import bp
from app.models import Strain
from flask import render_template, redirect, url_for, flash, request, jsonify, current_app
from flask_login import current_user, login_required


@bp.route('/')
@bp.route('/home')
@login_required
def home():
    return render_template('home.html', title='Home')


# TODO: DRY
# TODO: This and the relevant templates assume the only time there wont be strains in strain_list is when no strains
# TODO: have been tried. It can also occur when user navigates directly to an empty search.
# TODO: Also consider adding an actual search button.
@bp.route('/strains')
@login_required
def strains_list():
    page = request.args.get('page', 1, type=int)
    filter_ = request.args.get('filter')
    q = request.args.get('q')

    if filter_ == 'tried':
        title = 'Tried Strains'
        strains = current_user.tried.paginate(page, current_app.config['STRAINS_PER_PAGE'], False)
        next_url = url_for('main.strains_list', filter='tried', page=strains.next_num) if strains.has_next else None
        prev_url = url_for('main.strains_list', filter='tried',  page=strains.prev_num) if strains.has_prev else None

    # TODO: Change has_not_tried to not include the paginate call, then call it here. In line with tried.paginate
    elif filter_ == 'not_tried':
        title = 'Not Tried Strains'
        strains = current_user.has_not_tried(page, current_app)
        next_url = url_for('main.strains_list', filter='not_tried',  page=strains.next_num) if strains.has_next else None
        prev_url = url_for('main.strains_list', filter='not_tried',  page=strains.prev_num) if strains.has_prev else None

    # TODO: Circumvent 500 error if user navigates directly to search filter with no query.
    elif filter_ == 'search':
        title = 'Search: ' + q
        strains = Strain.query.filter(Strain.name.like('%' + q + '%')).paginate(page, current_app.config['STRAINS_PER_PAGE'], False)
        next_url = url_for('main.strains_list', filter=filter_, q=q, page=strains.next_num) if strains.has_next else None
        prev_url = url_for('main.strains_list', filter=filter_, q=q, page=strains.prev_num) if strains.has_prev else None

    # TODO: Consider adding paginate all as a shared class method, or refactoring to be more inline with tried.paginate
    else:
        title = 'Strains'
        strains = Strain.paginate_all(page, current_app)
        next_url = url_for('main.strains_list', page=strains.next_num) if strains.has_next else None
        prev_url = url_for('main.strains_list', page=strains.prev_num) if strains.has_prev else None

    return render_template('strains_list.html', title=title, strains_list=strains.items, next_url=next_url,
                           prev_url=prev_url)


@bp.route('/strains/<strain_index>')
@login_required
def some_strain(strain_index):
    strain = Strain.query.filter_by(index=strain_index).first_or_404()
    action = request.args.get('action')

    if action:
        if action == 'try':
            current_user.try_strain(strain)
            flash(f'Strain: {strain.name} has been tried')

        if action == 'untry':
            current_user.untry_strain(strain)
            flash(f'Strain: {strain.name} has been un...tried')

        db.session.commit()
        return redirect(url_for('main.some_strain', strain_index=strain_index))

    else:
        return render_template('strain.html', title=strain.name, strain=strain)


@bp.route('/typeahead')
def typeahead():
    search_string = request.args.get('q')
    initial_query = db.session.query(Strain.name).filter(Strain.name.like(search_string + '%'))
    results_count = initial_query.count()

    if results_count >= current_app.config['SEARCH_RESULTS']:
        return jsonify([i for i, in initial_query.limit(current_app.config['SEARCH_RESULTS']).all()])

    else:
        first_query = [i for i, in initial_query.all()]
        follow_up_query = db.session.query(Strain.name).filter(Strain.name.like('%' + search_string + '%'))
        agg_results = first_query + [i for i, in follow_up_query.limit(current_app.config['SEARCH_RESULTS'] - results_count).all() if i not in first_query]
        return jsonify(agg_results)


@bp.route('/name_to_index')
def name_to_index():
    strain_name = request.args.get("name")
    strain_index = db.session.query(Strain.index).filter(Strain.name == strain_name).first_or_404()
    return redirect(url_for('main.some_strain', strain_index=strain_index[0]))
