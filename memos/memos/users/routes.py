""" User Routes """
import os
from flask import render_template, url_for, flash, redirect, request, Blueprint, current_app, abort
from flask_login import login_user, current_user, logout_user, login_required
from memos import db, bcrypt

from memos.users.forms import (RegistrationForm, LoginForm, UpdateAccountForm,
                                   RequestResetForm, ResetPasswordForm)
from memos.users.utils import save_picture, send_reset_email
from memos.models.User import User
from memos.extensions import ldap

users = Blueprint('users', __name__)

@users.route("/register", methods=['GET', 'POST'])
def register():
    if ldap:
        redirect(url_for('users.login'))
        
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = User.create_hash_pw(form.password.data)
        user = User(username=form.username.data, email=form.email.data, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash('Your account has been created! You are now able to log in', 'success')
        return redirect(url_for('users.login'))
    return render_template('register.html', title='Register', form=form)


@users.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    form = LoginForm()
    if form.validate_on_submit():
        login_ok = False
        ldap_pw_ok = False
        if ldap:
            try:
                ldap_user = ldap.get_object_details(form.email.data)
            except:
                ldap_user = None

            if ldap_user:
                ldap_pw_ok = ldap.bind_user(form.email.data, form.password.data)
                login_ok = ldap_pw_ok

        user = User.query.filter_by(email=form.email.data).first()
        
        current_app.logger.info(f"User = {user} form={form.email.data}")

        # If we validated a user with ldap, but they don't exist in the database, add them.
        if user is None and ldap_pw_ok:
            user = User(username=ldap_user[os.environ["LDAP_USER_NAME"]][0].decode('ASCII'), 
                email=ldap_user[os.environ["LDAP_EMAIL"]][0].decode('ASCII'), password='xx')
            db.session.add(user)
            db.session.commit()

        # If we validated a user with ldap, Update their permissions from LDAP groups.
        if ldap_user:
            user.admin = False
            user.readAll = False
            admin_groups = os.environ["LDAP_ADMIN_GRP"].split(";")
            readAll_groups = os.environ["LDAP_READ_GRP"].split(";")
            if isinstance(ldap_user['memberOf'], list):
                for grp in ldap_user['memberOf']:
                    grp = str(grp, 'utf-8')
                    for aGrp in admin_groups:
                        if grp.startswith(aGrp) : user.admin = True
                    for rGrp in readAll_groups:
                        if grp.startswith(rGrp) : user.readAll = True
                    
            db.session.commit()

        if ldap_user is None and user:
            try:
                 login_ok = user.check_password(form.password.data)
            except:  # blanked password from ldap creation has a 'bad salt'
                pass

        if login_ok:
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('main.home'))
        else:
            flash('Login Unsuccessful. Please check email and password', 'danger')

    return render_template('login.html', title='Login', form=form)


@users.route("/logout")
def logout():
    """
    This function logs the user out
    """
    logout_user()
    return redirect(url_for('main.home'))


@users.route("/account", methods=['GET', 'POST'])
@users.route("/account/<string:username>", methods=['GET', 'POST'])
@login_required
def account(username=None):
    """_summary_

    Args:
        username (_type_, optional): _description_. Defaults to None.

    Returns:
        _type_: _description_
    """
    if username is None:
        user = current_user
    else:
        user = User.find(username=username)

    if user is None:
        abort(404)        
    
    current_app.logger.info(f"User = {current_user.username} Delegate List= {user.delegates}")
    form = UpdateAccountForm()
    disable_submit_button = None
    if form.validate_on_submit():
        if form.picture.data:
            picture_file = save_picture(form.picture.data)
            current_user.image_file = picture_file

        if user is not current_user and not current_user.admin:
            abort(403)

#        if not ldap and current_user.admin:
#            user.username = form.username.data
        
        if not ldap and current_user is not user:
            user.admin = form.admin.data
            user.readAll = form.readAll.data

        if not ldap:
            user.email = form.email.data

        user.delegates = form.delegates.data
        user.pagesize = form.pagesize.data
        user.subscriptions = form.subscriptions.data
        db.session.add(user)
        db.session.commit()
        flash('Your account has been updated!', 'success')
        return redirect(url_for('users.account'))
    elif request.method == 'GET':

        form.username.render_kw['disabled'] = True
        form.email.render_kw['disabled'] = False
        form.delegates.render_kw['disabled'] = False
        form.admin.render_kw['disabled'] = False
        form.readAll.render_kw['disabled'] = False
        form.subscriptions.render_kw['disabled'] = False
        form.pagesize.render_kw['disabled'] = False

        disable_submit_button = False

        form.username.data = user.username
        form.email.data = user.email
        form.admin.data = user.admin
        form.readAll.data = user.readAll
        form.delegates.data = current_user.delegates['usernames']
        form.subscriptions.data = current_user.subscriptions
        form.pagesize.data = current_user.pagesize

        if not (user == current_user or current_user.admin):
            form.username.render_kw['disabled'] = True
            form.email.render_kw['disabled'] = True
            form.delegates.render_kw['disabled'] = True
            form.admin.render_kw['disabled'] = True
            form.readAll.render_kw['disabled'] = True
            form.subscriptions.render_kw['disabled'] = True
            form.pagesize.render_kw['disabled'] = True
            disable_submit_button = True

        if ldap: # all of these characteristics come from the LDAP groups
            form.username.render_kw['disabled'] = True
            form.email.render_kw['disabled'] = True
            form.admin.render_kw['disabled'] = True
            form.readAll.render_kw['disabled'] = True
        
    image_file = url_for('static', filename='profile_pics/' + current_user.image_file)
    return render_template('account.html', title='Account',
                           image_file=image_file, form=form,user=user,disable_submit_button=disable_submit_button)

'''
@users.route("/user/<string:username>")
def user_posts(username):
    page = request.args.get('page', 1, type=int)
    user = User.query.filter_by(username=username).first_or_404()
    posts = Post.query.filter_by(author=user)\
        .order_by(Post.date_posted.desc())\
        .paginate(page=page, per_page=5)
    return render_template('user_posts.html', posts=posts, user=user)

'''

@users.route("/reset_password", methods=['GET', 'POST'])
def reset_request():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    form = RequestResetForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        send_reset_email(user)
        flash('An email has been sent with instructions to reset your password.', 'info')
        return redirect(url_for('users.login'))
    return render_template('reset_request.html', title='Reset Password', form=form)


@users.route("/reset_password/<token>", methods=['GET', 'POST'])
def reset_token(token):
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    user = User.verify_reset_token(token)
    if user is None:
        flash('That is an invalid or expired token', 'warning')
        return redirect(url_for('users.reset_request'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user.password = hashed_password
        db.session.commit()
        flash('Your password has been updated! You are now able to log in', 'success')
        return redirect(url_for('users.login'))
    return render_template('reset_token.html', title='Reset Password', form=form)
