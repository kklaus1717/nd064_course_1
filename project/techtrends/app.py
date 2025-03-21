import sqlite3
import logging
import sys

from flask import Flask, jsonify, json, render_template, request, url_for, redirect, flash
from werkzeug.exceptions import abort

db_connection_count = 0
post_count = 0

# Function to get a database connection.
# This function connects to database with the name `database.db`
def get_db_connection():
    connection = sqlite3.connect('database.db')
    connection.row_factory = sqlite3.Row
    #increase the connection ammount
    global db_connection_count
    db_connection_count += 1
    return connection

# Function to get a post using its ID
def get_post(post_id):
    connection = get_db_connection()
    post = connection.execute('SELECT * FROM posts WHERE id = ?',
                        (post_id,)).fetchone()
    connection.close()
    return post

# Define the Flask application
app = Flask(__name__)
app.config['SECRET_KEY'] = 'your secret key'

# Define the main route of the web application 
@app.route('/')
def index():
    connection = get_db_connection()
    posts = connection.execute('SELECT * FROM posts').fetchall()
    connection.close()
    return render_template('index.html', posts=posts)

# Define how each individual article is rendered 
# If the post ID is not found a 404 page is shown
@app.route('/<int:post_id>')
def post(post_id):
    post = get_post(post_id)
    if post is None:
      #A non-existing article is accessed
      app.logger.info(f"A non-existing article with ID {post_id} is accessed and a 404 page is returned")
      return render_template('404.html'), 404
    else:
      #An existing article is retrieved
      app.logger.info(f"An existing article with ID {post_id}is retrieved. Articel title is: {post['title']}")
      return render_template('post.html', post=post)

# Define the About Us page
@app.route('/about')
def about():
    #The "About Us" page is retrieved
    app.logger.info(f"The \"About Us\" page is retrieved")
    return render_template('about.html')

# Define the post creation functionality 
@app.route('/create', methods=('GET', 'POST'))
def create():
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']

        if not title:
            flash('Title is required!')
        else:
            connection = get_db_connection()
            connection.execute('INSERT INTO posts (title, content) VALUES (?, ?)',
                         (title, content))
            connection.commit()
            connection.close()
            #A new article is created
            app.logger.info(f"A new article is created. Articel title is: {title}")

            return redirect(url_for('index'))

    return render_template('create.html')

#Healthcheck 
@app.route('/healthz')
def healthz():
    response = app.response_class(
            response=json.dumps({"result":"OK - healthy"}),
            status=200,
            mimetype='application/json'
    )
    return response

#Metrics 
@app.route('/metrics')
def metrics():
    connection = get_db_connection()
    #Total amount of posts in the database
    post_count = connection.execute('SELECT count(*) FROM posts').fetchone()[0]
    connection.close()
    response = app.response_class(
            response=json.dumps({"status":"success","code":0,"data":{"db_connection_count":db_connection_count,"post_count":post_count}}),
            status=200,
            mimetype='application/json'
    )
    return response

# start the application on port 3111
if __name__ == "__main__":
    format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    logging.basicConfig(level=logging.DEBUG, format=format)
    formatter = logging.Formatter(format)
    # Handler for stdout
    stdout_handler = logging.StreamHandler(sys.stdout)
    stdout_handler.setLevel(logging.DEBUG)  # DEBUG and higher
    stdout_handler.setFormatter(formatter)
    # Handler for stderr
    stderr_handler = logging.StreamHandler(sys.stderr)
    stderr_handler.setLevel(logging.DEBUG)  # DEBUG and higher
    stderr_handler.setFormatter(formatter)
    
    app.logger.addHandler(stdout_handler)
    app.logger.addHandler(stderr_handler)
    
    app.run(host='0.0.0.0', port='3111')
