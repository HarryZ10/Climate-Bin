'''
User management is a critical component of any website. This file does two differnet things:

1) This file users Googles API to securely authenticate the users to this site. Mostly you just want to leave the code that does this
alone.

2) This file manages how users are described on the site.  This could be given users the ability to change their names from how they
are in Google or changing their default picture or managing other values that are unique to your application like is the user
an administrator etc.

Users are managed by several different files: 
* in app/classes/data.py there is a User data class that defines what data fields are stored for each user
* in app/classes/formd.py there is a UserForm class that defines what fields can be edited for each user
* There is this file which does all the hard work.  the /login and /editprofile routes are were you might
want to make changes for your site 
* in app/templates/profile.html and app/templates/editprofile.html are the templates that are used to 
display and edit information about the users
'''

from app import app
from .scopes import *

from flask import render_template, redirect, url_for, request, session, flash
from app.classes.data import User
from app.classes.forms import UserForm, ProfileForm
from requests_oauth2.services import GoogleClient
from requests_oauth2 import OAuth2BearerToken
from .credentials import *
from urllib.parse import urlparse
from os.path import splitext
import requests
import google.oauth2.credentials
import google_auth_oauthlib.flow
import googleapiclient.discovery
import os
import datetime as dt


# this is a reference to the google project json file you downloaded using the setup.txt instructions

# List of email addresses for Admin users
admins = ['harryzhu45@gmail.com']

# This code is run right after the app starts up and then not again. It defines a few universal things
# like is the app being run on a local computer and what is the local timezone
@app.before_first_request
def before_first_request():

    if request.url_root[8:11] == '127' or request.url_root[8:17] == 'localhost':
        session['devenv'] = True
        session['localtz'] = 'America/Los_Angeles'
        
    else:
        session['devenv'] = False
        session['localtz'] = 'UTC'

# This runs before every route and serves to make sure users are using a secure site and can only
# access pages they are allowed to access
@app.before_request
def before_request():
    
    # this checks if the user requests http and if they did it changes it to https
    # if request.headers.get('X-Forwarded-Proto') == 'http':
    #     url = request.url.replace('http://', 'https://', 1)
    #     print("redirected to https?")
    #     code = 301
    #     return redirect(url, code=code)
    
    # if not request.is_secure:
    #     flash("Redirected to https")
    #     return redirect(request.url.replace('http://', 'https://', 1), 301)
    

    # Create a list of all the paths that do not need authorization or are part of authorizing
    # so that each path this is *not* in this list requires an authorization check.
    # If you have urls that you want your user to be able to see without logging in add them here.
    unauthPaths = ['/','/home','/authorize','/login','/oauth2callback','/static/main.js',
                    '/static/local.css','/static/overlay-bg.jpg','/static/testimonial-2.jpg',
                    '/static/intro-vid.mp4','/static/interactive.mp4','/explore','/live']
                
    # this is some tricky code designed to send the user to the page they requested even if they have to first go through
    # a authorization process.
    session['return_URL'] = '/'
    
    # this sends users back to authorization if the login has timed out or other similar stuff
    if request.path not in unauthPaths:
        if 'credentials' not in session:
            flash('No credentials in your session. Adding them now.')
            return redirect(url_for('authorize'))
        if not google.oauth2.credentials.Credentials(**session['credentials']).valid:
            flash('Your credentials are not valid with Google Oauth. Re-authorizing now.')
            return redirect(url_for('authorize'))
        else:
            # refresh the session credentials
            credentials = google.oauth2.credentials.Credentials(**session['credentials'])
            session['credentials'] = credentials_to_dict(credentials)

# This tells the app what to do if the user requests the home either via '/home' or just'/'
@app.route('/')
@app.route('/home')
def index():
    
    return render_template("index.html", isIndex=True)


# # @app.route('/static/interactive.mp4')
# # @app.route('/static/favicon.ico')
# # @app.route('/static/intro-vid.mp4')
# # @app.route('/static/local.css')
# # @app.route('/static/main.js')
# # @app.route('/static/overlay-bg.jpg')
# @app.route('/static/<filename>')
# def static_files(filename):
#     return redirect('/home')

