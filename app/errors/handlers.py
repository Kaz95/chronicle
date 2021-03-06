from app import db
from app.errors import bp
from flask import render_template


# TODO: Test....?
# 'error' or literally any param is needed for error handlers to work correctly.
@bp.app_errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404


# TODO: Test....?
@bp.app_errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('errors/500.html'), 500
