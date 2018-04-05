from flask import Flask, request, redirect, render_template, flash, session
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime


app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:beproductive@localhost:8889/blogz'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
app.secret_key = 'hffv$$1fnfkdk!kffj#44f'
db = SQLAlchemy(app)


class Blog(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120))
    b_info = db.Column(db.Text)
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    posted = db.Column(db.DateTime)
    
    def __init__(self, name, b_info, owner, posted=None):
        self.name = name
        self.b_info = b_info
        self.owner = owner
        if posted is None:
            posted = datetime.utcnow()
        self.posted = posted


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(120), unique=True)
    password = db.Column(db.String(120))
    blogs = db.relationship('Blog', backref='owner')

    def __init__(self, username, password):
        self.username = username
        self.password = password


@app.before_request
def require_login():
    allowed_routes = ['login', 'signup', 'blog', 'index']
    if request.endpoint not in allowed_routes and 'username' not in session:
        return redirect('/login')


@app.route('/')
def index():
    users = User.query.all()
    return render_template('index.html', users=users)


@app.route('/login', methods=['POST','GET'])
def login():
    username_error = ""
    password_error = ""

    if request.method == 'POST':
        password = request.form['password']
        username = request.form['username']
        user = User.query.filter_by(username=username).first()

        if user and (user.password == password):
            session['username'] = username
            return redirect('/newpost')
        if not user:
            return render_template('login.html', username_error="Username does not exist.")
        else:
            return render_template('login.html', password_error="Your username or password was incorrect.")

    return render_template('login.html')


@app.route("/signup", methods=['POST', 'GET'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        verify = request.form['verify']
        exist = User.query.filter_by(username=username).first()

        username_error = ""
        password_error = ""
        verify_error = ""

        if username == "":
            username_error = "Please enter a username."
        elif len(username) <= 3 or len(username) > 20:
            username_error = "Username must be between 3 and 20 characters long."
        elif " " in username:
            username_error = "Username cannot contain any spaces."
        if password == "":
            password_error = "Please enter a password."
        elif len(password) <= 3:
            password_error = "Password must be greater than 3 characters long."
        elif " " in password:
            password_error = "Password cannot contain any spaces."
        if password != verify or verify == "":
            verify_error = "Passwords do not match."
        if exist:
            username_error = "Username already taken."
       
        if len(username) > 3 and len(password) > 3 and password == verify and not exist:
            new_user = User(username, password)
            db.session.add(new_user)
            db.session.commit()
            session['username'] = username
            return redirect('/newpost')
        else:
            return render_template('signup.html',
            username=username,
            username_error=username_error,
            password_error=password_error,
            verify_error=verify_error
            )

    return render_template('signup.html')


@app.route('/blog', methods=['POST', 'GET'])
def blog():
    blog_id = request.args.get('id')
    user_id = request.args.get('userid')

    posts = Blog.query.order_by(Blog.posted.desc())

    if blog_id:
        post = Blog.query.filter_by(id=blog_id).first()
        return render_template("post.html", name=post.name, b_info=post.b_info, user=post.owner.username, posted=post.posted, user_id=post.owner_id)
    if user_id:
        entries = Blog.query.filter_by(owner_id=user_id).all()
        return render_template('singleUser.html', entries=entries)

    return render_template('blog.html', posts=posts)

@app.route('/newpost')
def post():
    return render_template('newpost.html', title="Add A Blog")

@app.route('/newpost', methods=['POST', 'GET'])
def newpost():
    name = request.form['name']
    b_info = request.form["b_info"]
    owner = User.query.filter_by(username=session['username']).first()

    name_error = ""
    b_info_error = ""

    if name == "":
        name_error = "Title required."
    if b_info == "":
        b_info_error = "Content required."

    if not name_error and not b_info_error:
        new_post = Blog(name, b_info, owner)
        db.session.add(new_post)
        db.session.commit()
        page_id = "/blog?id=" + str (new_post.id)
        return redirect (page_id)
    else:
        return render_template("newpost.html",
            name = name,
            b_info = b_info,
            name_error = name_error,
            b_info_error = b_info_error
        )


@app.route('/logout')
def logout():
    del session['username']
    return redirect('/')

if __name__ == '__main__':
    app.run()