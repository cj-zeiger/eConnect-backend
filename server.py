#all of our imports
import sqlite3
from flask import Flask, g, request
import os
from contextlib import closing
#app setup
app = Flask(__name__)
app.config.from_object(__name__)


#configuration
app.config.update(dict(
    DATABASE = os.path.join(app.root_path, 'database.db'),
    DEBUG = True
))

#database methods
def connect_db():
    return sqlite3.connect(app.config['DATABASE'])
def init_db():
    with closing(connect_db()) as db:
        with app.open_resource('schema.sql', mode='r') as f:
            db.cursor().executescript(f.read())
    db.commit()
#always use this method when you need a refrence to the db connectoin
#If you need to use this outside of a request, use 'with app.app_context()'
def get_db():
    db = getattr(g, 'db', None)
    if db is None:
        db = g._database = connect_db()
    return db

#creates a db connection at the start of each request, this might not be needed
@app.before_request
def before_request():
    #get a database connection
    g.db = connect_db()

@app.teardown_request
def teardown_request(exception):
    db = getattr(g,'db',None)
    if db is not None:
        db.close()

def query_db(query, args=(), one=False):
    cur = get_db().execute(query, args)
    rv = cur.fetchall()
    cur.close()
    return (rv[0] if rv else None) if one else rv

@app.route('/')
def home_page():
    return 'Home Page' 
@app.route('/users/',methods=['GET','POST'])
def user_collection():
    if request.method == 'GET':
        return 'All Users'
    elif request.method == 'POST':
        if query_db('select ? from interactions')
        return 'User Added to Database'

@app.route('/users/<username>',methods=['GET','PUT'])
def single_user_endpoint(username):
    if request.method == 'GET':
        return '%s has a specific count' % username
    elif request.method == 'PUT':
        return '%s Updated' % username


if not os.path.exists('./database.db'):
    init_db()

if __name__ == '__main__':
    app.debug = True
    app.run()


