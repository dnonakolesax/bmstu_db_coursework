from flask import Blueprint, render_template, request, current_app, session
from database.sql_provider import SQLProvider
from database.operations import select, insert, edit
import os
import datetime

from access import group_required, external_required

blueprint_query = Blueprint('bp_query', __name__, template_folder='templates', static_folder='templates')

provider = SQLProvider(os.path.join(os.path.dirname(__file__), 'sql'))


@blueprint_query.route('/queries', methods=['GET', 'POST'])
@external_required
def queries():
    if request.method == 'GET':
        render_template('all_orders.html')
        _sql = provider.get('orders_history.sql', user_id=session['user_id'], notdone='Не назначен')
        product_result, schema = select(current_app.config['db_config'], _sql)
        possible_status = ['Ожидает обработки', 'Отклонён', 'Принят', 'В пути', 'Доставлен']
        selected_status = ['Все']
        schema = (
            "Номер заказа", "Дата заказа", "Водитель", "Наименование организации", "Статус", "Начальный адрес",
            "Конечный адрес", "Цена (₽)", "Грузы")
        return render_template('all_orders.html', schema=schema, result=product_result, cur_date=datetime.date.today(),
                               choose_status=possible_status, sel_stat=selected_status[0])
    else:
        if 'ord_but' in request.form:
            order_id = request.form.get('ord_id')
            print(order_id)
            _sql = provider.get('order_info.sql', invoice_id=order_id)
            order_result, order_schema = select(current_app.config['db_config'], _sql)
            order_schema = (
                "Номер заказа", "Дата заказа", "Водитель", "Наименование организации", "Статус", "Начальный адрес",
                "Конечный адрес")
            _sql = provider.get('get_order_items.sql', invoice_id=order_id)
            cargo_result, cargo_schema = select(current_app.config['db_config'], _sql)
            cargo_schema = ("Наименование груза", "Вес груза", "Количество товара")
            return render_template('order_details.html', schema1=order_schema, schema2=cargo_schema,
                                   result1=order_result, result2=cargo_result)
        else:
            begin_date = request.form.get('date_from')
            end_date = request.form.get('date_to')
            status = request.form.get('status')
            from_address = request.form.get('from')
            to_address = request.form.get('to')
            possible_status = ['Ожидает обработки', 'Отклонён', 'Принят', 'В пути', 'Доставлен', 'Все']
            possible_status.remove(status)
            selected_status = status
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
                                    end_date=end_date, From=from_address, To=to_address, notdone='Не назначен')
            else:
                _sql = provider.get('orders_with_dtype.sql', client_id=session['user_id'], begin_date=begin_date,
                                    end_date=end_date, status=status, From=from_address, To=to_address, notdone='Не назначен')
            product_result, schema = select(current_app.config['db_config'], _sql)
            schema = (
                "Номер заказа", "Дата заказа", "Водитель", "Наименование организации", "Статус", "Начальный адрес",
                "Конечный адрес", "Цена (₽)", "Грузы")
            return render_template('all_orders.html', schema=schema, result=product_result,
                                   cur_date=datetime.date.today(), from_val=begin_date, to_val=end_date,
                                   choose_status=possible_status, sel_stat=selected_status, From_ad=from_address,
                                   To_ad=to_address)


