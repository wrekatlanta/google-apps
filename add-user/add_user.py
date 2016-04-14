#!/usr/bin/env python3
from __future__ import print_function
from argparse import ArgumentParser
import httplib2
import os
import random
from string import digits, ascii_lowercase, ascii_uppercase

from apiclient import discovery
import oauth2client
from oauth2client import client
from oauth2client import tools

"""add_user.py: add a uset to WREK's Google Apps system."""

# If modifying these scopes, delete your previously saved credentials
# at ~/.credentials/admin-directory_v1-python-quickstart.json
SCOPES = 'https://www.googleapis.com/auth/admin.directory.user'
CLIENT_SECRET_FILE = 'client_secret.json'
APPLICATION_NAME = 'Directory API Python Quickstart'

PASSWORD_ALPHABET = digits + ascii_lowercase + ascii_uppercase


def password_generate(size=8, chars=PASSWORD_ALPHABET):
    """Generates a random password with a given length and alphabet

    Keyword arguments:
    size -- the length of this password
    chars -- the password's alphabet
    Returns a random password of length size.
    """
    return ''.join(random.SystemRandom().choice(chars) for _ in range(size))


def _get_credentials():
    """Gets valid user credentials from storage.

    If nothing has been stored, or if the stored credentials are invalid,
    the OAuth2 flow is completed to obtain the new credentials.

    Returns the obtained credentials
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
        credentials = tools.run_flow(flow, store, flags)
        print('Storing credentials to ' + credential_path)
    return credentials


def construct_user_json(first_name, last_name, primary_email,
                        organization='WREK', is_admin=False,
                        password=password_generate(), kind='user',
                        suspended=False, change_pass_at_next_login=True):

    """Constructs a JSON in the format of a user.

    Use this method in conjunction with add_user to produce the syntactically
    and structurally correct user JSON object.

    Keyword arguments:
    first_name -- the first name of the user
    last_name -- the last name of the user (surname)
    primary_email -- the primary email address of this user (@wrek.org)
    organization -- the user's organization (always WREK)
    is_admin -- boolean; start this user as an admin
    password -- the user's starting password
    kind -- the type of user (i.e. user, admin, super-admin, etc.)
    suspended -- boolean; start this user as suspended
    change_pass_at_next_login -- boolean; force user to make new pass

    Returns a dictionary representing the user JSON
    """

    # Make a dict of the ensuing JSON
    json_post = {
                    'name': {
                        'givenName': first_name,
                        'familyName': last_name
                    },
                    'suspended': suspended,
                    'primaryEmail': primary_email,
                    'emails': primary_email,
                    'isAdmin': is_admin,
                    'password': password,
                    'organizations': organization,
                    'kind': kind,
                    'changePasswordAtNextLogin': change_pass_at_next_login,
                }

    return json_post


def add_user(user_json):
    """Adds a user to the Google Apps system.

    Keyword arguments:
    user_json -- the json that defines the user object, as a dictionary
    Returns the HTTP response from the addition.
    """
    # Get the credentials
    credentials = _get_credentials()
    # Authorize
    http = credentials.authorize(httplib2.Http())

    # Build the service with the admin directory_v1 API
    service = discovery.build('admin', 'directory_v1', http=http)

    # Execute the request
    return service.users().insert(body=user_json).execute()


def main():
    parser = ArgumentParser(description='Adds a user to WREK\'s Google Apps')
    parser.add_argument('name', metavar='name', type=str, nargs='+',
                        help='the user\'s name as \'first last\'')
    parser.add_argument('--email', metavar='email', type=str, nargs='?',
                        default=None,
                        help='the user\'s email address')

    args = parser.parse_args()  # Parse the arguments
    first, last = args.name[0].split(" ")  # Split the full name into its parts
    email = args.email  # Grab the email address
    if not args.email:  # If no email was specified, default to initials
        email = first[0] + last[1] + "@wrek.org"

    user_info = construct_user_json(first, last, email)

    try:
        add_user(user_info)
    except Exception as e:
        print("Error:", e)

if __name__ == '__main__':
    main()
