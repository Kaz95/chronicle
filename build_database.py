from app import donezo
from app import db
from app.models import Strain


def build_db():
    info = donezo.done

    for tup in info.items():
        index = tup[0]
        name = tup[1]['name']
        leafly = 'https://www.leafly.com' + tup[1]['link']
        species = tup[1]['species']
        description = tup[1]['description']
        temp = Strain(index=index, name=name, leafly=leafly, species=species, description=description)
        db.session.add(temp)
    db.session.commit()


if __name__ == '__main__':
    build_db()