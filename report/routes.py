from flask import Blueprint, render_template, request, current_app, session
from database.sql_provider import SQLProvider
from database.operations import select, insert, edit
import os
import datetime

from access import group_required, external_required

blueprint_query = Blueprint('bp_query', __name__, template_folder='templates')

provider = SQLProvider(os.path.join(os.path.dirname(__file__), 'sql'))


@blueprint_query.route('/queries', methods=['GET', 'POST'])
@external_required
def queries():
    if request.method == 'GET':
        render_template('product_form.html')
        _sql = provider.get('orders_history.sql', client_id=session['user_id'])
        product_result, schema = select(current_app.config['db_config'], _sql)
        possible_status = ['Ожидает обработки', 'Отклонён', 'Принят', 'В пути', 'Доставлен']
        selected_status = ['Все']
        return render_template('db_result.html', schema=schema, result=product_result, cur_date=datetime.date.today(),
                               choose_status=possible_status, sel_stat=selected_status[0])
    else:
        begin_date = request.form.get('date_from')
        end_date = request.form.get('date_to')
        status = request.form.get('status')
        from_address = request.form.get('from')
        to_address = request.form.get('to')
        possible_status = ['Ожидает обработки', 'Отклонён', 'Принят', 'В пути', 'Доставлен', 'Все']
        possible_status.remove(status)
        selected_status = status
        if begin_date or end_date or status:
            if not begin_date:
                begin_date = datetime.date.min
            if not end_date:
                end_date = datetime.date.today()
            if not from_address:
                from_address = ''
            if not to_address:
                to_address = ''
            if status == 'Все':
                _sql = provider.get('orders_with_date.sql', client_id=session['user_id'], begin_date=begin_date,
                                    end_date=end_date, From=from_address, To=to_address)
            else:
                _sql = provider.get('orders_with_dtype.sql', client_id=session['user_id'], begin_date=begin_date,
                                    end_date=end_date, status=status, From=from_address, To=to_address)
            product_result, schema = select(current_app.config['db_config'], _sql)
            return render_template('db_result.html', schema=schema, result=product_result,
                                   cur_date=datetime.date.today(), from_val=begin_date, to_val=end_date,
                                   choose_status=possible_status, sel_stat=selected_status, From_ad=from_address,
                                   To_ad=to_address)
        else:
            return "Repeat input"


@blueprint_query.route('/create_order', methods=['GET', 'POST'])
@external_required
def create_order():
    if request.method == 'GET':
        _sql = provider.get('get_possible_cargos.sql')
        cargos_result, schema = select(current_app.config['db_config'], _sql)
        cargos = []
        for i in cargos_result:
            cargos.append(i[0])
        return render_template('create_form.html', cargo_types=cargos)
    else:
        weight = request.form.get('weight')
        amount = request.form.get('amount')
        cargo_type = request.form.get('cargo')
        from_address = request.form.get('from')
        to_address = request.form.get('to')
        _sql = provider.get('get_user_id.sql', user_id=session['user_id'])
        client_id, schema = select(current_app.config['db_config'], _sql)
        _sql = provider.get('cargo_name_by_id.sql', pc_name=cargo_type)
        cargo_type_id, schema = select(current_app.config['db_config'], _sql)
        _sql = provider.get('create_cargo.sql', weight=weight, amount=amount, PC_id=cargo_type_id[0][0])
        cc_id = insert(current_app.config['db_config'], _sql)
        _sql = provider.get('create_order.sql', date=datetime.date.today(), weight=weight, amount=amount,
                            Cargo_id=cc_id, Orderer_id=client_id[0][0], Status="Ожидает обработки", From=from_address,
                            To=to_address)
        order_id = insert(current_app.config['db_config'], _sql)
        return render_template('successfull_order.html', order_id=order_id)


