"""
Memo Routes
"""
import os
import re
from flask import (render_template, url_for, flash,current_app,
                   redirect, request, abort, Blueprint, send_from_directory)
from flask_login import current_user, login_required
from wtforms import SubmitField
from memos.flask_sqlalchemy_txns import transaction

from memos.models.MemoHistory import MemoHistory
from memos.models.User import User
from memos.memos.forms import MemoForm, MemoSearch
from memos.models.Memo import Memo
from memos.models.MemoFile import MemoFile
from memos.models.MemoActivity import MemoActivity

memos = Blueprint('memos', __name__)

@memos.route("/")
@memos.route("/memo")
@memos.route("/memo/<username>")
@memos.route("/memo/<username>/<memo_number>")
@memos.route("/memo/<username>/<memo_number>/<memo_version>")
def main(username=None,memo_number=None,memo_version=None):
    """ This route is used to display the list of memos """
    with transaction():
        pagesize = User.get_pagesize(current_user)
        page = request.args.get('page', 1, type=int)
        detail = request.args.get('detail')

        if detail is None:
            detail = False
        else:
            detail = True

        if username is not None and memo_number is None:
            combo = re.split("-",username)
            if len(combo) == 2:
                username = combo[0]
                memo_number = combo[1]
            if len(combo) == 3:
                username = combo[0]
                memo_number = combo[1]
                memo_version = combo[2]

        if memo_number is not None and re.match("^[0-9]+[a-zA-Z]+",memo_number):
            split = re.split("[a-zA-Z]",memo_number)
            memo_version = memo_number[len(split[0]):]
            memo_number = split[0]

        if memo_version is not None:
            memo_version = memo_version.upper()

        if current_user.is_anonymous:
            user = None
        else:
            user = current_user

        memo_list = Memo.get_memo_list(username=username,memo_number=memo_number,
                                    memo_version=memo_version,page=page,pagesize=pagesize)

        if len(memo_list.items) == 0:
            flash('No memos match that criteria','error')

        url_params = {}
        if username:
            url_params['username']=username

        next_page = "memos.main"

        return render_template('memo.html', memos=memo_list, title="memo",user=user,delegate=user,
                            signer=None, detail=detail,next_page=next_page,page=page,
                            url_params=url_params)


@memos.route("/file/memo/<string:username>/<int:memo_number>/<string:memo_version>/<string:uuid>")
def getfile(username,memo_number,memo_version,uuid):
    """    # this route will return the specified file"""
    with transaction():
        memo = Memo.find(username=username,memo_number=memo_number,memo_version=memo_version)

        if current_user.is_anonymous:
            user = None
        else:
            user = current_user

        if memo.has_access(user) is False:
            MemoHistory.activity(memo=memo,memo_activity=MemoActivity.IllegalFile,user=user)
            abort(403)

        memo_list = memo.get_files()
        for file in memo_list:
            if file.uuid == uuid:
                directory = os.path.join('static','memos',str(memo.user_id),str(memo_number),
                    memo_version)
                return send_from_directory(directory,file.uuid,download_name=file.filename,
                    as_attachment=True)

        return abort(404)

def process_file(new_memo,formfield):
    """This function will take the formfield, save the file
    into the filesystem at the right place"""
    with transaction():
        if formfield.data:
            f = formfield.data
            # make a directory
            path = new_memo.get_fullpath()
            os.makedirs(path,exist_ok=True)
            mfile = MemoFile(memo_id=new_memo.id,filename=f.filename)
            mfile.save()
            f.save(os.path.join(path, mfile.uuid))
            new_memo.num_files = new_memo.num_files + 1

