from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://Blogz:scoobydoo3@localhost:8889/Blogz'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key = 'y337kGcys&zP3B'


class Blog(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    body = db.Column(db.String(120))
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))


    def __init__(self, title, body, owner):
        self.title = title
        self.body = body
        self.owner = owner
        

class User(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    password = db.Column(db.String(10))
    username = db.Column(db.String(10), unique=True)
    blogz = db.relationship('Blog', backref='owner')

    def __init__(self, username, password):
        self.username = username
        self.password = password
      

@app.before_request
def require_login():
    allowed_routes = ['login', 'register', 'blog', 'index', 'static']
    if request.endpoint not in allowed_routes and 'username' not in session:
        return redirect('/login')

@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        if username == "":
            flash('Enter Username', 'warning')
            return render_template('login.html', title="Blogz")

        if password == "":
            flash('Enter Password', 'warning')
            return render_template('login.html', title="Blogz")

        user = User.query.filter_by(username=username).first()
        if not user:
            flash('Does not exist!', 'warning')
            return render_template('login.html', title="Blogz")

        user = User.query.filter_by(username=username, password=password).first()

        if user:  # and check_pw_hash(password, user.pw_hash):
            session['username'] = username
            flash("Logged in", 'info')
            return redirect('/newpost')
        else:
            flash('Wrong!', 'warning')
            return render_template('login.html', title="Blogz", username=username)
    return render_template('login.html', title="Blogz")

@app.route('/logout', methods=['POST'])
def logout():
    del session['username']
    return redirect('/blog')

@app.route('/register', methods=['POST', 'GET'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        if username == None:
            username = ''

        # check username
        if username == '':
            flash("Nope!Enter Username!", 'warning')
            return render_template('register.html')

        if len(username) < 3:
            flash("Username needs to be a minimum of 3 charecters!", 'warning')
            return render_template('register.html', title="Blogz", username=username)

        # check password
        password = request.form['password']
        if password == None:
            password = ''

        if password == '':
            flash("Nope! Enter a Password!", 'warning')
            return render_template('register.html', title="Blogz", username=username)
        
        if len(password) > 10 or len(password) < 3:
            flash("Password must be 3 to 10 charecters in length!", 'warning')
            return render_template('register.html', title="Blogz", username=username)

        verify = request.form['verify']
        if verify == None:
            verify = ''

        if verify == '':
            flash("Verify your Password!", 'warning')
            return render_template('register.html', title="Blogz", username=username)
        
        if verify != password:
            flash("Passwords do not Match!", 'warning')
            return render_template('register.html', title="Blogz", username=username)

        existing_user = User.query.filter_by(username=username).first()
        if not existing_user:
            new_user = User(username, password)
            db.session.add(new_user)
            db.session.commit()
            session['username'] = username
            return redirect('/newpost')
        else:
            flash("We already have the username {0}!!".format(username), 'warning')
    return render_template('register.html')

@app.route('/newpost', methods=['POST', 'GET'])
def newpost():

    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']

        if title == '':

            flash("Title cannot be blank!", 'warning')
            return render_template('newpost.html', title="Blogz", post_title=title, body=body)

        if body == '':

            flash("Blog cannot be blank!", 'warning')
            return render_template('newpost.html', title="Blogz", post_title=title, body=body)

        owner = User.query.filter_by(username=session['username']).first()
        

        new_post = Blog(title, body, owner)
        db.session.add(new_post)
        db.session.commit()
        postID = new_post.id
        post = Blog.query.filter_by(id=postID).first()
        
        return render_template('postdetail.html', title="Blogz", post=post )

    if request.method == 'GET':
        return render_template('newpost.html', title="Blogz")


@app.route('/blog', methods=['POST', 'GET'])
def blog():

    if request.method == 'GET':
        postID = request.args.get('id', default=None)
        if postID != None:
            post = Blog.query.filter_by(id=postID).first()
            return render_template('postdetail.html', title="Blogz", post=post)

        userID = request.args.get('userID', default=None)
        if userID != None:
            posts = Blog.query.filter_by(owner_id=userID).all()
            user = User.query.filter_by(id=userID).first()
            return render_template('userblog.html', title="Blogz", posts=posts, user=user)

    posts = Blog.query.filter_by().all()
    return render_template('blog.html', title="Blogz", posts=posts)


@app.route('/', methods=['POST', 'GET'])
def index():

    if request.method == 'GET':
        users = User.query.filter_by().all()
        return render_template('index.html', title="Blogz", users=users)

if __name__ == '__main__':
    app.run()