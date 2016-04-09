from __future__ import print_function
import httplib2
import os

from apiclient import discovery
import oauth2client
from oauth2client import client
from oauth2client import tools

import pprint
from string import digits, ascii_lowercase, ascii_uppercase
import random
import json

try:
    import argparse
    flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()
except ImportError:
    flags = None

# If modifying these scopes, delete your previously saved credentials
# at ~/.credentials/admin-directory_v1-python-quickstart.json
SCOPES = 'https://www.googleapis.com/auth/admin.directory.user'
CLIENT_SECRET_FILE = 'client_secret.json'
APPLICATION_NAME = 'Directory API Python Quickstart'

PASSWORD_ALPHABET = digits + ascii_lowercase + ascii_uppercase

def password_generate(size=13, chars=PASSWORD_ALPHABET):
    return ''.join(random.SystemRandom().choice(chars) for _ in range(size))


def _get_credentials():
    """Gets valid user credentials from storage.

    If nothing has been stored, or if the stored credentials are invalid,
    the OAuth2 flow is completed to obtain the new credentials.

    Returns:
        Credentials, the obtained credential.
    """
    home_dir = os.path.expanduser('~')
    credential_dir = os.path.join(home_dir, '.credentials')
    if not os.path.exists(credential_dir):
        os.makedirs(credential_dir)
    credential_path = os.path.join(credential_dir,
                                   'admin-directory_v1-python-quickstart.json')

    store = oauth2client.file.Storage(credential_path)
    credentials = store.get()
    if not credentials or credentials.invalid:
        flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE, SCOPES)
        flow.user_agent = APPLICATION_NAME
        if flags:
            credentials = tools.run_flow(flow, store, flags)
        else: # Needed only for compatibility with Python 2.6
            credentials = tools.run(flow, store)
        print('Storing credentials to ' + credential_path)
    return credentials

def construct_user_json(first_name, last_name, primary_email,
                        organization="WREK", is_admin=False,
                        password=password_generate(),
                        kind="user", suspended=False,
                        change_pass_at_next_login=True,
                        hash_function="SHA-1"):

    # Make a dict of the ensuing JSON
    json_post = {
                    "Content-Type": "application/json",
                    "name": {
                        "givenName": first_name,
                        "fullName": first_name + " " + last_name,
                        "familyName": last_name
                    },
                    "suspended": suspended,
                    "primaryEmail": primary_email,
                    "emails": primary_email,
                    "isAdmin": is_admin,
                    "hashFunction": hash_function,
                    "password": password,
                    "organizations": organization,
                    "kind": kind,
                    "changePasswordAtNextLogin": change_pass_at_next_login
                }

    return json.dumps(json_post) # Return a JSON object


def main():
    """Shows basic usage of the Google Admin SDK Directory API.

    Creates a Google Admin SDK API service object and outputs a list of first
    10 users in the domain.
    """
    credentials = _get_credentials()
    http = credentials.authorize(httplib2.Http())
    service = discovery.build('admin', 'directory_v1', http=http)

    body = construct_user_json("Test", "User", "gpb@wrek.org")

    print("Passing in:")
    print(json.dumps(json.loads(body)))

    service.users().insert(body=body).execute()

if __name__ == '__main__':
    main()
