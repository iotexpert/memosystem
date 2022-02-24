
----------------------
Bugs
----------------------


0   bug     next page and next screen & paginate (Memo.get_memo_list/memo_main,get_inbox/inbox,get_drafts/ )
0   enh     search
0   bug     new memo screen - make the uploaded saved file stay attacted
0   bug     new memo screen - be able to delete files that were attached

1   enh     code review verify of functions
1   enh     add comments

2   enh     active directory

2   enh     your inbox should show all of the memos insignoff that you are delegated to sign
2   bug     Fix backreferences

3   bug     Memo model - write memo json missing stuff
3   enh     User model - write user meta data json
3   bug     memo model - verify that table field lengths make sense

3   enh     admin interface - load a user table from json or excel

4   enh     create memo - number of file attachment hardcode

------------------------------
State Machine description
------------------------------

if a memo has signers it goes into "signoff" state when submitted
if a memo has no signers it goes straight into active

When the state moves to "signoff" email all of the people on the signers list
When the state moves to active email all of the people on the distribution list

------------------------------
Admin Features
------------------------------

update confidentiality
security logging
import memos from a directory structure

------------------------------
Naming Convention
------------------------------

functions  ... lower case with underscores
classes .... UpperCamelCase
variable ... lowercase single word... or with underscores
method .... lowercase with underscores
module ... lowercase.. potentially with underscores
package

memos_main
inbox       get_inbox
drafts      get_drafts
search      
