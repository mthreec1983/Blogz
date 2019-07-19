from flask import Flask, request, redirect, render_template, flash, session
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://Blogz:scoobydoo3@localhost:8889/Blogz'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key = "y33hgn77"

class Blog(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    body = db.Column(db.Text)
    owner_id = db.Column(db.Integer,  db.ForeignKey('user.id'))
    
    
    def __init__(self, title, body):
        self.title = title
        self.body = body
        

class User(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(120), unique=True)
    password = db.Column(db.String(120))
    blogz = db.relationship('Blog', backref='owner')

    def __init__(self, username, password):
        self.username = username
        self.password = password 

@app.before_request
def require_login():
    allowed_routes = ['login', 'signup', 'index', 'blog']
    if request.endpoint not in allowed_routes and 'user' not in session:
        return redirect('/')

@app.route('/')
def index():
    users = User.query.all()
    return render_template('index.html', title='Home', users=users, header='Blog Users')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['Username']
        password = request.form['Password']
        user = User.query.filter_by(username=username).first()
        if user and user.password == password:
            session['username'] = username
            flash('You are logged in!')
            return redirect('/')
        else:
            flash('That combination is not recognized, please try again', 'error')
    
    return render_template('login.html')
            
@app.route('/blog')
def blog():
    blog_id = request.args.get('id')

    if blog_id == None:
        posts = Blog.query.all()
        return render_template('blog.html', posts=posts, title='Blogz')
    else:
        post = Blog.query.get(blog_id)
        return render_template('entry.html', post=post, title='Blog Entry')

@app.route('/signup', methods=['POST', 'GET'])
def signup():
    if request.method == 'POST':
        username = request.form['Username']
        password = request.form['Password']
        verify = request.form['verify']

        existing_user = User.query.filter_by(username=username).first()

        if password.isspace():
            flash('Password must not contain spaces.', 'error')
        elif username.isspace():
            flash('Username must not contain spaces', 'error')
        elif password != verify:
            flash('Password does not match', "error")
        elif len(username) < 3 or len(username) > 20:
            flash('Username must be 3-20 characters', 'error')
        elif existing_user:
            flash('User already exists', 'error')
        elif not existing_user:
            new_user = User(username, password)
            db.session.add(new_user)
            db.session.commit()
            session['username'] = username
            return redirect('/')  
        
    return render_template('signup.html')

@app.route('/logout')
def logout():
    del session['username']
    return redirect('/index')

@app.route('/newpost', methods=['POST', 'GET'])
def new_post():
    if request.method == 'POST':
        blog_title = request.form['blog-title']
        blog_body = request.form['blog-entry']

        if blog_title == '':
            flash("Oops Please enter a title!", 'error')
        if blog_body == "":
            flash("Blog cannot be empty!", 'error')

        if blog_title and blog_body:
            new_entry = Blog(blog_title, blog_body)     
            db.session.add(new_entry)
            db.session.commit()        
            return redirect('/blog?id={}'.format(new_entry.id)) 
        else:
            return render_template('newpost.html', title='New Entry', 
                blog_title=blog_title, blog_body=blog_body)
    
    return render_template('newpost.html', title='New Entry')

if  __name__ == "__main__":
    app.run()