from app import app
from .users import *
from .scopes import *

from flask import render_template, redirect, url_for, request, session, flash
from app.classes.data import User
from app.routes.users import credentials_to_dict, CLIENT_SECRETS_FILE
from app.classes.forms import UserForm, ProfileForm
from requests_oauth2.services import GoogleClient
from requests_oauth2 import OAuth2BearerToken
from urllib.parse import urlparse
from os.path import splitext
import requests
import google.oauth2.credentials
import google_auth_oauthlib.flow
import googleapiclient.discovery
import os
import json


@app.route("/live")
def live():
    return render_template("livestream.html", isLive=True)

@app.route("/getyoutube")
def get_youtube():
    if 'credentials' not in session:
        # send a msg to the user
        flash('From /login - No credentials in your session. Adding them now.')
        # send the user to get authenticated by google
        return redirect(url_for('authorize'))
    
    # Now that the user has credentials, use those credentials to access Google's people api and get the users information
    credentials = google.oauth2.credentials.Credentials(**session['credentials'])
    session['credentials'] = credentials_to_dict(credentials)
    
    youtube_service = googleapiclient.discovery.build('youtube', 'v3', credentials=credentials)

    ytdata = youtube_service.channels().list(part="snippet,brandingSettings,id", mine=True).execute()

    with open('ytdata.txt', 'w') as json_file:
        json.dump(ytdata, json_file, indent = 4, sort_keys=True)
        
    currUser=User.objects.get(gid=session['gid'])
    
    try:
        channelid = ytdata['items'][0]['id']
        editUser = User.objects.get(gid=session['gid'])
    except KeyError:
        channelid = None

        if channelid:
            editUser.update(
                channelID = ytdata['items'][0]['id'],
                channeltitle = ytdata['items'][0]['brandingSettings']['channel']['title'],
                channelProfileColor = ytdata['items'][0]['brandingSettings']['channel']['profileColor'],
                channelURL = "https://youtube.com/channel/" + ytdata['items'][0]['id']
            )
            
            flash('Youtube has been imported successfully.')
        else:
            flash('Youtube data not found.')
        
    return redirect('profile')