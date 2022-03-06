from flask import render_template, Blueprint, redirect, url_for
from flask import current_app
import os

main = Blueprint('main', __name__)

@main.route("/help")
def help():
    md_text= open(os.path.join(current_app.root_path,"static","doc","help.md"),"r").read()
    return render_template('help.html', title='Help', md_text=md_text)


@main.route("/home")
def home():
    return redirect(url_for("memos.main"))

