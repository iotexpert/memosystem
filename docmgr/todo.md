
----------------------
Bugs
----------------------

0   bug     memo detail page - lists signature
0   bug     Fix backreferences

0   enh     memo page - add cancel button back into the drafts

0   enh     code review verify of functions
0   enh     add comments
0   bug     next page and next screen & paginate

1   enh     your inbox should show all of the memos insignoff that you are delegated to sign

2   enh     cancel route - make cancel completely delete the memo

2   bug     new memo screen - make the uploaded saved file stay attacted
2   bug     new memo screen - be able to delete files that were attached
2   bug     new memo screen - add a save button
2   bug     new memo screen - add a cancel button

2   enh     search

3   bug     memo model - save json missing stuff
3   enh     memo model - write user meta data json
3   bug     memo model - verify that table field lengths make sense

3   enh     admin interface
3   enh     memo model - email updates to memos

3   enh     usermodel - configure page size
3   enh     usermodel - add subscriptions
3   enh     usermodel - configure next memo number

4   enh     create memo - number of file attachment hardcode
4   enh     add license

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

