
# What is a Memo?
Memos are internal documents containing information that is part of the organization’s knowledge. These can be:
-	Ideas for how to approach a problem
-	Results of experiments or prototypes
-	Thoughts about areas to explore

The idea is to capture information in a searchable system, instead of transmitting them via email where there is not a common searchable repository.

## State Machine
Each memo can have one or more versions.  A version starts as a draft, moves to signoff when it is submitted, then to active when it is signed off (or has no signatures) and finally becomes obsolete when
1. Another version of the memo becomes active
2. The user, the delegate of the user or the admin marks the memo as obsolete

A memo can be in one of 4 states, Draft, Signoff, Active or Obsolete.  
![State Flow Diagram](/static/profile_pics/StateFlow.png)

# Top Banner
The top banner contains the menu options for the system. The options available will change when you log into or out of the system.
## Home
Lists the most recently released memos.
## Search
Allows searching through memos by *one* of the available fields:
- Title
- Keywords
- Memo (user-number)
- User
- Inbox (user's inbox to search, can be used by delegates.)
## Inbox
List of memos awaiting my review. Sign and Reject buttons are here.
### Available Inbox
The Available inboxes are list of your inbox, plus all the inboxes of users you are a delegate for.
## New Memo
Create a new memo
## Drafts
List of memos I have created, but not yet submitted.
## My Memos
List of memos I have released.
## Login
Screen to log into system
## Register
Screen to register a new account (If LDAP is not enabled)
## Account
Screen to display user settings.
- Username - unique identifier of a user in the system. This cannot be modified.
- Email - used to send notifications and reset password
- Delegates - users that can sign for you
- Subscriptions - users I want to be notified of memos from
- Admin - Indicates access to all features
- Read All - Indicates ability to read all confidential memos
- Page Size - number of memos per page you want to display
- Profile Picture - Upload a .png or .gif to customize your account

only administrators can alter the settings of the Admin and Read All fields.  
In an LDAP environment, Email, Admin and Read All are set from LDAP and cannot be updated.
## Logout
Logs out of system
## Help
This document

# Create New Memo
## Title
## Distribution
A list of **Usernames** seperated by space,comma,semicolon,colon or tab that will receive notification of the memo release via email.
## Keywords
A freeform list of words seperated by space,comma,semicolon,colon or tab.

This is only used by the search function by Keyword.

An example list of keywords "quality, engineering, design".

## Signers
A list of **Usernames** seperated by space,comma,semicolon,colon or tab that must sign the memo, before it is active. 
They will receive notification of the memo release via email.
## References
A list of **Memos** seperated by space,comma,semicolon that are referenced by this memo
## Confidential
If selected, only users on the Distribution and Signers lists can view the attached files.
## Files
Attached files hold the content of the memo. These can be any file format. Common items will be Word and PowerPoint files.
## Submit
Submits the memo for Signoff, if there are Signers listed. Otherwise, makes the memo active
## Save
Saves the changes to the memo and keeps it in the Draft state.
## Cancel
Deletes this Draft memo and all file attachments.

# Administrative Functions
## Inbox
An administrator can pull up anyone's Inbox page by going to the /inbox/<username> url.  
From that page, they can sign for that user.
## Account
An administrator can pull up anyone's Inbox page by going to the /account/<username> url.  
On that page, they can update any field except username. (If LDAP is enabled, Email, Admin and Read All are also locked)
