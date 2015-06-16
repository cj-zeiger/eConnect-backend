#all of our imports
import sqlite3
from flask import Flask, g, request, abort, json
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
    print 'Databse url is %s' % app.config['DATABASE']
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
    get_db().commit()
    return (rv[0] if rv else None) if one else rv


@app.route('/users/',methods=['GET','POST'])
def user_collection():
    if request.method == 'GET':
        return json.dumps(query_db('select * from interactions'))
    elif request.method == 'POST':
        form_data = request.form
        username = form_data['username']
        select_result = query_db('select * from interactions where name = ?',[username])
        if select_result and select_result[0][1] == username:
            #user already exists in the database
            abort(500)
        else:
            data_base_response = query_db('insert into interactions (name) values (?)', [username])
            return str(query_db('select id from interactions where name=?',[username],one=True)[0])


@app.route('/users/<username>',methods=['GET','PUT'])
def single_user_endpoint(username):
    print'/users/<username> reached where username = %s' % username
    result = query_db('select * from interactions where name = ?',[username], one=True)
    if not result:
            abort(500)
    if request.method == 'GET':
        if result[1] == username:
            return str(result[2])
        else:
            print 'somehow the https username variable and the result from the database query don\'t match'
            abort(500)
    elif request.method == 'PUT':
        query_db('update interactions set count=count+1 where name = ?',[username])
        return '%s\'s count has been incremented' % username


if not os.path.exists('./database.db'):
    init_db()

if __name__ == '__main__':
    app.debug = True
    app.run()


