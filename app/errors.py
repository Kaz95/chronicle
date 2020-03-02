from flask import render_template
from app import app
# 'error' or literally any param is needed for error handlers to work correctly.


@app.errorhandler(404)
def not_found_error(error):
    return render_template('404.html'), 404


@app.errorhandler(500)
def internal_error(error):
    return render_template('500.html'), 500