# a lot of stuff going on here for the user as they log in including creatin new users if this is their first login
@app.route('/login')
def login():

    # Go and get the users credentials from google. The /authorize and /oauth2callback functions should not be edited.
    # That is where the user is sent if their credentials are not currently stored in the session.  More about sessions below. 
    if 'credentials' not in session:
        # send a msg to the user
        flash('From /login - No credentials in your session. Adding them now.')
        # send the user to get authenticated by google
        return redirect(url_for('authorize'))

    # Now that the user has credentials, use those credentials to access Google's people api and get the users information
    credentials = google.oauth2.credentials.Credentials(**session['credentials'])
    
    session['credentials'] = credentials_to_dict(credentials)
    people_service = googleapiclient.discovery.build('people', 'v1', credentials=credentials)
    # set data to be the dictionary that contains all the information about the user that google has.  You can see this 
    # information displayed via the current profile template
    data = people_service.people().get(resourceName='people/me', personFields='names,emailAddresses,photos').execute()


   
    # get the google email address from the data object and check to see if the user has an ousd email account.  
    # Deny access if they do not
    # if not data['emailAddresses'][0]['value'][-8:] == "ousd.org":
    #     flash('You must have an ousd.org email address to access this site')
    #     return redirect(url_for('logout'))
        
    try:
        # see if the user already exists in the user dtabase document. If they don't then this attempt
        # to create a currUser object from the User class in the data.py file will fail 
        currUser = User.objects.get(gid = data['emailAddresses'][0]['metadata']['source']['id'])

        flash(f'Welcome Back! {currUser.fname}')
        # Check the email address in the data object to see if it is in the admins list and update the users
        # database record if needed.
        if data['emailAddresses'][0]['value'] in admins:
            admin = True
            if currUser.admin == False:
                currUser.update(admin=True)
        else:
            admin = False
            if currUser.admin == True:
                currUser.update(admin=False)
    
    except:
        # If the user was not in the database, then set some variables and create them
        # first decide if they are a student or a teacher by checking the front of their email address   
        
        flash('Birthday not found, please edit your birthday manually.')
        
        #See if the new user is in the Admins list
        if data['emailAddresses'][0]['value'] in admins:
            admin = True
            role = 'teacher'
        else:
            role = 'student'
            admin = False

        # Create a newUser object filled with the google values and the values that were just created
        newUser = User(
                        gid=data['emailAddresses'][0]['metadata']['source']['id'], 
                        gfname=data['names'][0]['givenName'],                       
                        fname=data['names'][0]['givenName'],
                        email=data['emailAddresses'][0]['value'],
                        image=data['photos'][0]['url'],
                        role=role,
                        admin=admin
                        )
        # save the newUser
        newUser.save()
        # then use the mongoengine get() method to get the newUser from the database as the currUser
        # gid is a unique attribute in the User class that matches google's id which is in the data object
        currUser = User.objects.get(gid = data['emailAddresses'][0]['metadata']['source']['id'])
        # send the new user a msg
        flash(f'Welcome {currUser.fname}.  A New user has been created for you.')


    try:
        
        year = data['birthdays'][1]['date']['year']
        editUser = User.objects.get(gid=session['gid'])

    except KeyError:
        year = None

        if year:
            month = data['birthdays'][1]['date']['month']
            day = data['birthdays'][1]['date']['day']
            birthday = dt.date(year,month,day)
            
            editUser.update(
                birthday = birthday
            )
            
            flash('User birthday has been imported successfully.')
        else:
            flash('User must enter birthday manually.')
        
    # this code puts several values in the session list variable.  The session variable is a great place
    # to store values that you want to be able to access while a user is logged in. The va;ues in the sesion
    # list can be added, changed, deleted as you would with any python list.
    session['currUserId'] = str(currUser.id)
    session['displayName'] = str(currUser.fname) + " " + str(currUser.lname)
    session['gid'] = data['emailAddresses'][0]['metadata']['source']['id']
    # this stores the entire Google Data object in the session
    session['gdata'] = data
    session['role'] = currUser.role
    session['admin'] = admin

    # The return_URL value is set above in the before_request route. This enables a user you is redirected to login to
    # be able to be returned to the page they originally asked for.
    return redirect(session['return_URL'])


