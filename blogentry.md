---
title: "SQLAlchemy: Limiting the Many in a One-To-Many Relationship"
date: 2015/03/30
author: Jason
tags: Flask-SQLAlchemy, SQLAlchemy,
---


While working on our most recent contract the client described a relationship between two entities. In this relationship each of the first entity had "up to, but not more than, 3" of the second.

For clarity's sake let's call the first entity a **Farmer** and the second entity we'll call a **BlindMouse**. The situation that the client was describing (in terms of a relational database) is called a **one-to-many** relationship. However, in most cases there is not a limit to the number of the **many** (the number of **BlindMouses**) that the **one** (a **Farmer**) can have. The solution we came up to throw a custom exception if an attempt is made to add more than the allowed number of records (**BlindMouses**) that can be associated with the foreign key of the **one** (**BlindMouse.farmer_id**)

Here I am using Flask-SQLAlchemy, but this can just as easily be implemented in plain old SQLAlchemy.

We are given the following tables:

```python

class Farmer(db.Model):
    __tablename__ = "farmer"
    id = db.Column(db.Integer, primary_key=True)

```

and

```python

class BlindMouse(db.Model):
    __tablename__ = "blindmouse"
    id = db.Column(db.Integer, primary_key=True)
    farmer = db.relationship('Farmer', backref='blind_mice')
    farmer_id = db.Column(db.Integer, db.ForeignKey('farmer.id'))

```

Then we create a custom error.

```python
from sqlalchemy.exc import IntegrityError

    class RelationLimitReachedError(IntegrityError):
        pass
```

Using SQLAlchemy's ```@event``` decorator and our new ```RelationLimitReachedError``` exception we set up a limit checker.

```python

from sqlalchemy import event


@event.listens_for(BlindMouse.farmer_id, 'set', retval=True)
def blindmouse_per_farmer_limit_check(target, value, oldvalue, initiator):
    if value is not None:
        mouse_count = BlindMouse.query.filter_by(farmer_id=value).count()
        if mouse_count >= 3:
            err = 'Max number of BlindMouses (3) reached for Farmer {}'
            orig = Exception(err.format(value))
            msg = "Record Not Committed"
            last_part = 'Session Rolled Back and Cursor Flushed'
            raise RelationLimitReachedError(msg, last_part, orig)
    return value

```

If the addition of a new **BlindMouse** to the **one-to-many** of the **Farmer** exceeds our limit (3) an ```IntegrityError``` is raised and the new **BlindMouse** is not added.

For a simple working example, follow the instructions in [this repo of mine](https://github.com/elbow-jason/three-blind-mice) and if your like the example give it a star.
