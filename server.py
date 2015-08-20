#all of our imports
import sqlite3
from flask import (Flask, g, request, abort, json, render_template, redirect,
    url_for, make_response, flash)
import os
from contextlib import closing
from datetime import datetime, date
from flask.ext.login import LoginManager, login_user, login_required
from flask.ext.bcrypt import check_password_hash
from user import User
import forms
#app setup
app = Flask(__name__)
#configuration
app.config.update(dict(
    DATABASE = os.path.join(app.root_path, 'database.db'),
    DEBUG = True
))
app.config.from_object(__name__)
app.secret_key = 'auoesh.bouoastuh.43,uoausoehuosth3ououea.auoub!'

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

running = True

@login_manager.user_loader
def load_user(userid):
    if userid == '1'.encode('UTF-8'):
        return User()
    else:
        return None

#database methods
def connect_db():
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

def query_db_json(query, args=()):
    cur = get_db().execute(query, args)
    li = cur.fetchall()
    json_list = []
    for row in li:
        d = {}
        for index,name in enumerate(cur.description):
            d[name[0]] = row[index]
        json_list.append(d)
    cur.close()
    get_db().commit()
    return json_list


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
@login_required
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET','POST'])
def login():
    form = forms.LoginForm()
    if form.validate_on_submit():
        if form.username.data == 'admin' and check_password_hash('$2a$12$jQtHgZe4.W2o4WTiHvcYxewEFCaoesUgKKuzSBAsU1xV1y9adCBMK', form.password.data):
            user = User()
            login_user(user)
            return redirect(url_for('index'))
        else:
            flash('Invalid Login')
    return render_template('login.html',form=form)

#API endpoints
@app.route('/running/')
def running():
    if running is True:
        return 'Running'
    else:
        return 'Not Running'
@app.route('/running/<toggle>')
def running_toggle(onff):
    if toggle:
        running = True
    else:
        running = False
@app.route('/users/',methods=['GET','POST'])
def users():
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

@app.route('/users/json')
def users_json():
    return json.dumps(query_db_json('select * from users order by count desc'))

@app.route('/users/<id>',methods=['GET'])
def users_id(id):
    result = query_db('select * from users where id = ?',[id], one=True)
    if not result:
            abort(500)
    if request.method == 'GET':
        return str(result[2])

@app.route('/transaction/',methods=['POST'])
def transaction():
    user_id_1 = request.form['user_id_1']
    user_id_2 = request.form['user_id_2']
    if not user_exists_id(user_id_1) or not user_exists_id(user_id_2):
        #either one or both of the users has not been registered
        abort(500)
    #check to see if these users have already met
    query1 = query_db('select * from interactions where user_id_1 = ? and user_id_2 = ?',[user_id_1,user_id_2],one=True)
    query2 = query_db('select * from interactions where user_id_1 = ? and user_id_2 = ?',[user_id_2,user_id_1],one=True)
    if query1 or query2:
        #this transaction already exists
        abort(406)
    #we are now free to add this new transaction
    n_transaction = query_db('insert into interactions (user_id_1,user_id_2,transaction_time) values (?,?,?)',[user_id_1,user_id_2,datetime.now()])
    #updating respective counts
    query_db('update users set count=count+1 where id = ?',[user_id_1])
    query_db('update users set count=count+1 where id = ?',[user_id_2])
    return 'Transaction Successful'

@app.route('/transaction/<int:user_id>')
def transaction_user_id(user_id):
    if not user_exists_id(user_id):
        abort(500)
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
