import os
from flask import (render_template, url_for, flash,current_app,
                   redirect, request, abort, Blueprint, send_from_directory)
from flask_login import current_user, login_required
from docmgr.models.MemoSignature import MemoSignature

from docmgr.models.User import User
from docmgr.memos.forms import MemoForm, MemoSearch
from docmgr.models.User import User
from docmgr.models.Memo import Memo,MemoState
from docmgr.models.MemoFile import MemoFile

memos = Blueprint('memos', __name__)

@memos.route("/")
@memos.route("/memo")
@memos.route("/memo/<string:username>")
@memos.route("/memo/<string:username>/<int:memo_number>")
@memos.route("/memo/<string:username>/<int:memo_number>/<int:memo_version>")
def memo_main(username=None,memo_number=None,memo_version=None):
    pagesize = 10
    page = request.args.get('page', 1, type=int)
    detail = request.args.get('detail')
    if detail == None:
        detail = False
    else:
        detail = True
            
    current_app.logger.info(f"User = {current_user} username={username} memo_number={memo_number} memo_version={memo_version}")

    
    if current_user.is_anonymous:
        user = None
    else:
        user = User.find(userid=current_user.id)


    memo_list = Memo.get_memo_list(username,memo_number,memo_version,pagesize,page)
    for memo in memo_list.items:
        current_app.logger.info(f"References = {memo.references}")

    files = None       

    if len(memo_list.items) == 0:
        flash('No memos match that criteria','failure')

    return render_template('memo.html', memos=memo_list, title="memo", details=False, user=user,delegate=user, signer=None, detail=detail)
 

@memos.route("/file/memo/<string:username>/<int:memo_number>/<int:memo_version>/<string:uuid>")
def getfile(username,memo_number,memo_version,uuid):

    memo = Memo.find(username=username,memo_number=memo_number,memo_version=memo_version)
    current_app.logger.info(f'Find File {username}/{memo_number}/{memo_version}/{uuid} memo={memo}')
    
    if current_user.is_anonymous:
        usr = None
    else:
        usr = current_user.username

    user = User.find(usr)
    if memo.has_access(user) == False:
        abort(403)

    memo_list = memo.get_files()
    for file in memo_list:
        current_app.logger.info(f"File = {file.uuid} {file.filename}")
        if file.uuid == uuid:
            directory = os.path.join('static','memos',str(memo.user_id),str(memo_number),str(memo_version))
            current_app.logger.info(f"Found Match directory={directory}")
            return send_from_directory(directory,file.uuid,attachment_filename=file.filename,as_attachment=True)

    abort(404)

def process_file(new_memo,formfield):
    if formfield.data:
        f = formfield.data
        # make a directory
        path = new_memo.get_fullpath()
        os.makedirs(path,exist_ok=True)
        mfile = MemoFile(memo_id=new_memo.id,filename=f.filename)
        current_app.logger.info(f"Mfile ={mfile.filename} UUID={mfile.uuid}")
        mfile.save()
        f.save(os.path.join(path, mfile.uuid))
        new_memo.num_files = new_memo.num_files + 1
        new_memo.save()

@memos.route("/cu/memo",methods=['GET', 'POST'])
@memos.route("/cu/memo/<string:username>",methods=['GET'])
@memos.route("/cu/memo/<string:username>/<int:memo_number>",methods=['GET', 'POST'])
@login_required
def create_revise_submit(username=None,memo_number=None):
    
    current_app.logger.info(f"In create update {username} {memo_number}")
    if username == None:
        username = current_user.username  

    # first check to see if the user has permission
    owner = User.find(username=username)

    if owner == None:
        return abort(404)

    delegate = User.find(username=current_user.username)
    
    current_app.logger.info(f"owner={owner} delegate={delegate}")
    
    if not Memo.can_create(owner=owner,delegate=delegate):
        return abort(403)

    memo = None

    form = MemoForm()
    
