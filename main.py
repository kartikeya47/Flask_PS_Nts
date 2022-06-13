from flask import Flask, render_template, request, session, redirect
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import json
from flask_mail import Mail


with open('config.json', 'r') as c:
    params = json.load(c)["params"]

local_server = True

app = Flask(__name__)


if local_server:
    app.config['SQLALCHEMY_DATABASE_URI'] = params['local_uri']
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = params['prod_uri']


db = SQLAlchemy(app)

app.secret_key = 'super-secret-key'


app.config.update(
    MAIL_SERVER='smtp.gmail.com',
    MAIL_PORT='465',
    MAIL_USE_SSL=True,
    MAIL_USERNAME=params['gmail-user'],
    MAIL_PASSWORD=params['gmail-password']
)

mail = Mail(app)


class Contacts(db.Model):
    sno = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    phone_num = db.Column(db.String(12), nullable=False)
    msg = db.Column(db.String(120), nullable=False)
    date = db.Column(db.String(12), nullable=False)
    email = db.Column(db.String(20), nullable=False)


class Posts(db.Model):
    sno = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(80), nullable=False)
    slug = db.Column(db.String(30), nullable=False)
    content = db.Column(db.String(120), nullable=False)
    date = db.Column(db.String(12), nullable=True)
    img_file = db.Column(db.String(12), nullable=True)


@app.route("/")
def home():
    posts = Posts.query.filter_by().all()[0:params['no_of_posts']]
    return render_template("index.html", params=params, posts=posts)


@app.route("/post/<string:post_slug>")
def post_route(post_slug):
    post = Posts.query.filter_by(slug=post_slug).first()
    return render_template("post.html", params=params, post1=post)


@app.route("/about")
def about():
    return render_template("about.html", params=params)


@app.route("/login", methods=['GET', 'POST'])
def login_page():
    posts = Posts.query.all()

    if 'user' in session and session['user'] == params['gmail-user']:
        return render_template("dashboard.html", params=params, posts=posts)

    if request.method == 'POST':
        username = request.form.get('uname')
        userpass = request.form.get('pass')
        if username == params['gmail-user'] and userpass == params['gmail-password']:
            # set the session variable
            session['user'] = username  # Telling the FlaskApp that this user is logged in
            return render_template("dashboard.html", params=params, posts=posts)
        else:
            return render_template("login.html", params=params)

    return render_template("login.html", params=params)


@app.route("/logout")
def logout():
    session.pop('user')
    return redirect('/login')


@app.route("/delete/<string:sno>", methods=['GET', 'POST'])
def delete(sno):
    if 'user' in session and session['user'] == params['gmail-user']:
        post = Posts.query.filter_by(sno=sno).first()
        db.session.delete(post)
        db.session.commit()
    return redirect('/login')


@app.route("/contact", methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':  # Add Entry to the Database, when the submit button is pressed
        name = request.form.get('name')
        email = request.form.get('email')
        phone = request.form.get('phone')
        message = request.form.get('message')
        entry = Contacts(name=name, phone_num=phone, msg=message, date=datetime.now(),
                         email=email)  # All entries got fetched
        db.session.add(entry)  # Now, add these entries to the database
        db.session.commit()
        mail.send_message('New message from ' + name, sender=email, recipients=[params['gmail-user']],
                          body=message + "\n" + phone)
    return render_template('contact.html', params=params)


@app.route("/edit/<string:sno>", methods=['GET', 'POST'])
def edit(sno):
    if 'user' in session and session['user'] == params['gmail-user']:
        if request.method == 'POST':
            box_title = request.form.get('title')
            slug = request.form.get('slug')
            content = request.form.get('content')
            img_file = request.form.get('img_file')
            if sno == '0':
                post = Posts(title=box_title, slug=slug, content=content, img_file=img_file)
                db.session.add(post)
                db.session.commit()
            else:
                post = Posts.query.filter_by(sno=sno).first()
                post.title = box_title
                post.slug = slug
                post.content = content
                post.img_file = img_file
                db.session.commit()
                return redirect('/edit/+sno')
        post = Posts.query.filter_by(sno=sno).first()
        return render_template('edit.html', params=params, post=post)


app.run(debug=True)
