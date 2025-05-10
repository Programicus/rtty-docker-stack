from flask import Flask, request, render_template, redirect, url_for
import psycopg2
import os

app = Flask(__name__)

def get_db_connection():
    conn = psycopg2.connect(
        dbname=os.environ.get('POSTGRES_DB', 'defaultdatabase'),
        user=os.environ.get('POSTGRES_USER', 'defaultuser'),
        password=os.environ.get('POSTGRES_PASSWORD', 'defaultpassword'),
        host='db'
    )
    return conn

def insert_msg_into_db(source, msg):
    with get_db_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute("INSERT INTO Queue (from_addr, source, message, status) VALUES (%s, %s, %s, %s)", (source, 'web_debug', msg, 'QUEUED'))
        conn.commit()

def set_foxtest(msg):
    with get_db_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute("INSERT INTO FOXTEST (foxtest_message) VALUES (%s)", (msg,))
        conn.commit()
def clear_foxtest():
    with get_db_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute("DELETE FROM FOXTEST")
        conn.commit()

def query_foxtest(conn):
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT foxtest_message FROM FOXTEST")

            result = cursor.fetchone()

            if result and result[0]:
                return True, result[0]
            else:
                return False, ''

    except Exception as e:
        app.logger.error(f"Error checking FOXTEST message: {e}")
        return False, ''


@app.route('/foxtest', methods=['POST'])
def foxtest():
    app.logger.error(f'foxtest: {request.form}')
    action = request.form.get('action')
    message = request.form.get('foxtest', '')

    if action == 'enable':
        set_foxtest(message)
    else:
        clear_foxtest()


    return redirect(url_for('index'))


@app.route('/debug', methods=['POST'])
def debug():
    source = request.form['source']
    message = request.form['message']
    
    insert_msg_into_db(message, source)
    
    return redirect(url_for('index'))

@app.route('/', methods=['GET', 'POST'])
def index():
    show_finished = 'show_finished' in request.form
    show_printing = 'show_printing' in request.form
    show_queued = 'show_queued' in request.form if request.method == 'POST' else True  # Default to checked
    
    
    query = "SELECT * FROM Queue WHERE 1=0"
    if show_finished:
        query += " OR status = 'FINISHED'"
    if show_printing:
        query += " OR status = 'PRINTING'"
    if show_queued:
        query += " OR status = 'QUEUED'"
    
    query += " ORDER BY status, timestamp"

    with get_db_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(query)
            entries = cursor.fetchall()

        foxtest_running, foxtest_msg = query_foxtest(conn)
    
    return render_template('index.html', 
        entries=entries, 
        show_finished=show_finished, 
        show_printing=show_printing, 
        show_queued=show_queued, 

        foxtest_running=foxtest_running,
        foxtest_msg=foxtest_msg
    )

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