#This is the profile page for the logged in user
@app.route('/profile', methods=['GET', 'POST'])
def profile():
    
    currUser=User.objects.get(gid=session['gid'])
    form = UserForm()
    pform = ProfileForm()
    editUser = User.objects.get(gid=session['gid'])
    
    if pform.validate_on_submit():
        editUser.update(
            skills = pform.skills.data,
            country = pform.country.data,
            biography = pform.biography.data
        )
        
        return redirect(url_for('profile'))

    pform.skills.data = editUser.skills
    pform.biography.data = editUser.biography
    pform.country.data = editUser.country

    if form.validate_on_submit():
        editUser.update(
            fname = form.fname.data,
            lname = form.lname.data,
            pronouns = form.pronouns.data,
            birthday = form.birthday.data,
            gfname = session['gdata']['names'][0]['givenName'],
        )
        
        return redirect(url_for('profile'))

        form.fname.data = editUser.fname
        form.lname.data = editUser.lname
        form.pronouns.data = editUser.pronouns
        form.birthday.data = editUser.birthday
    
    return render_template("profile.html", currUser=currUser, data=session['gdata'], pform=pform, form=form, isIndex=False,isProfile=True)

#######################################################################################
### THE CODE BELOW IS ALL GOOGLE AUTHENTICATION CODE AND PROBABLY SHOULD NOT BE TOUCHED

# Do not edit anything in this route.  This is just for google authentication
@app.route('/authorize')
def authorize():

    # Create flow instance to manage the OAuth 2.0 Authorization Grant Flow steps.
    # flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
    #   CLIENT_SECRETS_FILE, scopes=SCOPES)
    
    flow = google_auth_oauthlib.flow.Flow.from_client_config(
        client_config=GOOGLE_CLIENT_CONFIG,
        scopes=SCOPES)

    # The URI created here must exactly match one of the authorized redirect URIs
    # for the OAuth 2.0 client, which you configured in the API Console. If this
    # value doesn't match an authorized URI, you will get a 'redirect_uri_mismatch'
    # error.
    flow.redirect_uri = url_for('oauth2callback', _external=True)
    authorization_url, state = flow.authorization_url(
        # Enable offline access so that you can refresh an access token without
        # re-prompting the user for permission. Recommended for web server apps.
        access_type='offline',
        # Enable incremental authorization. Recommended as a best practice.
        include_granted_scopes='true')

    # Store the state so the callback can verify the auth server response.
    session['state'] = state
    #session['expires_in'] = expires_in

    return redirect(authorization_url)

# Do not edit anything in this route.  This is just for google authentication
@app.route("/oauth2callback")
def oauth2callback():
    # Specify the state when creating the flow in the callback so that it can
    # verified in the authorization server response.
    state = session['state']

    # flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(CLIENT_SECRETS_FILE, scopes=SCOPES, state=state)
    
    flow = google_auth_oauthlib.flow.Flow.from_client_config(
        client_config=GOOGLE_CLIENT_CONFIG,
        scopes=SCOPES, state=state)
    flow.redirect_uri = url_for('oauth2callback', _external=True)

    # Use the authorization server's response to fetch the OAuth 2.0 tokens.
    authorization_response = request.url

    flow.fetch_token(authorization_response=authorization_response)

    # Store credentials in the session.
    # ACTION ITEM: In a production app, you likely want to save these
    #              credentials in a persistent database instead.
    credentials = flow.credentials
    session['credentials'] = credentials_to_dict(credentials)

    #return flask.redirect(flask.url_for('test_api_request'))
    return redirect(url_for('login'))

# Do not edit anything in this route.  This is just for google authentication
@app.route('/revoke')
def revoke():
    if 'credentials' not in session:
        return redirect(url_for('authorize'))

    if google.oauth2.credentials.Credentials(**session['credentials']).valid:
        credentials = google.oauth2.credentials.Credentials(**session['credentials'])
    else:
        flash('Your current session credentials are not valid. I need to log you back in so that you can access your authorization to revoke it.')
        return redirect('authorize')

    revoke = requests.post('https://accounts.google.com/o/oauth2/revoke',
        params={'token': credentials.token},
        headers = {'content-type': 'application/x-www-form-urlencoded'})

    status_code = getattr(revoke, 'status_code')
    if status_code == 200:
        session['revokereq']=1
        return redirect('/logout')
    else:
        flash('An error occurred.')
        return redirect('/')

@app.errorhandler(404)
def error404(error):
    return render_template('errorpage.html'), 404


# @app.errorhandler(500)
# def error404(error):
#     return render_template('errorpage.html'), 500

@app.route("/logout")
def logout():
    session.clear()
    flash('Session has been cleared and user logged out.')
    return redirect('/')

# Do not edit anything in this route.  This is just for google authentication
def credentials_to_dict(credentials):
    return {'token': credentials.token,
          'refresh_token': credentials.refresh_token,
          'token_uri': credentials.token_uri,
          'client_id': credentials.client_id,
          'client_secret': credentials.client_secret,
          'scopes': credentials.scopes
          }

