from server import *
with app.test_request_context():
    print query_db_json('select * from users order by count desc')
