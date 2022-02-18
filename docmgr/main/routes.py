from flask import render_template, request, Blueprint, redirect, url_for

main = Blueprint('main', __name__)

@main.route("/about")
def about():
    return render_template('about.html', title='About')


@main.route("/home")
def home():
    return redirect(url_for("memos.memo_main"))
