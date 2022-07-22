""" ADMIN Routes """
import os
from flask import render_template, url_for, flash, redirect, request, Blueprint, current_app, abort
from flask_login import login_user, current_user, logout_user, login_required
from sqlalchemy import false
from memos import db
from memos.flask_sqlalchemy_txns import transaction
from memos.models.Memo import Memo
from memos.admin.forms import AdminForm

admin = Blueprint('admin', __name__)

@admin.route("/admin", methods=['GET'])
@login_required
def main():
    if current_user.admin == False:
        abort(403)

    with transaction():    
        admin_form = AdminForm()
    return render_template('admin.html', title='Admin',form=admin_form)

@admin.route("/admin/rename",methods = ['POST'])
@login_required
def rename():    
    if current_user.admin == False:
        abort(403)
    
    with transaction():
        admin_form = AdminForm()
        
        if admin_form.validate_on_submit():
            rval = Memo.rename(admin_form.source.data,admin_form.destination.data)
            if rval:
                flash(f'Sucessful rename src = {admin_form.source.data} dst = {admin_form.destination.data}', 'success')
            else:        
                flash(f'Failed to rename source="{admin_form.source.data}" destination="{admin_form.destination.data}"', 'danger')

    return redirect(url_for('admin.main', form=admin_form))



@admin.route("/admin/delete",methods = ['POST'])
@login_required
def delete():
 
    if current_user.admin is False:
        abort(403)

    with transaction():
        admin_form = AdminForm()

        if admin_form.validate_on_submit():
            ref = Memo.parse_reference(admin_form.delete_ref.data)

            current_app.logger.info(f"{ref}")
            if ref["valid"] is True and ref["memo"].cancel(current_user,validate_user=False) is True:
                flash(f'Sucessful delete {admin_form.delete_ref.data}', 'success')
            else:
                flash(f'Failed to delete "{admin_form.delete_ref.data}" invalid reference', 'danger')
 
    return redirect(url_for('admin.main'))