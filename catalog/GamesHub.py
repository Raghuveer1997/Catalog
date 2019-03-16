from flask import Flask, render_template, url_for
from flask import request, redirect, flash, make_response, jsonify
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from Data_Setup import Base, GameFranchiseName, GameTitle, GmailUser
from flask import session as login_session
import random
import string
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import json
import requests
import datetime

engine = create_engine('sqlite:///games.db',
                       connect_args={'check_same_thread': False}, echo=True)
Base.metadata.create_all(engine)
DBSession = sessionmaker(bind=engine)
session = DBSession()
app = Flask(__name__)

CLIENT_ID = json.loads(open('client_secrets.json',
                            'r').read())['web']['client_id']
APPLICATION_NAME = "Games Hub"

DBSession = sessionmaker(bind=engine)
session = DBSession()
# Create anti-forgery state token
gfs_cat = session.query(GameFranchiseName).all()

# completed
# login


@app.route('/login')
def showLogin():
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in range(32))
    login_session['state'] = state
    # return "The current session state is %s" % login_session['state']
    gfs_cat = session.query(GameFranchiseName).all()
    gfes = session.query(GameTitle).all()
    return render_template('login.html',
                           STATE=state, gfs_cat=gfs_cat, gfes=gfes)
    # return render_template('myhome.html', STATE=state
    # gfs_cat=gfs_cat,gfes=gfes)


