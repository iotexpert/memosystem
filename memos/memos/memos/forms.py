from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, FileField,BooleanField,HiddenField
from wtforms.validators import DataRequired,ValidationError
from memos.models.User import User
from memos.models.User import User
from memos.models.Memo import Memo
from memos.models.MemoFile import MemoFile
from memos.models.MemoSignature import MemoSignature
from flask import current_app
class MemoForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    keywords = StringField('Keywords')
    distribution = StringField('Distribution')
    signers = StringField('Signers')
    references = StringField('References')
    confidential = BooleanField('Confidential?')

    username = HiddenField('username')
    memo_number = HiddenField('memo_number')
    memo_version = HiddenField('memo_version')

    memodoc1 = FileField('Memo')
    memodoc2 = FileField('Memo')
    memodoc3 = FileField('Memo')
    memodoc4 = FileField('Memo')
    memodoc5 = FileField('Memo')

    submit = SubmitField('Submit')
    save   = SubmitField('Save',render_kw={'formnovalidate': True})
    cancel = SubmitField('Cancel',render_kw={'formnovalidate': True})

    def validate_distribution(self, distribution):
        users = User.valid_usernames(distribution.data)
        if len(users['invalid_usernames']) > 0:
            raise ValidationError(f'Invalid users {users["invalid_usernames"]}')

    def validate_signers(self, distribution):
        users = User.valid_usernames(distribution.data)
        if users['non_users']:
            raise ValidationError(f'Invalid users {users["invalid_usernames"]} or email addresses specified.')
    
    def validate_references(self,references):
        current_app.logger.info(f"References = {references.data}")
        valid_references = Memo.valid_references(references.data)
        if len(valid_references['invalid']) > 0:
            raise ValidationError(f'Invalid memo references = {valid_references["invalid"]}')
        
        
        
class MemoSearch(FlaskForm):
    title = StringField('Title')
    keywords = StringField('Keywords')
    memo_ref = StringField('Memo')
    username = StringField('User')
    inbox = StringField('Inbox')
    search = SubmitField('Search')
