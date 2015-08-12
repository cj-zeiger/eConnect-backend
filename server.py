#all of our imports
import sqlite3
from flask import (Flask, g, request, abort, json, render_template, redirect,
    url_for, make_response)
import os
from contextlib import closing
from datetime import datetime, date
#app setup
app = Flask(__name__)
#configuration
app.config.update(dict(
    DATABASE = os.path.join(app.root_path, 'database.db'),
    DEBUG = True
))
app.config.from_object(__name__)
app.secret_key = '\x97u\x88\x18\xb6s\x85\x1c|\x067\xfd\x97_d\xb7ub`{\xc9\xb1z\x14'


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

def get_user_name(user_id):
    query = query_db('select name from users where id=?',[str(user_id)],True)
    return query[0]

#webpages
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        response = make_response(url_for('index'))
        #session['username'] = request.form['username']
        return redirect(url_for('index'))
    else:
        return render_template('login.html')

#API endpoints
@app.route('/users/',methods=['GET','POST'])
def user_collection():
    if request.method == 'GET':
        return json.dumps(query_db('select * from users order by count desc'))
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

@app.route('/transaction/<int:user_id>')
def get_transaction_list(user_id):
    if not user_exists_id(user_id):
        print 'get_transaction_list() called with invalid user ID'
        abort(500)
    print [str(user_id)]
    query1 = query_db('select * from interactions where user_id_1 = ? order by transaction_time desc', [str(user_id)])
    query2 = query_db('select * from interactions where user_id_2 = ? order by transaction_time desc', [str(user_id)])
    merged_list = []

    while query1 and query2:
        if query1[0][3] == query2[0][3]:
            merged_list.append(get_user_name(query1[0][2]))
            query1.pop(0)
        elif query1[0][3] > query2[0][3]:
            merged_list.append(get_user_name(query1[0][2]))
            query1.pop(0)
        else:
            merged_list.append(get_user_name(query2[0][1]))
            query2.pop(0)
    if query1:
        while query1:
            merged_list.append(get_user_name(query1[0][2]))
            query1.pop(0)
    else:
        while query2:
            merged_list.append(get_user_name(query2[0][1]))
            query2.pop(0)
    return json.dumps(merged_list)


if not os.path.exists('./database.db'):
    print 'initdb()'
    init_db()

if __name__ == '__main__':
    app.run()
