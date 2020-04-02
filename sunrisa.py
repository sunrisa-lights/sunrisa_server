from flask import Flask, render_template
import pymysql.cursors
import logging

app = Flask(__name__)
logging.basicConfig(filename='error.log',level=logging.DEBUG)
conn = pymysql.connect(host='localhost',
                       user='root',
                       password='root')


@app.route("/", methods=['GET', 'POST'])
def hello():
    logging.debug("Hello was called")
    return render_template('index.html')

@app.route("/pp", methods=['GET'])
def test_write():
    logging.debug("test_write was called")
    logging.debug("connect was called")
    create_and_use_db("test1")
    create_table()
    return 'hello world'

def create_and_use_db(db_name):
    create_sql = 'create database {}'.format(db_name)
    try:
        conn.cursor().execute(create_sql)
    except pymysql.err.ProgrammingError:
        logging.debug("db already exists")

    use_sql = 'use {}'.format(db_name)
    conn.cursor().execute(use_sql)

def create_table():
    create_table_sql = 'CREATE TABLE example ( id smallint unsigned not null auto_increment, name varchar(20) not null, constraint pk_example primary key (id) );'
    try:
        conn.cursor().execute(create_table_sql)
    except pymysql.err.InternalError:
        logging.debug("table already exists")

    logging.debug("table created")


if __name__ == "__main__":
    app.run()