@blueprint_query.route('/orders', methods=['GET', 'POST'])
@group_required
def order_history():
    if request.method == 'GET':
        _sql = provider.get('all_orders.sql', notdone='Не назначен')
        product_result, schema = select(current_app.config['db_config'], _sql)
        possible_status = ['Ожидает обработки', 'Отклонён', 'Принят', 'В пути', 'Доставлен']
        selected_status = ['Все']
        schema = (
            "Номер заказа", "Дата", "Водитель", "Организация", "Статус", "Начальный пункт", "Конечный пункт",
            "Цена (₽)", "Грузы")
        return render_template('all_orders.html', schema=schema, result=product_result, cur_date=datetime.date.today(),
                               choose_status=possible_status, sel_stat=selected_status[0])
    else:
        if 'ord_but' in request.form:
            order_id = request.form.get('ord_id')
            print(order_id)
            _sql = provider.get('order_info.sql', invoice_id=order_id)
            order_result, order_schema = select(current_app.config['db_config'], _sql)
            order_schema = (
                "Номер заказа", "Дата заказа", "Водитель", "Наименование организации", "Статус", "Начальный адрес",
                "Конечный адрес", "Цена (₽)")
            _sql = provider.get('get_order_items.sql', invoice_id=order_id)
            cargo_result, cargo_schema = select(current_app.config['db_config'], _sql)
            cargo_schema = ("Наименование груза", "Вес груза", "Количество товара")
            return render_template('order_details.html', schema1=order_schema, schema2=cargo_schema,
                                   result1=order_result, result2=cargo_result, manager=True)
        else:
            begin_date = request.form.get('date_from')
            end_date = request.form.get('date_to')
            status = request.form.get('status')
            from_address = request.form.get('from')
            to_address = request.form.get('to')
            possible_status = ['Ожидает обработки', 'Отклонён', 'Принят', 'В пути', 'Доставлен', 'Все']
            possible_status.remove(status)
            selected_status = status
            if not begin_date:
                begin_date = datetime.date(2010, 1, 1)
            if not end_date:
                end_date = datetime.date.today()
            if not from_address:
                from_address = ''
            if not to_address:
                to_address = ''
            if status == 'Все':
                _sql = provider.get('all_orders_date.sql', begin_date=begin_date,
                                    end_date=end_date, From=from_address, To=to_address, notdone='Не назначен')
            else:
                _sql = provider.get('all_orders_dtype.sql', begin_date=begin_date,
                                    end_date=end_date, status=status, From=from_address, To=to_address,
                                    notdone='Не назначен')
            product_result, schema = select(current_app.config['db_config'], _sql)
            schema = (
                "Номер заказа", "Дата", "Водитель", "Организация", "Статус", "Начальный пункт", "Конечный пункт",
                "Цена (₽)", "Грузы")
            return render_template('all_orders.html', schema=schema, result=product_result,
                                   cur_date=datetime.date.today(), from_val=begin_date, to_val=end_date,
                                   choose_status=possible_status, sel_stat=selected_status, From_ad=from_address,
                                   To_ad=to_address)


@blueprint_query.route('/autopark', methods=['GET', 'POST'])
@group_required
def autopark():
    if request.method == 'GET':
        _sql = provider.get('autopark.sql', client_id=session['user_id'])
        result, schema = select(current_app.config['db_config'], _sql)
        schema = ("Id транспорта", "Грузоподъёмность", "Год выпуска", "Марка и модель", "Регистрационный знак")
        return render_template('autopark.html', schema=schema, result=result, date_from=1970, date_to=2022)
    else:
        begin_date = request.form.get('date_from')
        end_date = request.form.get('date_to')
        plate = request.form.get('plate')
        carmod = request.form.get('carmod')
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
        schema = ("Id транспорта", "Грузоподъёмность", "Год выпуска", "Марка и модель", "Регистрационный знак")
        return render_template('autopark.html', schema=schema, result=product_result, date_from=begin_date,
                               date_to=end_date,
                               car_mod=carmod, plate=plate)


@blueprint_query.route('/workers', methods=['GET', 'POST'])
@group_required
def workers():
    if request.method == 'GET':
        render_template('workers.html')
        _sql = provider.get('workers.sql', client_id=session['user_id'])
        result, schema = select(current_app.config['db_config'], _sql)
        schema = ("Id работника", "ФИО", "Домашний адрес", "Дата рождения", "Дата начала работы", "Должность")
        return render_template('workers.html', schema=schema, result=result, date_from=1970, date_to=2022)
    else:
        name = request.form.get('work_name')
        post = request.form.get('work_post')
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
        schema = ("Id работника", "ФИО", "Домашний адрес", "Дата рождения", "Дата начала работы", "Должность")
        return render_template('workers.html', schema=schema, result=product_result, work_name=ntf,
                               work_post=ptf)


@blueprint_query.route('/new-orders', methods=['GET', 'POST'])
@group_required
def all_d_orders():
    if request.method == 'GET':
        _sql = provider.get('get_personal_id.sql', user_id=session['user_id'])
        result, schema = select(current_app.config['db_config'], _sql)
        p_id = result[0][0]
        _sql = provider.get('status_and_worker.sql', p_id=p_id)
        result, schema = select(current_app.config['db_config'], _sql)
        return render_template('curr_orders.html', schema=schema, result=result)
