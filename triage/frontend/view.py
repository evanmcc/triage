
from frontend import app, g, request, session, abort, \
    url_for, render_template, redirect, flash

from flaskext.bcrypt import Bcrypt

bcrypt = Bcrypt(app)

from pymongo import Connection

users = Connection().user_db.users

@app.route('/')
def splash():
    if session.get('logged_in') == True: 
        return redirect(url_for('rdr'))


    return render_template('splash.html')

@app.route('/login', methods = ['POST'] )
def login():
    if session.get('logged_in'):
        return redirect(url_for('rdr'))

    un = request.form.get('username')
    pw = request.form.get('password')

    if not un or not pw:
        abort(401) 

    user = users.find_one({'name':un})
    if not user: 
        abort(401) 
    
        # XXX: need to replace this with a real secret key
    if not bcrypt.check_password_hash(user['password'], pw):
        abort(401)
    
    # else we're clear
    session['logged_in'] = True

    return redirect(url_for('feeds'))

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    flash('You have been logged out.')
    return redirect(url_for('splash'))

@app.route('/rdr')
def feeds():
    if not session.get('logged_in'): 
        return redirect(url_for('splash'))
    
    return render_template('rdr.html')

@app.route('/admin')
def admin():
    return ''

@app.route('/mkuser', methods = [ 'POST' ])
def mkuser():
    un  = request.form.get('username')
    pw  = request.form.get('password')
    pw2 = request.form.get('password2')
    em  = request.form.get('email')
    
    if not un or not pw or not pw2:
        flash('all fields are required')
        return redirect(url_for('splash'))

    if pw != pw2: 
        flash('passwords must match')
        return redirect(url_for('splash'))

    if users.find_one({'name':un}):
        flash('user already exists')
        return redirect(url_for('splash'))

    if users.find_one({'email':em}):
        flash('email isn\'t unique')
        return redirect(url_for('splash'))

    #should check for email validity here.

    #otherwise we're here.
    #usually we're going to ask for more information on a second page,
    # real name, payment, etc. but for now just create the user and forward 
    # to the viewer page.

    users.insert({'name':un, 
                  'password':bcrypt.generate_password_hash(pw), 
                 'friends':None, 'feeds':None})
    session['username'] = un
    session['logged_in'] = True

    return ''


@app.route('/manage')
def manage():
    return ''

@app.route('/settings')
def settings():
    return ''

