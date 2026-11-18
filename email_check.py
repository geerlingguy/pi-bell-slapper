#!/usr/bin/env python3
"""Ring the bell when a matching email arrives, using IMAP IDLE."""

import argparse
import email
import email.policy
import json
import logging
import os
import time
import urllib.request
from urllib.error import HTTPError

import yaml
from imapclient import IMAPClient, SEEN
from imapclient.exceptions import IMAPClientError

IDLE_SECONDS = 300  # Re-issue IDLE well before servers or NAT routers drop the connection.
RETRY_SECONDS = 30
DEFAULTS = {
    'email': {'port': 993, 'folder': 'INBOX'},
    'match': {'from': '', 'subject': ''},
    'ding': {'url': 'http://localhost/api/ding', 'count': 1, 'sound': True},
}

log = logging.getLogger('email_check')


def load_config(path):
    with open(path, encoding='utf-8') as stream:
        raw = yaml.safe_load(stream) or {}
    config = {section: {**defaults, **(raw.get(section) or {})} for section, defaults in DEFAULTS.items()}
    for key in ('host', 'username', 'password'):
        if not config['email'].get(key):
            raise SystemExit(f'{path}: email.{key} is required.')
    if not str(config['ding']['url']).startswith(('http://', 'https://')):
        raise SystemExit(f'{path}: ding.url must start with http:// or https://.')
    return config


def matches(message, match):
    """True if every non-empty match value is in the header (case-insensitive)."""
    return all(str(value).lower() in str(message.get(header, '')).lower()
               for header, value in match.items() if value)


def ding(settings):
    body = json.dumps({'count': settings['count'], 'sound': settings['sound']}).encode()
    request = urllib.request.Request(settings['url'], data=body, headers={'Content-Type': 'application/json'})
    # Retry while the ding queue is full (HTTP 429).
    for _ in range(120):
        try:
            with urllib.request.urlopen(request, timeout=10):  # nosec B310
                return
        except HTTPError as e:
            if e.code != 429:
                raise
            time.sleep(1)


def check(client, config, dry_run=False):
    """Ding for each unread matching email, then mark it read. Returns the number matched."""
    ids = client.search(['UNSEEN'])
    if not ids:
        return 0
    found = 0
    for msgid, data in client.fetch(ids, ['BODY.PEEK[HEADER.FIELDS (FROM SUBJECT)]']).items():
        headers = next(value for key, value in data.items() if key.startswith(b'BODY'))
        message = email.message_from_bytes(headers, policy=email.policy.default)
        if not matches(message, config['match']):
            continue
        found += 1
        log.info('Match: %s (from %s)', message.get('Subject', ''), message.get('From', ''))
        if not dry_run:
            ding(config['ding'])
            client.add_flags([msgid], [SEEN])
    return found


def connect(config):
    settings = config['email']
    client = IMAPClient(settings['host'], port=settings['port'], timeout=60)
    client.login(settings['username'], settings['password'])
    client.select_folder(settings['folder'])
    return client


def run(config):
    while True:
        try:
            with connect(config) as client:
                log.info('Watching %s on %s.', config['email']['folder'], config['email']['host'])
                while True:
                    check(client, config)
                    client.idle()
                    client.idle_check(timeout=IDLE_SECONDS)
                    client.idle_done()
        except (IMAPClientError, OSError) as e:
            log.warning('%s; reconnecting in %d seconds.', e, RETRY_SECONDS)
            time.sleep(RETRY_SECONDS)


def main():
    default_config = os.path.join(os.environ.get('CREDENTIALS_DIRECTORY', '.'), 'email.yml')
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('config', nargs='?', default=default_config, help='Config file (default: %(default)s)')
    parser.add_argument('--test', action='store_true',
                        help='Log in and list matching unread emails, without dinging or marking them read')
    args = parser.parse_args()
    logging.basicConfig(level=logging.INFO, format='%(message)s')
    config = load_config(args.config)
    if args.test:
        with connect(config) as client:
            print(f'Logged in. {check(client, config, dry_run=True)} matching unread email(s).')
    else:
        run(config)


if __name__ == '__main__':
    main()
