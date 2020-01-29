
from flask import Flask, g, render_template, flash, redirect, url_for, abort
from flask_bcrypt import check_password_hash
from flask_login import (LoginManager, login_user, logout_user,
                         login_required, current_user)

import forms
import models

#DEBUG = True
#PORT = 8000
#HOST = '0.0.0.0'

app = Flask(__name__)
app.secret_key = 'jgsfvemgwer73845crgjesfgd'

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'


@login_manager.user_loader
def load_user(userid):
    try:
        return models.User.get(models.User.id == userid)
    except models.DoesNotExist:
        return None    


@app.before_request
def before_request():
    """ Connect to the database before each request. """
    g.db = models.DATABASE
    g.db.connect()
    g.user = current_user


@app.after_request
def after_request(response):
    """ Close the database connection after each request. """
    g.db.close()
    return response


@app.route('/register', methods=('GET', 'POST'))
def register():
    form = forms.RegisterForm()
    if form.validate_on_submit():
        flash("YOu have registered", "success")
        models.User.create_user(
            username=form.username.data,
            email=form.email.data,
            password=form.password.data
        )
        return redirect(url_for('index'))
    return render_template('register.html', form=form)    

@app.route('/', methods=['GET'])
@app.route('/entries', methods=['GET'])
def index():
    stream = models.Post.select().limit(100)
    return render_template('index.html', stream=stream)    


@app.route('/stream')
@app.route('/stream/<username>')
def stream(username=None):
    template = 'stream.hmtl'
    if username and username != current_user.username:
        try:
            user = models.User.select().where(
                models.User.username**username).get()
        except models.DoesNotExist:
            abort(404)
        else:            
            stream = user.posts.limit(100)
    else:
        stream = current_user.get_stream().limit(100)
        user = current_user
    if username:
        template = 'user_stream.html'

    return render_template(template, stream=stream, user=user)      


@app.route('/entries/<id>')
def view_post(id):
    try:
        post = models.Post.get(models.Post.id == id)
    except models.DoesNotExist:
        abort(404)
    return render_template('detail.html',post=post)       


@app.route('/entries/<id>/edit', methods=['GET', 'POST'])
@login_required
def edit_post(id):
    try:
        post = models.Post.get(models.Post.id == id)
    except models.DoesNotExist:
        abort(404)
    else:        
        form = forms.AddEntryForm()
        if form.validate_on_submit():
            with models.DATABASE.transaction():
                post.title = form.title.data
                post.time_spent = form.time_spent.data
                post.content = form.content.data
                post.date = form.date.data
                post.save()
                flash('Entry was edited successfully')
                return redirect(url_for('view_post', id=post.id))
        return render_template('edit.html', form=form, post=post)    


@app.route('/entries/<id>/delete', methods=['GET', 'POST'])
@login_required
def delete_post(id):
    try:
        post = models.Post.get(models.Post.id == id)
    except models.DoesNotExist:
       abort(404)

    post.delete_instance()
    flash('Post deleted')
    return redirect(url_for('index'))


@app.route('/login', methods=('GET', 'POST'))
def login():
    form = forms.LoginForm()
    if form.validate_on_submit():
        try:
            user = models.User.get(models.User.email == form.email.data)
        except models.DoesNotExist:
            flash('Your email or password does not match', 'error')
        else:
            if check_password_hash(user.password, form.password.data):
                login_user(user)
                flash('You are logged in', 'success')
                return redirect(url_for('index'))
            else:
                flash('Your email or password does not match', 'error')
    return render_template('login.html', form=form)            


@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You are logged out', 'success')
    return redirect(url_for('index'))


@app.route('/entries/new', methods=('GET', 'POST'))
@login_required
def add_entry():
    form = forms.AddEntryForm()
    if form.validate_on_submit():
        models.Post.create(user=g.user._get_current_object(),
                           content=form.content.data.strip(),
                           title=form.title.data.strip(),
                           time_spent=form.time_spent.data.strip(),
                           resources=form.resources.data.strip(),
                           date=form.date.data
        )
        flash('Message posted! Thanks!', 'success')
        return redirect(url_for('index'))
    return render_template('new_entry.html', form=form)    


@app.errorhandler(404)
def not_found(error):
    return render_template('404.html'), 404


if __name__ == "__main__":
    models.initialize()
    try:
        models.User.create_user(
            username="olya",
            email="olya@mail.com",
            password="password",
            admin = True
        )
    except ValueError:
        pass    
    app.run(debug=True)   