@blueprint_query.route('/select_driver', methods=['GET', 'POST'])
@group_required
def select_driver():
    if request.method == 'GET':
        _sql = provider.get('unprocessed_orders.sql', Status="Ожидает обработки")
        unprocessed_orders, schema = select(current_app.config['db_config'], _sql)
        _sql = provider.get('drivers.sql', Post='Водитель')
        drv, schem = select(current_app.config['db_config'], _sql)
        drivers = []
        for i in drv:
            drivers.append(i[0])
        return render_template('unprocessed_orders.html', result=unprocessed_orders, schema=schema, drivers=drivers)
    else:
        for key, val in request.form.items():
            print(key, val)
            pos = key.find('.')
            inv_id = key[pos + 1:]
            _sql = provider.get('driver_id.sql', drv_name=val)
            drv, schem = select(current_app.config['db_config'], _sql)
            drv = drv[0][0]
            print(drv, inv_id)
            _sql = provider.get('add_driver_invoice.sql', p_id=drv, Status='Принят', inv_id=inv_id)
            edit(current_app.config['db_config'], _sql)
        return render_template('orders_done.html')


@blueprint_query.route('/orders', methods=['GET', 'POST'])
@group_required
def order_history():
    if request.method == 'GET':
        render_template('all_orders.html')
        _sql = provider.get('all_orders.sql', client_id=session['user_id'])
        product_result, schema = select(current_app.config['db_config'], _sql)
        possible_status = ['Ожидает обработки', 'Отклонён', 'Принят', 'В пути', 'Доставлен']
        selected_status = ['Все']
        return render_template('db_result.html', schema=schema, result=product_result, cur_date=datetime.date.today(),
                               choose_status=possible_status, sel_stat=selected_status[0])
    else:
        begin_date = request.form.get('date_from')
        end_date = request.form.get('date_to')
        status = request.form.get('status')
        from_address = request.form.get('from')
        to_address = request.form.get('to')
        possible_status = ['Ожидает обработки', 'Отклонён', 'Принят', 'В пути', 'Доставлен', 'Все']
        possible_status.remove(status)
        selected_status = status
        if begin_date or end_date or status:
            if not begin_date:
                begin_date = datetime.date.min
            if not end_date:
                end_date = datetime.date.today()
            if not from_address:
                from_address = ''
            if not to_address:
                to_address = ''
            if status == 'Все':
                _sql = provider.get('all_orders_date.sql', begin_date=begin_date,
                                    end_date=end_date, From=from_address, To=to_address)
            else:
                _sql = provider.get('all_orders_dtype.sql', begin_date=begin_date,
                                    end_date=end_date, status=status, From=from_address, To=to_address)
            product_result, schema = select(current_app.config['db_config'], _sql)
            return render_template('db_result.html', schema=schema, result=product_result,
                                   cur_date=datetime.date.today(), from_val=begin_date, to_val=end_date,
                                   choose_status=possible_status, sel_stat=selected_status, From_ad=from_address,
                                   To_ad=to_address)
        else:
            return "Repeat input"


@blueprint_query.route('/autopark', methods=['GET', 'POST'])
@group_required
def autopark():
    if request.method == 'GET':
        render_template('autopark.html')
        _sql = provider.get('autopark.sql', client_id=session['user_id'])
        result, schema = select(current_app.config['db_config'], _sql)
        return render_template('autopark_result.html', schema=schema, result=result, date_from=1970, date_to=2022)
    else:
        begin_date = request.form.get('date_from')
        end_date = request.form.get('date_to')
        plate = request.form.get('plate')
        carmod = request.form.get('carmod')
        if begin_date or end_date or plate or carmod:
            if not begin_date:
                begin_date = 1970
            if not end_date:
                end_date = 2022
            if not plate:
                pltf = ''
            else:
                pltf = plate
            if not carmod:
                crmdtf = ''
            else:
                crmdtf = carmod
            _sql = provider.get('find_car.sql', client_id=session['user_id'], begin_date=begin_date,
                                end_date=end_date, carmodel=crmdtf, plate=pltf)
            product_result, schema = select(current_app.config['db_config'], _sql)
            return render_template('autopark_result.html', schema=schema, result=product_result, from_val=begin_date,
                                   to_val=end_date,
                                   car_mod=carmod, plate=plate)
        else:
            return "Repeat input"


