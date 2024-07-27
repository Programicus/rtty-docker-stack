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

@app.route('/', methods=['GET', 'POST'])
def index():
    show_finished = 'show_finished' in request.form
    show_printing = 'show_printing' in request.form
    show_queued = 'show_queued' in request.form if request.method == 'POST' else True  # Default to checked
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    query = "SELECT * FROM Queue WHERE 1=0"
    if show_finished:
        query += " OR status = 'FINISHED'"
    if show_printing:
        query += " OR status = 'PRINTING'"
    if show_queued:
        query += " OR status = 'QUEUED'"
    
    query += " ORDER BY status, timestamp"

    cursor.execute(query)
    entries = cursor.fetchall()
    cursor.close()
    conn.close()
    
    return render_template('index.html', entries=entries, show_finished=show_finished, show_printing=show_printing, show_queued=show_queued)

@app.route('/debug', methods=['GET', 'POST'])
def debug():
    if request.method == 'POST':
        source = request.form['source']
        message = request.form['message']
        
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO Queue (source, message, status) VALUES (%s, %s, %s)", (source, message, 'QUEUED'))
        conn.commit()
        cursor.close()
        conn.close()
        
        return redirect(url_for('index'))
    return render_template('debug.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
