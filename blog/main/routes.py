from flask import Blueprint, request, render_template
from blog.models import Post

main = Blueprint('main', __name__)


@main.route("/")
def home():
    return render_template('home.html')


@main.route("/posts")
def posts():
    # posts = Post.query.all()
    page = request.args.get('page', 1, type=int)
    posts = Post.query.order_by(
        Post.date_posted.desc()).paginate(page=page, per_page=6)

    return render_template('posts.html', posts=posts)