@memos.route("/cu/memo",methods=['GET', 'POST'])
@memos.route("/cu/memo/<string:username>",methods=['GET'])
@memos.route("/cu/memo/<string:username>/<int:memo_number>",methods=['GET', 'POST'])
@login_required
def create_revise_submit(username=None,memo_number=None):
    """The get/post method to create revise and submit new memos"""
    with transaction():
        if username is None:
            username = current_user.username

        # first check to see if the user has permission
        owner = User.find(username=username)

        if owner is None:
            return abort(404)

        delegate = current_user

        if not Memo.can_create(owner=owner,delegate=delegate):
            return abort(403)

        current_app.logger.info(f"owner = {owner} delegate={delegate} memo_number={memo_number}")
        memo = Memo.create_revise(owner=owner,delegate=delegate,memo_number=memo_number)

        class FileForm(MemoForm):
            """# this class is used to add multiple file buttons"""
            @staticmethod
            def create(memo):
                """Create"""
                for idx,_ in enumerate(memo.get_files()):
                    button_name = f"file_{idx}"
                    setattr(FileForm, button_name, SubmitField('Remove'))
            def getField(self, field_name):
                """getField"""
                for f in self:
                    if f.name == field_name:
                        return f
                return None # pragma nocover - This case should never occur


        FileForm.create(memo)
        form = FileForm()

        if request.method == 'GET':
            form.title.data = memo.title
            form.keywords.data = memo.keywords
            form.distribution.data = memo.distribution
            form.signers.data = memo.signers['signers']
            form.confidential.data = memo.confidential
            form.references.data = memo.references['ref_string']

            form.username.data = username
            form.memo_number.data = memo.number
            form.memo_version.data = memo.version

            return render_template('create_memo.html', title=f'New Memo {memo}',form=form, legend=f'New Memo {memo}', user=owner, memo=memo)

        # Everthing from here down is POST

        if form.validate_on_submit():
            if form.cancel.data is True:
                return redirect(url_for('memos.cancel',username=form.username.data,
                                        memo_number=form.memo_number.data,memo_version=form.memo_version.data))

            memo.title = form.title.data
            memo.distribution = form.distribution.data
            memo.keywords = form.keywords.data
            memo.signers = form.signers.data
            memo.references = form.references.data
            memo.confidential = form.confidential.data

            process_file(memo,form.memodoc1)
            process_file(memo,form.memodoc2)
            process_file(memo,form.memodoc3)
            process_file(memo,form.memodoc4)
            process_file(memo,form.memodoc5)

            # make a json backup
            memo.save()

            # Look and see if they pressed a remove button on one of the files.
            for idx,file in enumerate(memo.get_files()):
                if hasattr(form,f'file_{idx}'):
                    status = getattr(form,f'file_{idx}')
                    if status.data is True:
                        file.remove_file(memo)
                        flash(f"Remove {file}",'success')
                        return redirect(request.url)  # redirect back to edit instead...

            if form.save.data is True:
                flash(f'{memo} has been saved!', 'success')
                return redirect(url_for('memos.main'))

            # creation is all done... all documents added... signatures etc.
            memo.process_state(acting=current_user)
            # make a json backup
            flash(f'{memo} has been created!', 'success')
            return redirect(url_for('memos.main'))

        return render_template('create_memo.html', title=f'New Memo {memo}',
                            form=form, legend=f'New Memo {memo}', user=delegate, memo=memo)


# bring up the list of all of the memos that the current user can sign
@memos.route("/inbox")
@memos.route("/inbox/<string:username>")
@login_required
def inbox(username=None):
    """ this function will return all of the memos in the users inbox"""
    with transaction():
        pagesize = User.get_pagesize(current_user)
        page = request.args.get('page', 1, type=int)
        next_page = 'memos.inbox'

        if username is None:
            user = current_user
        else:
            user = User.find(username=username)
            if user is None:
                return abort(404)

        delegate = current_user
        if not user.is_delegate(current_user):    
            return abort(403)

        memo_list = Memo.get_inbox(user,page,pagesize)
        inbox_list = [user] + [current_user] + current_user.delegate_for['users']

        url_params = {
            'username':username,
                }

        next_page = "memos.inbox"

        return render_template('memo.html', memos=memo_list, title=f"Inbox {username}", legend=f'Inbox: {username}',
                            user=user, delegate=delegate,next_page=next_page, url_params=url_params, inbox_list=inbox_list)


