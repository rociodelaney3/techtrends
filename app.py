import sqlite3

from flask import Flask, jsonify, json, render_template, request, url_for, redirect, flash
from werkzeug.exceptions import abort
from datetime import datetime
import logging

connection_counter = 0
# Function to get a database connection.
# This function connects to database with the name `database.db`
def get_db_connection():
    global connection_counter
    connection = sqlite3.connect('database.db')
    connection.row_factory = sqlite3.Row
    connection_counter += 1
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
    app.logger.info('Initial request completed')
    return render_template('index.html', posts=posts)

# Define how each individual article is rendered 
# If the post ID is not found a 404 page is shown
@app.route('/<int:post_id>')
def post(post_id):
    post = get_post(post_id)
    if post is None:
      app.logger.info(f'Article with id {post_id} does not exist')
      return render_template('404.html'), 404
    else:
      postTitle = post['title']
      app.logger.info(f'Article "{postTitle}" retrieved!')
      return render_template('post.html', post=post)

# Define the About Us page
@app.route('/about')
def about():
    app.logger.info(f'About page accessed')
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
            app.logger.info(f'Article "{title}" was created')
            return redirect(url_for('index'))

    return render_template('create.html')

@app.route('/healthz')
def status():
    response = app.response_class(
            response=json.dumps({"result":"OK - healthy"}),
            status=200,
            mimetype='application/json'
    )
    #logs
    app.logger.info(f'Status request successfull')
    return response

@app.route('/metrics')
def metrics():
    connection = get_db_connection()
    post_count = connection.execute('SELECT count(1) from posts').fetchone()[0]
    return app.response_class(
        response=json.dumps({
            'post_count': post_count,
            'db_connection_count': connection_counter
        }),
        status=200,
        mimetype='application/json'
    )


# start the application on port 3111
if __name__ == "__main__":
   logging.basicConfig(filename='app.log',level=logging.DEBUG)

   app.run(host='0.0.0.0', port='3111')