#    def cancel(username=None,memo_number=0,memo_version=0):

    if request.method == 'POST' and form.cancel.data == True:
        return redirect(url_for('memos.cancel',username=form.username.data,memo_number=form.memo_number.data,memo_version=form.memo_version.data))    

        
    if request.method == 'POST' and form.save.data == True:
        current_app.logger.info('They Pressed Save')
        memo_number = int(form.memo_number.data)
        memo_version = int(form.memo_version.data)

        current_app.logger.info(f"Find {form.username.data} {memo_number} {memo_version}")

        memo = Memo.find(username=form.username.data,memo_number=memo_number,memo_version=memo_version)  

    
        if memo == None:
            current_app.logger.info("memo not found WTF")
            return abort(404)
        
        if memo.memo_state != MemoState.Draft: 
            flash(f'You may only revise Draft memos','error')
            return redirect(url_for('memos.memo_main'))    

        current_app.logger.info(f"Memo in draft state... that is good")

        memo.title = form.title.data
        memo.distribution = form.distribution.data
        memo.keywords = form.keywords.data
        memo.signers = form.signers.data
        memo.confidential = form.confidential.data        
        memo.references = form.references.data

        process_file(memo,form.memodoc1)
        process_file(memo,form.memodoc2)  
        process_file(memo,form.memodoc3)
        process_file(memo,form.memodoc4)
        process_file(memo,form.memodoc5)

        # make a json backup
        memo.save()

        flash(f'{memo} has been saved!', 'success')
        return redirect(url_for('memos.memo_main'))


    # just user case
    if request.method == 'GET':
        memo = Memo.create_revise(owner=owner,delegate=delegate,memo_number=memo_number)

        form.title.data = memo.title
        form.keywords.data = memo.keywords
        form.distribution.data = memo.distribution
        form.signers.data = memo.signers['signers']
        form.confidential.data = memo.confidential
        form.references.data = memo.references['refs']
        
        form.username.data = username
        form.memo_number.data = memo.number
        form.memo_version.data = memo.version

        current_app.logger.info(f"User= {form.username.data} Memo={form.memo_number.data} Version={form.memo_version.data}")

    if form.validate_on_submit():

        current_app.logger.info(f"Form is validated... now deal with the data")
        memo_number = int(form.memo_number.data)
        memo_version = int(form.memo_version.data)

        current_app.logger.info(f"Find {form.username.data} {memo_number} {memo_version}")

        memo = Memo.find(username=form.username.data,memo_number=memo_number,memo_version=memo_version)  

        current_app.logger.info(f"ARH Memo = {memo}")
    
        if memo == None:
            current_app.logger.info("memo not found WTF")
            return abort(404)
        
        if memo.memo_state != MemoState.Draft: 
            flash(f'You may only revise Draft memos','error')
            return redirect(url_for('memos.memo_main'))    

        current_app.logger.info(f"Memo in draft state... that is good")

        memo.title = form.title.data
        memo.distribution = form.distribution.data
        memo.keywords = form.keywords.data
        memo.signers = form.signers.data
        memo.confidential = form.confidential.data
        
        memo.references = form.references.data

        process_file(memo,form.memodoc1)
        process_file(memo,form.memodoc2)  
        process_file(memo,form.memodoc3)
        process_file(memo,form.memodoc4)
        process_file(memo,form.memodoc5)

        # creation is all done... all documents added... signatures etc.
        memo.process_state()

        # make a json backup
        memo.save()

        flash(f'{memo} has been created!', 'success')
        return redirect(url_for('memos.memo_main'))
    
    return render_template('create_memo.html', title='New Memo 123 ',form=form, legend=f'New Memo {memo}', user=delegate, memo=memo)

# bring up the list of all of the memos that the current user can sign
@memos.route("/inbox")
@memos.route("/inbox/<string:username>")
@login_required
def inbox(username=None):
    if username==None:
        username = current_user.username

    user = User.find(username=username)


    delegate = User.find(username=current_user.username)
    
    current_app.logger.info(f"Sign memos for {user}")
    
    current_app.logger.info(f"{delegate.get_who_delegated()}")
    
    page = request.args.get('page', 1, type=int)
    memo_list = Memo.get_inbox(user)
    current_app.logger.info(f"Memoslist for {user.username} memo_list={memo_list}")
    return render_template('memo.html', memos=memo_list, title=f"Inbox {username}", user=user, delegate=delegate)


@memos.route("/drafts")
@memos.route("/drafts/<string:username>")
@login_required
def drafts(username=None):
    if username==None:
        username = current_user.username

    user = User.find(username=username)
    delegate = User.find(username=current_user.username)

    page = request.args.get('page', 1, type=int)
    memo_list = Memo.get_drafts(user)
    return render_template('memo.html', memos=memo_list, title=f"Inbox {username}", user=user, delegate=delegate)


