from flask import Blueprint, render_template, request, current_app, session, redirect, url_for
from database.sql_provider import SQLProvider
from database.operations import select, insert, edit
import os
import datetime
from database.connection import DBContextManager
from access import external_required
import geocoder
from mpu import haversine_distance
import orders.address_processing as address_processing

blueprint_orders = Blueprint('bp_orders', __name__, template_folder='templates', static_folder='templates')

provider = SQLProvider(os.path.join(os.path.dirname(__file__), 'sql'))


@external_required
@blueprint_orders.route('/create-order', methods=['GET', 'POST'])
def create_order():
    if request.method == 'GET':
        _sql = provider.get('get_possible_cargos.sql')
        cargos_result, schema = select(current_app.config['db_config'], _sql)
        cargos = []
        for i in cargos_result:
            cargos.append(i[0] + " (" + i[1] + ")")
        from_address = ''
        to_address = ''
        if 'from' in session and 'to' in session:
            from_address = session['from']
            to_address = session['to']
        order_list = session.get('order', {})
        print(order_list)
        return render_template('new_order.html', cargo_types=cargos, order=order_list, fromad=from_address,
                               toad=to_address)
    else:
        amount = int(request.form.get('amount'))
        cargo_type = request.form.get('cargo')
        cargo_type, cargo_mes = cargo_type.split(" (")
        print(cargo_type)
        cargo_mes = cargo_mes[:-1]
        _sql = provider.get('cargo_name_by_id.sql', pc_name=cargo_type)
        cargo_type_id, schema = select(current_app.config['db_config'], _sql)
        add_to_basket(str(cargo_type_id[0][0]), amount, cargo_type, cargo_mes)
        return redirect(url_for('bp_orders.create_order'))


def add_to_basket(ctype_id: str, amount, cargo_type, cargo_mes):
    curr_order = session.get('order', {})
    if ctype_id in curr_order:
        curr_order[ctype_id]['cargo_amount'] = curr_order[ctype_id]['cargo_amount'] + amount
    else:
        curr_order[ctype_id] = {
            'cargo_amount': amount,
            'cargo_name': cargo_type,
            'cargo_mes': cargo_mes
        }
        session['order'] = curr_order
        session.permanent = True
    return True


@external_required
@blueprint_orders.route('confirm-order', methods=['GET', 'POST'])
def confirm_order():
    if request.method == 'GET':
        return render_template('confirm_order.html')
    else:
        if "count" in request.form:
            region1 = request.form.get("region")
            city1 = request.form.get("city")
            street1 = request.form.get("street")
            building1 = request.form.get("building")
            region2 = request.form.get("region2")
            city2 = request.form.get("city2")
            street2 = request.form.get("street2")
            building2 = request.form.get("building2")
            if "district" in request.form:
                district1 = request.form.get("district")
                address1 = region1 + ", " + district1 + ", " +city1 + ", " + street1 + ", " + building1
                bool1 = True
            else:
                address1 = city1 + ", " + street1 + ", " + building1
                bool1 = False
            if "district2" in request.form:
                district2 = request.form.get("district2")
                address2 = region2 + ", " + district2 + ", " + city2 + ", " + street2 + ", " + building2
                bool2 = True
            else:
                address2 = city2 + ", " + street2 + ", " + building2
                bool2 = False
            address1g = address_processing.process_address(address1, bool1)
            address2g = address_processing.process_address(address2, bool2)
            g1 = geocoder.osm(address1g)
            g2 = geocoder.osm(address2g)
            if g1.latlng is None:
                return render_template('confirm_order.html',
                                       message='Введён некорректный адрес отправки')
            if g2.latlng is None:
                return render_template('confirm_order.html',
                                       message='Введён некорректный адрес получения')
            distance = haversine_distance(g1.latlng, g2.latlng)
            session['from'] = address1
            session['to'] = address2
            session['distance'] = distance
            price_mult = 0
            curr_order = session.get('order', {})
            for key in curr_order:
                _sql = provider.get('pcargo_price.sql', pc_id=key)
                cargo_price, schema = select(current_app.config['db_config'], _sql)
                price_mult = price_mult + (curr_order[key]['cargo_amount'] * cargo_price[0][0])
            session['price'] = int(price_mult * distance)
            return render_template('confirm_order.html', region=region1, city=city1, street=street1, building=building1,
                                   region2=region2, city2=city2, street2=street2, building2=building2,
                                   price_km=price_mult, price=int(price_mult * distance), district=district1,
                                   district2=district2)
        elif "order" in request.form:
            return redirect(url_for('bp_orders.save_order'))


@external_required
@blueprint_orders.route('/save-order', methods=['GET', 'POST'])
def save_order():
    _sql = provider.get('get_user_id.sql', user_id=session['user_id'])
    client_id, schema = select(current_app.config['db_config'], _sql)
    curr_order = session.get('order', {})
    print(session['price'])
    _sql = provider.get('insert_order.sql', date=datetime.date.today(), Orderer_id=client_id[0][0],
                        Status="Ожидает обработки", From=session['from'],
                        To=session['to'], Price=session['price'])
    insert(current_app.config['db_config'], _sql)
    order_id = save_order_with_list(current_app.config['db_config'], client_id[0][0], curr_order)
    if order_id:
        session.pop('price')
        session.pop('order')
        session.pop('from')
        session.pop('to')
        return render_template('successfull_order.html', order_id=order_id)
    else:
        return 'fail((('


def save_order_with_list(dbconfig: dict, user_id: int, curr_order: dict):
    with DBContextManager(dbconfig) as cursor:
        if cursor is None:
            raise ValueError('net kursora!!!')
        _sql1 = provider.get('select_order_id.sql', user_id=user_id)
        result1 = cursor.execute(_sql1)
        if result1 == 1:
            _sql2 = provider.get('select_order_id.sql', user_id=user_id)
            cursor.execute(_sql2)
            order_id = cursor.fetchall()[0][0]
            if order_id:
                for key in curr_order:
                    amount = curr_order[key]['cargo_amount']
                    _sql3 = provider.get('insert_order_list.sql', invoice_id=int(order_id), pcargo_id=int(key),
                                         amount=int(amount))
                    cursor.execute(_sql3)
                return order_id


@external_required
@blueprint_orders.route('clear-basket')
def clear_basket():
    if 'order' in session:
        session.pop('order')
    return redirect(url_for('bp_orders.create_order'))