@memos.route("/drafts")
@memos.route("/drafts/<string:username>")
@login_required
def drafts(username=None):
    """this function will return all of the memos in the draft state for the
    user (or specified user)"""
    with transaction():
        pagesize = User.get_pagesize(current_user)
        page = request.args.get('page', 1, type=int)
        next_page = 'memos.drafts'

        if username is None:
            user = current_user
        else:
            user = User.find(username=username)
            if user is None:
                return abort(404)

        delegate = current_user
        if not user.is_delegate(current_user):    
            return abort(403)

        memo_list = Memo.get_drafts(user,page,pagesize)

        url_params = {}
        if username is not None:
            url_params['username']=username

        next_page = "memos.drafts"

        return render_template('memo.html', memos=memo_list, title=f"Inbox {username}", user=user, delegate=delegate,next_page=next_page, url_params=url_params)


###########################################################################
# State Machine Functions
###########################################################################

@memos.route("/sign/memo/<string:username>/<int:memo_number>/<string:memo_version>")
@login_required
def sign(username,memo_number,memo_version):
    """this function will attempt to sign the specified memo"""
    with transaction():
        signer = request.args.get('signer', type=str)

        current_app.logger.info(f"Signer = {signer}")

        if signer is None:
            signer = current_user
        else:
            signer = User.find(username=signer)
            if signer is None:
                return abort(404)

        delegate = current_user

        memo = Memo.find(username=username,memo_number=memo_number,memo_version=memo_version)
        if memo:
            if memo.sign(signer,delegate):
                flash(f'Sign {memo} Success', 'success')
            else:
                flash(f'Sign {memo} Failed', 'error')
        else:
            flash(f'Sign {username}-{memo_number}-{memo_version} Failed', 'error')
        return redirect(url_for('memos.main'))

@memos.route("/unsign/memo/<string:username>/<int:memo_number>/<string:memo_version>")
@login_required
def unsign(username,memo_number,memo_version):
    """this function will attempt to unsign a memo"""
    with transaction():
        next_page = request.args.get('next_page', type=str)
        page = request.args.get('page', 1, type=int)

        if next_page is None:
            next_page = "memos.main"

        signer = request.args.get('signer', type=str)

        if signer is None:
            signer = current_user
        else:
            signer = User.find(username=signer)
            if signer is None:
                return abort(404)

        delegate = current_user

        memo = Memo.find(username=username,memo_number=memo_number,memo_version=memo_version)
        if memo:
            if memo.unsign(signer,delegate):
                flash(f'Unsign {memo} success', 'success')
                return redirect(url_for('memos.main'))
            else:
                flash(f'Unsign {memo} Failed', 'error')
        else:
            flash(f'Unsign {username}-{memo_number}-{memo_version} Failed', 'error')

        return redirect(url_for(next_page,page=page,next_page=next_page))


@memos.route("/obsolete/memo/<string:username>/<int:memo_number>/<string:memo_version>")
@login_required
def obsolete(username,memo_number,memo_version):
    """Attempt to obsolete a memo"""
    with transaction():
        next_page = request.args.get('next_page', type=str)
        page = request.args.get('page', 1, type=int)

        if next_page is None:
            next_page = "memos.main"

        current_app.logger.info(f"Next Page = {next_page} page={page}")

        delegate = current_user

        memo = Memo.find(username=username,memo_number=memo_number,memo_version=memo_version)

        if memo:
            if memo.obsolete(delegate):
                flash(f'Obsolete {memo} Success', 'success')
            else:
                flash(f'Obsolete {memo} Failed', 'error')
        else:
            flash(f'Obsolete {username}-{memo_number}-{memo_version } Failed', 'error')

        return redirect(url_for(next_page,page=page,next_page=next_page))


@memos.route("/cancel/memo/<string:username>/<int:memo_number>/<string:memo_version>",methods=['GET'])
@login_required
def cancel(username=None,memo_number=0,memo_version=0):
    """Attempt to cancel a memo - only memos in the draft state"""
    with transaction():
        next_page = request.args.get('next_page', type=str)
        page = request.args.get('page', 1, type=int)

        if next_page is None:
            next_page = "memos.main"

        user = current_user

        memo = Memo.find(username=username,memo_number=memo_number,memo_version=memo_version)

        if memo:
            memostring = f"{memo}"
            if memo.cancel(user):
                flash(f'Canceled {memostring}', 'success')
            else:
                flash(f'Cancel {memo} Failed', 'error')
        else:
            flash(f'Cannot cancel memo {username}-{memo_number}-{memo_version}', 'error')

        return redirect(url_for(next_page,page=page,next_page=next_page))

