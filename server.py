#all of our imports
import sqlite3
from flask import Flask, g, request, abort, json
import os
from contextlib import closing
from datetime import datetime, date
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
    return sqlite3.connect(app.config['DATABASE'],detect_types=sqlite3.PARSE_DECLTYPES)
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

#helper methods
def user_exists(username):
    query = query_db('select * from users where name = ?',[username],one=True)
    if query and query[1] == username:
        return True
    else:
        return False
def user_exists_id(id):
    query = query_db('select * from users where id = ?', [int(id)])
    if query and query[0][0] == int(id):
        return True
    else:
        return False

@app.route('/users/',methods=['GET','POST'])
def user_collection():
    if request.method == 'GET':
        return jsonify(query_db('select * from users order by count desc'))
    elif request.method == 'POST':
        form_data = request.form
        username = form_data['username']
        if user_exists(username):
            #user already exists in the database
            abort(500)
        else:
            data_base_response = query_db('insert into users (name) values (?)', [username])
            return str(query_db('select id from users where name=?',[username],one=True)[0])


@app.route('/users/<id>',methods=['GET'])
def single_user_endpoint(id):
    print'/users/<id> reached where user id is = %s' % id
    result = query_db('select * from users where id = ?',[id], one=True)
    if not result:
            abort(500)
    if request.method == 'GET':
        return str(result[2])
@app.route('/transaction/',methods=['POST'])
def new_transaction():
    user_id_1 = request.form['user_id_1']
    user_id_2 = request.form['user_id_2']
    print "Entered /transaction/ withe user_id_1=%s and user_id_2=%s" % (str(user_id_1),str(user_id_2))
    if not user_exists_id(user_id_1) or not user_exists_id(user_id_2):
        #either one or both of the users has not been registered
        print 'one or more users does not exist'
        abort(500)
    #check to see if these users have already met
    query1 = query_db('select * from interactions where user_id_1 = ? and user_id_2 = ?',[user_id_1,user_id_2],one=True)
    query2 = query_db('select * from interactions where user_id_1 = ? and user_id_2 = ?',[user_id_2,user_id_1],one=True)
    if query1 or query2:
        #this transaction already exists
        print 'transaction already exists'
        abort(406)
    #we are now free to add this new transaction
    n_transaction = query_db('insert into interactions (user_id_1,user_id_2,transaction_time) values (?,?,?)',[user_id_1,user_id_2,datetime.now()])
    #updating respective counts
    query_db('update users set count=count+1 where id = ?',[user_id_1])
    query_db('update users set count=count+1 where id = ?',[user_id_2])
    return 'Transaction Successful'
if not os.path.exists('./database.db'):
    print 'initdb()'
    init_db()

if __name__ == '__main__':
    app.debug = True
    app.run()


