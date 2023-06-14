from flask import Blueprint, request, redirect, flash, render_template, url_for
from flask_login import login_required, current_user, login_user, logout_user
from blog.models import Post, User
from blog import db, bcrypt
from blog.user.forms import LoginForm, RegistrationForm, RequestResetForm, ResetPasswordForm, UpdateAccountForm
from blog.user.utils import send_reset_email, save_picture

user = Blueprint('user', __name__)

@user.route("/register", methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect('/')
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_pw = bcrypt.generate_password_hash(
            form.password.data).decode('utf-8')
        user = User(username=form.username.data,
                    email=form.email.data, password=hashed_pw)
        db.session.add(user)
        db.session.commit()
        flash(f"Account created for {form.username.data}! You are now able to log in.", 'success')
        return redirect("/login")
    return render_template('register.html', form=form)


@user.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect('/')
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, form.remember.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect("/")
        else:
            flash("login failed. please check email and password", 'danger')
    return render_template('login.html', form=form)

@user.route('/logout')
def logout():
    logout_user()
    return redirect('/')


@user.route('/account', methods=['GET', 'POST'])
@login_required
def account():
    image_file = url_for('static', filename='profile_pics/'+current_user.image_file)
    return render_template('account.html', image_file=image_file)

@user.route('/account/update', methods=['GET', 'POST'])
@login_required
def update_account():
    form = UpdateAccountForm()
    if form.validate_on_submit():
        if form.picture.data:
            picture_file = save_picture(form.picture.data)
            current_user.image_file = picture_file
        current_user.username = form.username.data
        current_user.email = form.email.data
        db.session.commit()
        flash('your account has been updated', 'success')
        return redirect('/account')
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
    
    image_file = url_for('static', filename='profile_pics/'+current_user.image_file)
    return render_template('update_account.html', image_file=image_file, form=form)

@user.route("/user/<string:username>")
def user_posts(username):
    page = request.args.get('page', 1, type=int)
    user = User.query.filter_by(username=username).first_or_404()
    posts_count = Post.query.filter_by(author=user).count()
    print(posts_count)
    posts = Post.query.filter_by(author=user)\
        .order_by(Post.date_posted.desc())\
        .paginate(page=page, per_page=5)
    return render_template('user_posts.html', posts=posts, user=user, posts_count=posts_count)


@user.route("/reset_password", methods=['GET', 'POST'])
def reset_request():
    if current_user.is_authenticated:
        return redirect('/')
    form = RequestResetForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        send_reset_email(user)
        flash('password reset link has been sent to your email', 'info')
        return redirect('/login')
    return render_template('reset_request.html', form=form)

@user.route('/reset_password/<token>', methods=['POST', 'GET'])
def reset_token(token):
    if current_user.is_authenticated:
        return redirect("/")
    user = User.verify_reset_token(token)
    if user is None:
        flash("That is an invalid or expired token", 'warning')
        return redirect('/reset_request')
    form = ResetPasswordForm()
    if form.validate_on_submit():
        hashed_pw = bcrypt.generate_password_hash(form.password.data)
        user.password = hashed_pw
        db.session.commit()
        flash('Your password has been updated! You are now able to log in.', 'success')
        return redirect('/login')
    return render_template('reset_token.html', form=form)