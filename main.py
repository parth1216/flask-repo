from flask import Flask, render_template, request, session
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail

import json
from datetime import datetime


with open('config.json', 'r') as c:
    params = json.load(c)["params"]

app = Flask(__name__)
app.secret_key='super-secret-key'
local_server = True
app.config.update(
    MAIL_SERVER = 'smtp.gmail.com',
    MAIL_PORT = '465',
    MAIL_USE_SSL= True,
    MAIL_USERNAME = params['gmail_user'],
    MAIL_PASSWORD = params['gmail_pass']

)
mail = Mail(app)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
if (local_server):
    app.config['SQLALCHEMY_DATABASE_URI'] = params['local_uri']
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = params['prod_uri']
db = SQLAlchemy(app)

class Contacts(db.Model):
    sno = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    phone_num = db.Column(db.String(12), nullable=False)
    msg = db.Column(db.String(120), nullable=False)
    date = db.Column(db.String(12), nullable=True)
    email = db.Column(db.String(20), nullable=False)

class Posts(db.Model):
    sno = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(80), nullable=False)
    tag_line = db.Column(db.String(100), nullable=False)
    slug = db.Column(db.String(22), nullable=False)
    content = db.Column(db.String(120), nullable=False)
    date = db.Column(db.String(12), nullable=True)
    img_file = db.Column(db.String(50), nullable=False)



@app.route("/index")
def index():
    posts = Posts.query.filter_by().all()[0:params['no_of_posts']]
    return render_template('index.html', params=params, posts=posts)

@app.route("/post/<string:post_slug>", methods= ['GET'])
def post_route(post_slug):
    post = Posts.query.filter_by(slug=post_slug).first()
    return render_template('post.html', params = params, post=post)

@app.route("/about")
def about():
    return render_template('about.html', params=params)

@app.route("/dashboard", methods= ['GET', 'POST'])
def dashboard():
    if ('user' in session and session['user']==params['admin_user']):
        posts = Posts.query.all()
        return render_template('dashboard.html', params=params, posts=posts)
    if request.method == 'POST':
        username = request.form.get('uname')
        userpass = request.form.get('pass')
        if (username==params['admin_user'] and userpass==params['admin_pass']):
            #set the session variables
            session['user'] = username
            posts=Posts.query.all()

            return render_template('dashboard.html', params=params, posts=posts)

    else:
        return render_template('login.html', params=params)

@app.route("/edit/<string:sno>", methods = ['GET', 'POST'])
def edit(sno):
    if ('user' in session and session['user'] == params['admin_user']):
        if (request.method == 'POST'):

            box_title = request.form.get('title')
            print(box_title)
            tline = request.form.get('tline')
            print(tline)
            slug = request.form.get('slug')
            print(slug)
            content = request.form.get('content')
            print(content)
            img_file = request.form.get('img_file')
            print(img_file)
            date = datetime.now()
            print(date)
            if sno=='0':
                post = Posts(title=box_title, slug=slug, content=content, tag_line=tline, img_file=img_file, date=date)
                db.session.add(post)
                db.session.commit()

    return render_template('edit.html', params=params, sno=sno)






@app.route("/contact", methods = ['GET', 'POST'])
def contact():
    if (request.method == 'POST'):
        '''ADD ENATRY TO THE DATABASE'''
        
        name = request.form.get('name')
        email = request.form.get('email')
        phone = request.form.get('phone')
        message = request.form.get('message')
        
        entry = Contacts(name = name, phone_num = phone, msg = message, date = datetime.now(), email = email)
        db.session.add(entry)
        db.session.commit()

        mail.send_message('New message from coding thunder by ' + name,
            sender=email,
            recipients = [params['gmail_user']],
            body = message + "\n" +"phone no. : " + phone

        )
    return render_template('contact.html', params=params)



app.run(debug=True)



# sudo /opt/lampp/lampp start ==>> turn on xampp