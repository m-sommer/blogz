from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:blogz@localhost:8889/blogz'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key = 'y337kGcys&zP3B'

class Post(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    content = db.Column(db.String(120))
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self, title, content, owner):
        self.title = title
        self.content = content
        self.owner = owner

class User(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(60))
    password = db.Column(db.String(60))
    blogs = db.relationship('Post', backref='owner')

    def __init__(self, username, password):
        self.username = username
        self.password = password

@app.before_request
def require_login():
    allowed_routes = ['index', 'blog', 'login', 'signup']
    if request.endpoint not in allowed_routes and 'username' not in session:
        return redirect('/login')

@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and user.password == password:
            session['username'] = username
            flash("Logged In")
            return redirect('/newpost')
        else: 
            if not user:
                flash('Invalid Username', 'error')
                return render_template('/login.html', username=username)
            else:
                flash('Invalid Password', 'error')
                return render_template('/login.html', username=username)

    return render_template('login.html')

@app.route('/signup', methods=['POST', 'GET'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        verify = request.form['verify']

        if username == '' or password == '' or verify == '': 
            flash('One or more fields are invalid', 'error')
            return render_template('/signup.html', username=username)

        if len(username) < 3:
            flash('Username must be at least 3 characters', 'error')
            return render_template('/signup.html', username=username)

        if len(password) < 3:
            flash('Password must be at least 3 characters', 'error')
            return render_template('/signup.html', username=username)

        if password != verify:
            flash('Passwords do not match', 'error')
            return render_template('/signup.html', username=username)
        else:
            existing_user = User.query.filter_by(username=username).first()
            if not existing_user:
                new_user = User(username, password)
                db.session.add(new_user)
                db.session.commit()
                session['username'] = username
                flash("Logged In")
                return redirect('/newpost')
            else:
                flash('Duplicate User', 'error')
                return render_template('/signup.html', username=username)

    return render_template('signup.html')

@app.route('/logout')
def logout():
    del session['username']
    flash("Logged Out")
    return redirect('/blog')

@app.route('/', methods=['POST', 'GET'])
def index():

    users = User.query.all()
    return render_template('index.html', users=users)

@app.route('/blog', methods=['POST', 'GET'])
def blog():

    if request.args.get('id'):
        blog_id = request.args.get('id')
        post = Post.query.get(blog_id)
        owner_id = request.args.get('id')
        owner = Post.query.get(owner_id)
        return render_template('post.html', post=post, owner=owner)

    if request.args.get('user'):
        username = request.args.get('user')
        user = User.query.filter_by(username=username).first()
        posts = user.blogs
        return render_template('user.html', posts=posts, user=user)

    if request.method == 'POST':
        entry_title = request.form['entry_title']
        entry_content = request.form['entry_content']

        if not entry_title or not entry_content:
            flash('Please fill in both fields', 'error')
            return render_template('newpost.html')
        else:
            owner = User.query.filter_by(username=session['username']).first()
            new_post = Post(entry_title, entry_content, owner)
            db.session.add(new_post)
            db.session.commit()
            return redirect('/blog?id={0}'.format(new_post.id))

    posts = Post.query.all()
    users = User.query.all()
    return render_template('blog.html', posts=posts, users=users)

@app.route('/newpost', methods=['POST', 'GET'])
def newpost():

    return render_template('newpost.html')

if __name__ == '__main__':
    app.run()