@app.route('/gconnect', methods=['POST'])
def gconnect():
    # Validate state token
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Obtain authorization code
    code = request.data

    try:
        # Upgrade the authorization code into a credentials object
        oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        response = make_response(
            json.dumps('Failed to upgrade the authorization code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Check that the access token is valid.
    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
           % access_token)
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])
    # If there was an error in the access token info, abort.
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is used for the intended user.
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(
            json.dumps("Token's user ID doesn't match given user ID."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is valid for this app.
    if result['issued_to'] != CLIENT_ID:
        response = make_response(
            json.dumps("Token's client ID does not match app's."), 401)
        print ("Token's client ID does not match app's.")
        response.headers['Content-Type'] = 'application/json'
        return response

    stored_access_token = login_session.get('access_token')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_access_token is not None and gplus_id == stored_gplus_id:
        response = make_response(json.dumps('Current user already connected.'),
                                 200)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Store the access token in the session for later use.
    login_session['access_token'] = credentials.access_token
    login_session['gplus_id'] = gplus_id

    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()

    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']

    # see if user exists, if it doesn't make a new one
    user_id = getUserID(login_session['email'])
    if not user_id:
        user_id = createUser(login_session)
    login_session['user_id'] = user_id

    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += ' " style = "width: 300px; height: 300px; border-radius: 150px;'
    '-webkit-border-radius: 150px; -moz-border-radius: 150px;"> '
    flash("you are now logged in as %s" % login_session['username'])
    print ("done!")
    return output


# User Helper Functions
def createUser(login_session):
    User1 = GmailUser(name=login_session['username'], email=login_session[
                   'email'])
    session.add(User1)
    session.commit()
    user = session.query(GmailUser).filter_by(email=login_session['email']
                                              ).one()
    return user.id


def getUserInfo(user_id):
    user = session.query(GmailUser).filter_by(id=user_id).one()
    return user


def getUserID(email):
    try:
        user = session.query(GmailUser).filter_by(email=email).one()
        return user.id
    except Exception as error:
        print(error)
        return None

# DISCONNECT - Revoke a current user's token and reset their login_session

# completed
# Home


@app.route('/')
@app.route('/home')
def home():
    gfs_cat = session.query(GameFranchiseName).all()
    return render_template('myhome.html', gfs_cat=gfs_cat)

# completed
# Game Franchise for admins


@app.route('/GamesHub')
def GamesHub():
    try:
        if login_session['username']:
            name = login_session['username']
            gfs_cat = session.query(GameFranchiseName).all()
            gfs = session.query(GameFranchiseName).all()
            gfes = session.query(GameTitle).all()
            return render_template('myhome.html', gfs_cat=gfs_cat,
                                   gfs=gfs, gfes=gfes, uname=name)
    except:
        return redirect(url_for('showLogin'))

######
# Showing Games based on Game Franchise


@app.route('/GamesHub/<int:gfid>/showGameFranchises')
def showGameFranchises(gfid):
    gfs_cat = session.query(GameFranchiseName).all()
    gfs = session.query(GameFranchiseName).filter_by(id=gfid).one()
    gfes = session.query(GameTitle).filter_by(gamefranchisenameid=gfid).all()
    try:
        if login_session['username']:
            return render_template('showGameFranchises.html', gfs_cat=gfs_cat,
                                   gfs=gfs, gfes=gfes,
                                   uname=login_session['username'])
    except:
        return render_template('showGameFranchises.html',
                               gfs_cat=gfs_cat, gfs=gfs, gfes=gfes)

#####
# Add New Game Franchise


@app.route('/GamesHub/addGameFranchises', methods=['POST', 'GET'])
def addGameFranchises():
    if request.method == 'POST':
        company = GameFranchiseName(name=request.form['name'],
                                    user_id=login_session['user_id'])
        session.add(company)
        session.commit()
        return redirect(url_for('GamesHub'))
    else:
        return render_template('addGameFranchises.html', gfs_cat=gfs_cat)

########
# Edit Game Franchise


@app.route('/GamesHub/<int:gfid>/edit', methods=['POST', 'GET'])
def editGameFranchises(gfid):
    editGameFranchise = session.query(GameFranchiseName).filter_by(id=gfid
                                                                   ).one()
    creator = getUserInfo(editGameFranchise.user_id)
    user = getUserInfo(login_session['user_id'])
    # If logged in user != item owner redirect them
    if creator.id != login_session['user_id']:
        flash("You cannot edit this Game Franchise."
              "This is belongs to %s" % creator.name)
        return redirect(url_for('GamesHub'))
    if request.method == "POST":
        if request.form['name']:
            editGameFranchise.name = request.form['name']
        session.add(editGameFranchise)
        session.commit()
        flash("Game Franchise Edited Successfully")
        return redirect(url_for('GamesHub'))
    else:
        # gfs_cat is global variable we can them in entire application
        return render_template('editGameFranchises.html',
                               gf=editGameFranchise, gfs_cat=gfs_cat)

######
# Delete Game Franchise


@app.route('/GameHub/<int:gfid>/delete', methods=['POST', 'GET'])
def deleteGameFranchises(gfid):
    gf = session.query(GameFranchiseName).filter_by(id=gfid).one()
    creator = getUserInfo(gf.user_id)
    user = getUserInfo(login_session['user_id'])
    # If logged in user != item owner redirect them
    if creator.id != login_session['user_id']:
        flash("You cannot Delete this Game Franchise."
              "This is belongs to %s" % creator.name)
        return redirect(url_for('GamesHub'))
    if request.method == "POST":
        session.delete(gf)
        session.commit()
        flash("Game Franchise Deleted Successfully")
        return redirect(url_for('GamesHub'))
    else:
        return render_template('deleteGameFranchises.html',
                               gf=gf, gfs_cat=gfs_cat)

#
# Add New Game Name Details


@app.route('/GameHub/addGameFranchises/addGameDetails/<string:gfname>/add',
           methods=['GET', 'POST'])
def addGameDetails(gfname):
    gfs = session.query(GameFranchiseName).filter_by(name=gfname).one()
    # See if the logged in user is not the owner of game
    creator = getUserInfo(gfs.user_id)
    user = getUserInfo(login_session['user_id'])
    # If logged in user != item owner redirect them
    if creator.id != login_session['user_id']:
        flash("You can't add new book edition"
              "This is belongs to %s" % creator.name)
        return redirect(url_for('showGameFranchises', gfid=gfs.id))
    if request.method == 'POST':
        gamename = request.form['gamename']
        launchyear = request.form['launchyear']
        rating = request.form['rating']
        price = request.form['price']
        gametype = request.form['gametype']
        gamedetails = GameTitle(gamename=gamename, launchyear=launchyear,
                                rating=rating,
                                price=price,
                                gametype=gametype,
                                date=datetime.datetime.now(),
                                gamefranchisenameid=gfs.id,
                                gmailuser_id=login_session['user_id'])
        session.add(gamedetails)
        session.commit()
        return redirect(url_for('showGameFranchises', gfid=gfs.id))
    else:
        return render_template('addGameDetails.html',
                               gfname=gfs.name, gfs_cat=gfs_cat)

#
# Edit Game details


@app.route('/GamesHub/<int:gfid>/<string:gfename>/edit',
           methods=['GET', 'POST'])
def editGame(gfid, gfename):
    gf = session.query(GameFranchiseName).filter_by(id=gfid).one()
    gamedetails = session.query(GameTitle).filter_by(gamename=gfename).one()
    # See if the logged in user is not the owner of game
    creator = getUserInfo(gf.user_id)
    user = getUserInfo(login_session['user_id'])
    # If logged in user != item owner redirect them
    if creator.id != login_session['user_id']:
        flash("You can't edit this book edition"
              "This is belongs to %s" % creator.name)
        return redirect(url_for('showGameFranchises', gfid=gf.id))
    # POST methods
    if request.method == 'POST':
        gamedetails.gamename = request.form['gamename']
        gamedetails.launchyear = request.form['launchyear']
        gamedetails.rating = request.form['rating']
        gamedetails.price = request.form['price']
        gamedetails.gametype = request.form['gametype']
        gamedetails.date = datetime.datetime.now()
        session.add(gamedetails)
        session.commit()
        flash("Game Edited Successfully")
        return redirect(url_for('showGameFranchises', gfid=gfid))
    else:
        return render_template('editGame.html', gfid=gfid,
                               gamedetails=gamedetails, gfs_cat=gfs_cat)

#####
# Delte Game Edit


@app.route('/GamesHub/<int:gfid>/<string:gfename>/delete',
           methods=['GET', 'POST'])
def deleteGame(gfid, gfename):
    gf = session.query(GameFranchiseName).filter_by(id=gfid).one()
    gamedetails = session.query(GameTitle).filter_by(gamename=gfename).one()
    # See if the logged in user is not the owner of game
    creator = getUserInfo(gf.user_id)
    user = getUserInfo(login_session['user_id'])
    # If logged in user != item owner redirect them
    if creator.id != login_session['user_id']:
        flash("You can't delete this book edition"
              "This is belongs to %s" % creator.name)
        return redirect(url_for('showGameFranchises', gfid=gf.id))
    if request.method == "POST":
        session.delete(gamedetails)
        session.commit()
        flash("Deleted Game Successfully")
        return redirect(url_for('showGameFranchises', gfid=gfid))
    else:
        return render_template('deleteGame.html', gfid=gfid,
                               gamedetails=gamedetails, gfs_cat=gfs_cat)

####
# Logout from current user


@app.route('/logout')
def logout():
    access_token = login_session['access_token']
    print ('In gdisconnect access token is %s', access_token)
    print ('User name is: ')
    print (login_session['username'])
    if access_token is None:
        print ('Access Token is None')
        response = make_response(
            json.dumps('Current user not connected....'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    access_token = login_session['access_token']
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % access_token
    h = httplib2.Http()
    result = \
        h.request(uri=url, method='POST', body=None,
                  headers={'content-type': 'application/x-www-form-urlencoded'}
                  )[0]

    print (result['status'])
    if result['status'] == '200':
        del login_session['access_token']
        del login_session['gplus_id']
        del login_session['username']
        del login_session['email']
        del login_session['picture']
        response = make_response(json.dumps('Successfully'
                                            'disconnected user..'), 200)
        response.headers['Content-Type'] = 'application/json'
        flash("Successful logged out")
        return redirect(url_for('showLogin'))
        # return response
    else:
        response = make_response(
            json.dumps('Failed to revoke token for given user.', 400))
        response.headers['Content-Type'] = 'application/json'
        return response

#####
# Json


@app.route('/GameHub/JSON')
def allGamesJSON():
    gamefranchises = session.query(GameFranchiseName).all()
    category_dict = [c.serialize for c in gamefranchises]
    for c in range(len(category_dict)):
        games = [i.serialize for i in session.query(
                 GameTitle
                 ).filter_by(gamefranchisenameid=category_dict[c]["id"]).all()]
        if games:
            category_dict[c]["game"] = games
    return jsonify(GameFranchiseName=category_dict)

####


@app.route('/GameHub/gameFranchise/JSON')
def categoriesJSON():
    games = session.query(GameFranchiseName).all()
    return jsonify(gameFranchise=[c.serialize for c in games])

####


@app.route('/Gamehub/games/JSON')
def itemsJSON():
    items = session.query(GameTitle).all()
    return jsonify(games=[i.serialize for i in items])

#####


@app.route('/GameHub/<path:game_name>/games/JSON')
def categoryItemsJSON(game_name):
    gameFranchise = session.query(
        GameFranchiseName).filter_by(name=game_name).one()
    games = session.query(GameTitle).filter_by(gamename=gameCategory).all()
    return jsonify(gameEdtion=[i.serialize for i in games])

#####


@app.route('/GameHub/<path:game_name>/<path:edition_name>/JSON')
def ItemJSON(game_name, edition_name):
    gameFranchise = session.query(
        GameFranchiseName).filter_by(name=game_name).one()
    gameEdition = session.query(GameTitle).filter_by(
           gamename=edition_name, gamename1=gameFranchise).one()
    return jsonify(gameEdition=[gameEdition.serialize])

if __name__ == '__main__':
    app.secret_key = "super_secret_key"
    app.debug = True
    app.run(host='127.0.0.1', port=8000)
