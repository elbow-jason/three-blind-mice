three-blind-mice
================
An example of limiting the number of the many in a one-to-many relationship using SQLAlchemy events.


Setup
-----

In a virtual env (or not if you are feeling a bit crazy) run:

```$ pip install -r requirements.txt```


Run the Server
--------------

Go to [http://localhost:5000](http://localhost:5000) in your browser


Do it!
------

Add a mouse 3 times and it works fine. Attempt to add a fourth and an custom exception is raised.