###########################################################################
# State Machine Functions
###########################################################################

@memos.route("/sign/memo/<string:username>/<int:memo_number>/<int:memo_version>")
@login_required
def sign(username,memo_number,memo_version):
    
    signer = request.args.get('signer', type=str)

    signer_username = current_user.username

    if signer != None:
       signer_username = signer
    
    signer = User.find(username=signer_username)
    delegate = User.find(username=current_user.username)
    
    memo = Memo.find(username=username,memo_number=memo_number,memo_version=memo_version)
    if memo:
        if memo.sign(signer,delegate):            
            flash(f'Sign {memo} Success', 'success')
        else:
            flash(f'Sign {memo} Failed', 'error')
    else:
        flash(f'Sign {username}-{memo_number}-{memo_version} Failed', 'error')
    return redirect(url_for('memos.memo_main'))



@memos.route("/unsign/memo/<string:username>/<int:memo_number>/<int:memo_version>")
@login_required
def unsign(username,memo_number,memo_version):
    
    signer = request.args.get('signer', type=str)

    signer_username = current_user.username

    if signer != None:
       signer_username = signer
    
    signer = User.find(username=signer_username)
    delegate = User.find(username=current_user.username)
    
    memo = Memo.find(username=username,memo_number=memo_number,memo_version=memo_version)
    if memo:
        if memo.unsign(signer,delegate):            
            flash(f'Unsign {memo} success', 'success')
            return redirect(url_for('memos.memo_main'))
        else:
            flash(f'Unsign {memo} Failed', 'error')
    else:
        flash(f'Unsign {username}-{memo_number}-{memo_version} Failed', 'error')
    return redirect(url_for('memos.memo_main'))


@memos.route("/obsolete/memo/<string:username>/<int:memo_number>/<int:memo_version>")
@login_required
def obsolete(username,memo_number,memo_version):
    
    delegate = User.find(username=current_user.username)
  
    memo = Memo.find(username=username,memo_number=memo_number,memo_version=memo_version)
    
    current_app.logger.info(f"Found memo={memo}")
    if memo:
        if memo.obsolete(delegate):            
            flash(f'Obsolete {memo} Success', 'success')
        else:
            flash(f'Obsolete {memo} Failed', 'error')
    else:
        flash(f'Obsolete {username}-{memo_number}-{memo_version } Failed', 'error')
    return redirect(url_for('memos.memo_main'))



@memos.route("/cancel/memo/<string:username>/<int:memo_number>/<int:memo_version>",methods=['GET'])
@login_required
def cancel(username=None,memo_number=0,memo_version=0):
    user = User.find(username=current_user.username)
    memo = Memo.find(username=username,memo_number=memo_number,memo_version=memo_version)
    
    current_app.logger.info(f"Found memo={memo}")
    if memo:
        if memo.cancel(user):            
            flash(f'Canceled {memo}', 'success')
        else:
            flash(f'Canceled {memo} Failed', 'error')
    else:
        flash(f'Cannot cancel memo {username}-{memo_number}-{memo_version}', 'error')

    return redirect(url_for('memos.memo_main'))


@memos.route("/reject/memo/<string:username>/<int:memo_number>/<int:memo_version>")
@login_required
def reject(username,memo_number,memo_version):
    
    signer = request.args.get('signer', type=str)

    signer_username = current_user.username

    if signer != None:
       signer_username = signer
    
    signer = User.find(username=signer_username)
    delegate = User.find(username=current_user.username)
    
    memo = Memo.find(username=username,memo_number=memo_number,memo_version=memo_version)
    if memo:
        if memo.reject(signer,delegate):            
            flash(f'Rejected {memo.user.username}-{memo.number}-{memo.version}', 'success')
        else:
            flash(f'Rejected {memo.user.username}-{memo.number}-{memo.version}', 'success')
    else:
        flash(f'Cannot unsign memo {username}-{memo_number}-{memo_version}', 'failure')
    return redirect(url_for('memos.memo_main'))

@memos.route("/search",methods=['GET', 'POST'])
def search():
    form = MemoSearch()
    return render_template('memo_search.html', title='New Memo 123 ',form=form)
