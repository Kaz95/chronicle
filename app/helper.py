from flask import url_for


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
        print('-------STRAINS------')
        print(strains)
        next_url = url_for('main.strains_list', filter=filt, page=strains.next_num) if strains.has_next else None
        prev_url = url_for('main.strains_list', filter=filt, page=strains.prev_num) if strains.has_prev else None

    return prev_url, next_url