@memos.route("/reject/memo/<string:username>/<int:memo_number>/<string:memo_version>")
@login_required
def reject(username,memo_number,memo_version):
    """Attempt to reject a memo in the signoff state"""
    with transaction():
        next_page = request.args.get('next_page', type=str)
        page = request.args.get('page', 1, type=int)

        if next_page is None:
            next_page = "memos.main"

        signer = request.args.get('signer', type=str)

        if signer is None:
            signer = current_user
        else:
            signer = User.find(username=signer)
            if signer is None:
                return abort(404)

        delegate = current_user

        memo = Memo.find(username=username,memo_number=memo_number,memo_version=memo_version)
        if memo:
            if memo.reject(signer,delegate):
                flash(f'Rejected {memo.user.username}-{memo.number}-{memo.version}', 'success')
            else:
                flash(f'Reject {memo.user.username}-{memo.number}-{memo.version} Failed', 'error')
        else:
            flash(f'Cannot unsign memo {username}-{memo_number}-{memo_version}', 'error')

        return redirect(url_for(next_page,page=page,next_page=next_page))

@memos.route("/search",methods=['GET', 'POST'])
def search():
    """The route to handle searching"""
    with transaction():
        pagesize = User.get_pagesize(current_user)
        page = request.args.get('page', 1, type=int)
        detail = request.args.get('detail')
        search_param = request.args.get('search')
        next_page = 'memos.search'
        if detail is None:
            detail = False
        else:
            detail = True

        if current_user.is_anonymous:
            user = None
        else:
            user = current_user

        form = MemoSearch()

        url_params = {}

        if form.validate_on_submit():

            if form.title.data and form.title.data != '':
                memos_found = Memo.search(title=form.title.data,page=page,pagesize=pagesize)
                search_param = f"title:{form.title.data}"
                url_params['search'] = search_param
                return render_template('memo.html', memos=memos_found, title="memo",user=user,delegate=user,detail=detail,next_page=next_page,url_params =url_params)

            if form.keywords.data and form.keywords.data != '':
                memos_found = Memo.search(keywords=form.keywords.data,page=page,pagesize=pagesize)
                search_param = f"keywords:{form.keywords.data}"
                url_params['search'] = search_param
                return render_template('memo.html', memos=memos_found, title="memo",user=user,delegate=user,detail=detail,next_page=next_page,url_params =url_params)

            if form.memo_ref.data and form.memo_ref.data != '':
                return redirect(url_for("memos.main",username=form.memo_ref.data,page=page))

            if form.username.data and form.username.data != '':
                return redirect(url_for("memos.main",username=form.username.data,page=page))

            if form.inbox.data and form.inbox.data != '':
                return redirect(url_for("memos.inbox",username=form.inbox.data,page=page))

            return render_template('memo_search.html', title='Memo Search ',legend='Search',form=form)


    # Everything below here is GET
        url_params = {}

        if search_param is not None:
            title = re.split('^title:',search_param,maxsplit=1)
            keywords = re.split('^keywords:',search_param,maxsplit=1)
            if len(title) == 2:
                memos_found = Memo.search(title=title[1],page=page,pagesize=pagesize)
                url_params['search']= f'title:{title[1]}'
            if len(keywords) == 2:
                memos_found = Memo.search(keywords=keywords[1],page=page,pagesize=pagesize)
                url_params['search']= f'keywords:{keywords[1]}'

            next_page = "memos.search"
            return render_template('memo.html', memos=memos_found, title="memo",user=user,delegate=user,detail=detail,next_page=next_page,url_params=url_params)

        return render_template('memo_search.html', title='Memo Search ',legend='Search',form=form)


@memos.route("/history")
@login_required
def history():
    """Look at the history table"""
    with transaction():
        pagesize = User.get_pagesize(current_user)
        page = request.args.get('page', 1, type=int)

        history_list = MemoHistory.get_history(page=page,pagesize=pagesize)
        url_params = {
                }

        next_page = "memos.history"
        return render_template('memo_history.html', history=history_list,next_page=next_page, url_params=url_params)
    