@blueprint_query.route('/workers', methods=['GET', 'POST'])
@group_required
def workers():
    if request.method == 'GET':
        render_template('workers.html')
        _sql = provider.get('workers.sql', client_id=session['user_id'])
        result, schema = select(current_app.config['db_config'], _sql)
        return render_template('worker_result.html', schema=schema, result=result, date_from=1970, date_to=2022)
    else:
        name = request.form.get('work_name')
        post = request.form.get('work_post')
        if name or post:
            if not name:
                ntf = ''
            else:
                ntf = name
            if not post:
                ptf = ''
            else:
                ptf = post
            _sql = provider.get('find_worker.sql', work_name=ntf, work_post=ptf)
            product_result, schema = select(current_app.config['db_config'], _sql)
            return render_template('worker_result.html', schema=schema, result=product_result, work_name=ntf,
                                   work_post=ptf)
        else:
            return "Repeat input"


@blueprint_query.route('/otchet', methods=['GET', 'POST'])
@group_required
def otchet():
    _sql = provider.get('otchet.sql', client_id=session['user_id'])
    result, schema = select(current_app.config['db_config'], _sql)
    return render_template('otchet.html', schema=schema, result=result)


@blueprint_query.route('/new_orders', methods=['GET', 'POST'])
@group_required
def new_d_orders():
    if request.method == 'GET':
        _sql = provider.get('get_personal_id.sql', user_id=session['user_id'])
        result, schema = select(current_app.config['db_config'], _sql)
        p_id = result[0][0]
        _sql = provider.get('status_and_worker.sql', p_id=p_id, Status='Принят')
        result, schema = select(current_app.config['db_config'], _sql)
        return render_template('new_orders.html', schema=schema, result=result)
    else:
        for key, val in request.form.items():
            print(key, val)
            pos = key.find('.')
            inv_id = key[pos + 1:]
            _sql = provider.get('update_invoice_condition.sql', Status='В пути', inv_id=inv_id)
            edit(current_app.config['db_config'], _sql)
    return render_template('orders_accepted.html')


@blueprint_query.route('/curr_orders', methods=['GET', 'POST'])
@group_required
def curr_d_orders():
    if request.method == 'GET':
        _sql = provider.get('get_personal_id.sql', user_id=session['user_id'])
        result, schema = select(current_app.config['db_config'], _sql)
        p_id = result[0][0]
        _sql = provider.get('status_and_worker.sql', p_id=p_id, Status='В пути')
        result, schema = select(current_app.config['db_config'], _sql)
        return render_template('curr_orders.html', schema=schema, result=result)
    else:
        for key, val in request.form.items():
            print(key, val)
            pos = key.find('.')
            inv_id = key[pos + 1:]
            _sql = provider.get('update_invoice_condition.sql', Status='Доставлен', inv_id=inv_id)
            edit(current_app.config['db_config'], _sql)
    return render_template('orders_delivered.html')


@blueprint_query.route('personal/profile', methods=['GET', 'POST'])
@group_required
def show_int_profile():
    _sql = provider.get('get_personal_id.sql', user_id=session['user_id'])
    result, schema = select(current_app.config['db_config'], _sql)
    p_id = result[0][0]
    _sql = provider.get('get_personal_profile.sql', p_id=p_id)
    result, schema = select(current_app.config['db_config'], _sql)
    return render_template('int_profile.html', schema=schema, result=result)


@blueprint_query.route('clients/profile', methods=['GET', 'POST'])
@external_required
def show_ext_profile():
    _sql = provider.get('get_user_id.sql', user_id=session['user_id'])
    result, schema = select(current_app.config['db_config'], _sql)
    c_id = result[0][0]
    _sql = provider.get('get_client_profile.sql', c_id=c_id)
    result, schema = select(current_app.config['db_config'], _sql)
    return render_template('client_profile.html', schema=schema, result=result)
