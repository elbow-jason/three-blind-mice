from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy

from sqlalchemy import event
from sqlalchemy.exc import IntegrityError


app = Flask('three_blind_mice')

db = SQLAlchemy(app)

app.config.update(
    SQLALCHEMY_DATABASE_URI='sqlite:///test.db',
    HOST='localhost',
    PORT='5000',
    DEBUG=True
)


class Farmer(db.Model):
    __tablename__ = 'farmer'
    id = db.Column(db.Integer, primary_key=True)


class BlindMouse(db.Model):
    __tablename__ = 'blindmouse'
    id = db.Column(db.Integer, primary_key=True)
    farmer = db.relationship('Farmer', backref='blind_mice')
    farmer_id = db.Column(db.Integer, db.ForeignKey('farmer.id'))


class RelationLimitReachedError(IntegrityError):
    pass


@event.listens_for(BlindMouse.farmer_id, "set", retval=True)
def blindmouse_per_farmer_limit_check(target, value, oldvalue, initiator):
    if value is not None:
        mouse_count = BlindMouse.query.filter_by(farmer_id=value).count()
        if mouse_count >= 3:
            err = "Max number of BlindMouses (3) reached for Farmer {}..."
            orig = Exception(err.format(value))
            msg = 'Record Not Committed.'
            last_part = 'Session Rolled Back and Cursor Flushed.'
            raise RelationLimitReachedError(msg, last_part, orig)
    return value



@app.route('/')
def index():
    return '<a href="/add_mouse">Add a blind mouse to the farmer</a>'


@app.route('/add_mouse')
def add_mouse():
    new_mouse = BlindMouse()
    new_mouse.farmer_id = 1

    try:
        db.session.add(new_mouse)
        db.session.commit()
        return '<p>added mouse</p><p><a href="/"> Go back </a> </p>'
    except RelationLimitReachedError as e:
        db.session.rollback()
        raise e

if __name__ == '__main__':

    db.create_all()

    farmer = Farmer()
    db.session.add(farmer)
    db.session.commit()

    app.run()
