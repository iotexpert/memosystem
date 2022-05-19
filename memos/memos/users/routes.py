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
    if ldap: #pragma nocover  -- testing ldap is very environment centric.
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
        ldap_user = None
        if ldap: #pragma nocover  -- testing ldap is very environment centric.
            try:
                ldap_user = ldap.get_object_details(form.username.data)
            except:
                ldap_user = None

            if ldap_user:
                ldap_pw_ok = ldap.bind_user(form.username.data, form.password.data)
                login_ok = ldap_pw_ok

        user = User.query.filter_by(username=form.username.data).first()
        
        current_app.logger.debug(f"User = {user} form={form.username.data}")

        # If we validated a user with ldap, but they don't exist in the database, add them.
        if user is None and ldap_pw_ok: #pragma nocover  -- testing ldap is very environment centric.
            user = User(username=ldap_user[os.environ["LDAP_USER_NAME"]][0].decode('ASCII'), 
                email=ldap_user[os.environ["LDAP_EMAIL"]][0].decode('ASCII'), password='xx')
            db.session.add(user)
            db.session.commit()

        # If we validated a user with ldap, Update their permissions from LDAP groups.
        if ldap_user: #pragma nocover  -- testing ldap is very environment centric.
            user.admin = False
            user.readAll = False
            admin_groups = os.environ["LDAP_ADMIN_GRP"].split(";")
            readAll_groups = os.environ["LDAP_READ_GRP"].split(";")
            if 'memberOf' in ldap_user and isinstance(ldap_user['memberOf'], list):
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
            except:  # pragma nocover - blanked password from ldap creation has a 'bad salt'
                pass

        if login_ok:
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('main.home'))
        else:
            flash('Login Unsuccessful. Please check username and password', 'danger')

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
    form = UpdateAccountForm()

    if username is None:
        user = current_user
    else:
        user = User.find(username=username)

    if user is None:
        abort(404)        
    
    current_app.logger.info(f"User = {current_user.username} Delegate List= {user.delegates}")
    disable_submit_button = None
    if form.validate_on_submit():
        
        current_app.logger.info(f"User = {user} current_user={current_user} formusername={form.username.data}")
        if user is not current_user and not current_user.admin:
            abort(403)

        if form.picture.data:
            picture_file = save_picture(form.picture.data)
            user.image_file = picture_file

        if not ldap and current_user.admin:
            user.admin = form.admin.data
            user.readAll = form.readAll.data    

        if not ldap:
            current_app.logger.info(f"Email = {type(form.email.data)}")
            user.email = form.email.data

        user.delegates = form.delegates.data
        user.pagesize = form.pagesize.data
        user.subscriptions = form.subscriptions.data
        db.session.add(user)
        db.session.commit()
        flash('Your account has been updated!', 'success')
        return redirect(url_for('users.account',username=user.username))
    
    elif request.method == 'GET':

        form.username.render_kw['disabled'] = True
        form.email.render_kw['disabled'] = False
        form.delegates.render_kw['disabled'] = False
        form.admin.render_kw['disabled'] = False
        form.readAll.render_kw['disabled'] = False
        form.subscriptions.render_kw['disabled'] = False
        form.pagesize.render_kw['disabled'] = False

        disable_submit_button = False

        current_app.logger.info(f"username={user.username} email={user.email} readAll={user.readAll} admin={user.admin}")

        form.username.data = user.username
        form.email.data = user.email
        form.admin.data = user.admin
        form.readAll.data = user.readAll
        form.delegates.data = user.delegates['usernames']
        form.subscriptions.data = user.subscriptions
        form.pagesize.data = user.pagesize

        if not (user == current_user or current_user.admin):
            form.username.render_kw['disabled'] = True
            form.email.render_kw['disabled'] = True
            form.delegates.render_kw['disabled'] = True
            form.admin.render_kw['disabled'] = True
            form.readAll.render_kw['disabled'] = True
            form.subscriptions.render_kw['disabled'] = True
            form.pagesize.render_kw['disabled'] = True
            disable_submit_button = True

        if ldap: # pragma nocover - all of these characteristics come from the LDAP groups
            form.username.render_kw['disabled'] = True
            form.email.render_kw['disabled'] = True
            form.admin.render_kw['disabled'] = True
            form.readAll.render_kw['disabled'] = True
        
    image_file = url_for('static', filename='profile_pics/' + user.image_file)
    
        
    return render_template('account.html', username=user.username,title='Account',
                           image_file=image_file, form=form,user=user,disable_submit_button=disable_submit_button)

@users.route("/reset_password", methods=['GET', 'POST'])
def reset_request():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    form = RequestResetForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and len(user.email) > 2:
            send_reset_email(user)
            flash('An email has been sent with instructions to reset your password.', 'info')
        else:
            flash('There is no account with that email. You must register first.', 'warning')
            return redirect(url_for('users.reset_request'))
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
