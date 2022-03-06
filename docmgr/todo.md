
----------------------
Bugs
----------------------


0   enh     make memo versions be a letter
0   enh     make a route for /memo/arh-1a
0   enh     search

1   enh     code review verify of functions
1   enh     add comments

2   enh     active directory

2   enh     your inbox should show all of the memos insignoff that you are delegated to sign
2   bug     Fix backreferences

2   bug     in memo signoff the signers needs to be able to view the memo

2   bug     Memo should be able to have only 1 draft

3   bug     Memo model - write memo json missing stuff
3   enh     User model - write user meta data json
3   bug     memo model - verify that table field lengths make sense

3   enh     admin interface - load a user table from json or excel

4   enh     create memo - require at least 1 attachment
4   enh     create memo - number of file attachment hardcode
4   enh     create memo - if you upload a file in word with right tags it will fix the meta-data
4   enh     create memo - add a link to get a template
4   enh     help - add configuration insturctions for administrator

4   enh     create memo - add the ability to add an email address to the distribution list (what does this do to security?)
4   enh     create memo - when you revise a memo the references are copied automatically



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

