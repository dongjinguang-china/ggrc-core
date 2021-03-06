# Copyright (C) 2018 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>

"""GDrive module"""

import uuid
import httplib2

import flask
from flask import render_template
from logging import getLogger
from werkzeug.exceptions import Unauthorized

from ggrc import settings
from ggrc.app import app
from ggrc.login import login_required

from oauth2client import client


_GOOGLE_AUTH_URI = "https://accounts.google.com/o/oauth2/auth"
_GOOGLE_TOKEN_URI = "https://accounts.google.com/o/oauth2/token"
_GOOGLE_API_GDRIVE_SCOPE = "https://www.googleapis.com/auth/drive"

# pylint: disable=invalid-name
logger = getLogger(__name__)


def get_http_auth():
  """Get valid user credentials from storage and create an authorized
  http from it.

  If nothing has been stored, or if the stored credentials are invalid,
  the OAuth2 flow is completed to obtain the new credentials.

  Returns:
      http instance authorized with the credentials

  Note: changes for QUICK FIX only (GGRC-4417). Will be refactored in
  the scope of GGRC-4311
  """
  if 'credentials' not in flask.session:
    raise Unauthorized('Unable to get valid credentials')
  try:
    credentials = client.OAuth2Credentials.from_json(
        flask.session['credentials'])
    http_auth = credentials.authorize(httplib2.Http())
    if credentials.access_token_expired:
      credentials.refresh(http_auth)
  except Exception as ex:
    logger.exception(ex.message)
    del flask.session['credentials']
    raise Unauthorized('Unable to get valid credentials.')
  flask.session['credentials'] = credentials.to_json()
  return http_auth


@app.route("/is_gdrive_authorized")
@login_required
def is_gdrive_authorized():
  """FE need quick check if BE has credentials.

  Unfortunately we can not quick check if credentials are valid here.
  """
  if 'credentials' in flask.session:
    return 'OK'
  else:
    raise Unauthorized('')


@app.route("/authorize")
def authorize_app():
  """Redirect to Google API auth page to authorize.

  This handler should be splitted by two according to steps:
  - OAuth step 1
  - OAuth step 2

  Note: will be splitted in the scope of GGRC-4311
  """
  if 'credentials' in flask.session:
    return render_template("gdrive/auth_gdrive.haml")

  flow = client.OAuth2WebServerFlow(
      settings.GAPI_CLIENT_ID,
      settings.GAPI_CLIENT_SECRET,
      scope=_GOOGLE_API_GDRIVE_SCOPE,
      redirect_uri=flask.url_for("authorize_app", _external=True),
      auth_uri=_GOOGLE_AUTH_URI,
      token_uri=_GOOGLE_TOKEN_URI,
  )
  if 'code' not in flask.request.args:
    state = str(uuid.uuid4())
    auth_uri = flow.step1_get_authorize_url(state=state)
    flask.session['state'] = state
    return flask.redirect(auth_uri)

  # Cross Site Request Forgery (XRSF) guard.
  if flask.request.args['state'] != flask.session['state']:
    raise Unauthorized('Wrong state.')

  auth_code = flask.request.args["code"]
  credentials = flow.step2_exchange(auth_code)
  flask.session['credentials'] = credentials.to_json()
  return render_template("gdrive/auth_gdrive.haml")
