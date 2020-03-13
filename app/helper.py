from flask import url_for
from app.models import User
from werkzeug.urls import url_parse


# TODO: Test
def create_prev_next_urls(strains, filt=None, q=None):
    if q:
        next_url = url_for('main.strains_list', filter=filt, q=q,
                           page=strains.next_num) if strains.has_next else None
        prev_url = url_for('main.strains_list', filter=filt, q=q,
                           page=strains.prev_num) if strains.has_prev else None

    elif not filt:
        next_url = url_for('main.strains_list', page=strains.next_num) if strains.has_next else None
        prev_url = url_for('main.strains_list', page=strains.prev_num) if strains.has_prev else None

    else:
        next_url = url_for('main.strains_list', filter=filt, page=strains.next_num) if strains.has_next else None
        prev_url = url_for('main.strains_list', filter=filt, page=strains.prev_num) if strains.has_prev else None

    return prev_url, next_url


def auth_creds(username, password):
    user = User.query.filter_by(username=username).first()

    if user is None or not user.verify_password(password):
        return False
    return user


def validate_next_page(next_page):
    if not next_page or url_parse(next_page).netloc != '':
        return False
    return True


def create_user(username, password):
    user = User()
    user.username = username
    user.hash_password(password)
    return user
