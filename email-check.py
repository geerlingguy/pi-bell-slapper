#!/usr/bin/env python

# The email checker script.

import yaml
import email
from imapclient import IMAPClient

# Attempt to read in the configuration.
with open("config.yml", 'r') as stream:
    try:
        config = yaml.load(stream, Loader=yaml.FullLoader)
    except yaml.YAMLError as exc:
        print(exc)

# Log into email server.
server = IMAPClient(config['email']['imap_host'])
server.login(config['email']['username'], config['email']['password'])

# See how many messages are in the inbox.
select_info = server.select_folder('INBOX')
print('Messages in INBOX: %d' % select_info[b'EXISTS'])

# See if there are any new messages.
messages = server.search('UNSEEN')
print("Unread messages: %d\n" % len(messages))

from_contains = config['conditions']['from_contains']
subject_contains = config['conditions']['subject_contains']

# Process unread messages. When message is fetched, it's marked as 'seen'.
for msgid, message_data in server.fetch(messages, ['RFC822']).items():
    email_message = email.message_from_bytes(message_data[b'RFC822'])
    email_from = email_message.get('From')
    email_subject = email_message.get('Subject')

    # Check if the email from address and subject match our conditions.
    if from_contains in email_from and subject_contains in email_subject:
        print("Found matching email: %s\n" % email_subject)
        # TODO: Hit that bell!

server.logout()
