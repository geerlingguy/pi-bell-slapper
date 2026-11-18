#!/usr/bin/env python3
"""Ding the bell when an unread email matches the configured conditions."""

import email
import json
import logging
import os
import urllib.request
from time import sleep
from urllib.error import HTTPError

import yaml
from imapclient import IMAPClient

with open(os.path.join(os.path.dirname(os.path.realpath(__file__)), 'config.yml'), encoding='utf-8') as stream:
    config = yaml.safe_load(stream)


def ding():
    url = config['ding']['url']
    if not url.startswith(('http://', 'https://')):
        raise ValueError(f'ding.url must be http(s): {url}')
    body = json.dumps({'count': config['ding']['count'], 'sound': config['ding']['sound']}).encode()
    request = urllib.request.Request(url, data=body, headers={'Content-Type': 'application/json'})
    # Retry while the ding queue is full (HTTP 429).
    for _ in range(120):
        try:
            with urllib.request.urlopen(request, timeout=10):  # nosec B310
                return
        except HTTPError as e:
            if e.code != 429:
                raise
            sleep(1)


server = IMAPClient(config['email']['imap_host'])
server.login(config['email']['username'], config['email']['password'])

select_info = server.select_folder('INBOX')
logging.info('Messages in INBOX: %d', select_info[b'EXISTS'])

# Fetching a message marks it as seen.
messages = server.search('UNSEEN')
logging.info('Unread messages: %d', len(messages))

from_contains = config['conditions']['from_contains']
subject_contains = config['conditions']['subject_contains']

for message_data in server.fetch(messages, ['RFC822']).values():
    message = email.message_from_bytes(message_data[b'RFC822'])
    subject = message.get('Subject', '')
    if from_contains in message.get('From', '') and subject_contains in subject:
        print(f'Found matching email: {subject}')
        ding()

server.logout()
