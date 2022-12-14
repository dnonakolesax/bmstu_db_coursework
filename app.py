import json
import os
from flask import Flask, render_template, session, redirect, url_for
from auth.routes import blueprint_auth
from queries.routes import blueprint_query
from report.route import blueprint_report
from orders.routes import blueprint_orders
from access import login_required

app = Flask(__name__)
app.secret_key = 'there is no spoon'

app.register_blueprint(blueprint_auth, url_prefix='/auth')
app.register_blueprint(blueprint_query, url_prefix='/queries')
app.register_blueprint(blueprint_report, url_prefix='/reports')
app.register_blueprint(blueprint_orders, url_prefix='/orders')


app.config['db_config'] = json.load(open('configs/db.json'))
app.config['access_config'] = json.load(open('configs/access.json'))


@app.route('/')
@login_required
def menu_choice():
    if session.get('user_group', None) == 'manager':
        return render_template('manager_menu.html')
    elif session.get('user_group', None) == 'mechanic':
        return render_template('mechanic_menu.html')
    elif session.get('user_group', None) == 'driver':
        return render_template('driver_menu.html')
    elif session.get('user_group', None) == 'accountant':
        return render_template('accountant_menu.html')
    else:
        return render_template('external_user_menu.html')


@app.route('/exit')
@login_required
def exit_func():
    session.clear()
    return redirect(url_for('blueprint_auth.start_auth'))


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5001)
