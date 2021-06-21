#!/usr/bin/env python3

# The email checker script.

import os
import yaml
import logging
import email
import bell_slap
from time import sleep
from imapclient import IMAPClient

# Store where we currently are in the filesystem.
__location__ = os.path.realpath(
    os.path.join(os.getcwd(), os.path.dirname(__file__)))

# Attempt to read in the configuration.
with open(os.path.join(__location__, "config.yml"), 'r') as stream:
    try:
        config = yaml.load(stream, Loader=yaml.FullLoader)
    except yaml.YAMLError as exc:
        print(exc)

# Log into email server.
server = IMAPClient(config['email']['imap_host'])
server.login(config['email']['username'], config['email']['password'])

# See how many messages are in the inbox.
select_info = server.select_folder('INBOX')
logging.info('Messages in INBOX: %d' % select_info[b'EXISTS'])

# See if there are any new messages.
messages = server.search('UNSEEN')
logging.info("Unread messages: %d\n" % len(messages))

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
        bell_slap.slap_the_bell()
        # Sleep for a few seconds between dings.
        sleep(random.randint(1, 5))

server.logout()
