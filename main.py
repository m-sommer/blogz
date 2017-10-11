from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://build-a-blog:buildablog@localhost:8889/build-a-blog'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key = 'y337kGcys&zP3B'

class Post(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    content = db.Column(db.String(120))

    def __init__(self, title, content):
        self.title = title
        self.content = content

@app.route('/blog', methods=['POST', 'GET'])
def index():

    if request.args:
            blog_id = request.args.get('id')
            post = Post.query.get(blog_id)
            return render_template('post.html', post=post)
    
    if request.method == 'POST':
        entry_title = request.form['entry_title']
        entry_content = request.form['entry_content']

        if not entry_title or not entry_content:
            flash('Please fill in both fields', 'error')
            return render_template('newpost.html')
        else:
            new_post = Post(entry_title, entry_content)
        
            db.session.add(new_post)
            db.session.commit()
            
            return redirect('/blog?id={0}'.format(new_post.id))

    posts = Post.query.all()
    return render_template('blog.html', posts=posts)

@app.route('/newpost', methods=['POST', 'GET'])
def newpost():

    return render_template('newpost.html')

if __name__ == '__main__':
    app.run()