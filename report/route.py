import os
from flask import Blueprint, request, render_template, current_app, redirect, url_for, session
from access import group_required
from database.operations import select, call_proc
from database.sql_provider import SQLProvider
import json
import calendar
import locale
from datetime import date
blueprint_report = Blueprint('bp_report', __name__, template_folder='templates', static_folder='templates')

provider = SQLProvider(os.path.join(os.path.dirname(__file__), 'sql'))

report_url = json.load(open('configs/report_url.json'))

with open('configs/report_list.json', 'r', encoding='utf_8') as f:
    report_list = json.load(f)


@blueprint_report.route('/report-menu', methods=['GET', 'POST'])
@group_required
def start_report():
    if request.method == 'GET':
        user_group = session['user_group']
        allow_create = True if user_group == 'accountant' else False
        return render_template('menu_report.html', report_list=report_list, allow_create=allow_create)
    else:
        rep_id = str(request.form.get('rep_id'))
        if request.form.get('create_rep'):
            url_rep = report_url[rep_id]["create_rep"]
        else:
            url_rep = report_url[rep_id]["view_rep"]
        print('url_rep=', url_rep)
        return redirect(url_for(url_rep))


@blueprint_report.route('/create-client-report', methods=['GET', 'POST'])
@group_required
def create_rep1():
    if request.method == 'GET':
        curr_date = date.today().strftime("%Y-%m")
        return render_template('report_form.html', curr_date=curr_date)
    else:
        rep_month = request.form.get('month')
        rep_year, rep_month = rep_month.split('-')
        print(rep_month)
        print(rep_year)
        if rep_month and rep_year:
            _sql = provider.get('if_exists_client.sql', rep_month=rep_month, rep_year=rep_year)
            product_result, schema = select(current_app.config['db_config'], _sql)
            if product_result:
                return render_template('report_form.html', message='Ошибка: такой отчёт уже существует!')
            call_proc(current_app.config['db_config'], 'weights_by_client_report', rep_month, rep_year)
            _sql = provider.get('report_client.sql', rep_month=rep_month, rep_year=rep_year)
            product_result, schema = select(current_app.config['db_config'], _sql)
            if not product_result:
                return render_template('report_form.html', message='Ошибка: попытка сделать пустой отчёт!')
            return render_template('report_form.html', message='Отчёт успешно создан!')
        else:
            return "Repeat input"


@blueprint_report.route('/view-client-report', methods=['GET', 'POST'])
@group_required
def view_rep1():
    if request.method == 'GET':
        _sql = provider.get('available_client.sql')
        product_result, schema = select(current_app.config['db_config'], _sql)
        locale.setlocale(locale.LC_ALL, 'ru_RU')
        rep_dates = []
        for product in product_result:
            rep_dates.append(calendar.month_name[product[0]] + " " + str(product[1]))
        print(rep_dates)
        return render_template('get_report.html', report_list=rep_dates)
    else:
        rep_name = report_list[0]['rep_name']
        rep_month = request.form.get('rep_date')
        rep_date = rep_month
        rep_month = request.form.get('rep_date')
        rep_month, rep_year = rep_month.split(' ')
        locale.setlocale(locale.LC_ALL, 'ru_RU')
        for index in range(1, 13):
            if calendar.month_name[index] == rep_month:
                rep_month = index
                break
        if rep_month and rep_year:
            _sql = provider.get('report_client.sql', rep_month=rep_month, rep_year=rep_year)
            product_result, schema = select(current_app.config['db_config'], _sql)
            schema = ("Наименование организации", "Сумма заказов (₽)", "Сделано заказов", "Месяц", "Год")
            return render_template('rep.html', schema=schema, result=product_result, rep_date=rep_date, rep_name=rep_name)
        else:
            return "Repeat input"


@blueprint_report.route('/create-driver-report', methods=['GET', 'POST'])
@group_required
def create_rep2():
    if request.method == 'GET':
        curr_date = date.today().strftime("%Y-%m")
        return render_template('report_form.html', curr_date=curr_date)
    else:
        rep_month = request.form.get('month')
        rep_year, rep_month = rep_month.split('-')
        print(rep_month)
        print(rep_year)
        if rep_month and rep_year:
            _sql = provider.get('if_exists_driver.sql', rep_month=rep_month, rep_year=rep_year)
            product_result, schema = select(current_app.config['db_config'], _sql)
            if product_result:
                return render_template('report_form.html', message='Ошибка: такой отчёт уже существует!')
            call_proc(current_app.config['db_config'], 'work_by_drivers_report', rep_month, rep_year)
            _sql = provider.get('report_driver.sql', rep_month=rep_month, rep_year=rep_year)
            product_result, schema = select(current_app.config['db_config'], _sql)
            if not product_result:
                return render_template('report_form.html', message='Ошибка: попытка сделать пустой отчёт!')
            return render_template('report_form.html', message='Отчёт успешно создан!')
        else:
            return "Repeat input"


@blueprint_report.route('/view-driver-report', methods=['GET', 'POST'])
@group_required
def view_rep2():
    if request.method == 'GET':
        _sql = provider.get('available_driver.sql')
        product_result, schema = select(current_app.config['db_config'], _sql)
        locale.setlocale(locale.LC_ALL, 'ru_RU')
        rep_dates = []
        for product in product_result:
            rep_dates.append(calendar.month_name[product[0]] + " " + str(product[1]))
        print(rep_dates)
        return render_template('get_report.html', report_list=rep_dates)
    else:
        rep_name = report_list[1]['rep_name']
        rep_month = request.form.get('rep_date')
        rep_date = rep_month
        rep_month, rep_year = rep_month.split(' ')
        locale.setlocale(locale.LC_ALL, 'ru_RU')
        for index in range(1, 13):
            if calendar.month_name[index] == rep_month:
                rep_month = index
                break
        if rep_month and rep_year:
            print(rep_month, rep_year)
            _sql = provider.get('report_driver.sql', rep_month=rep_month, rep_year=rep_year)
            product_result, schema = select(current_app.config['db_config'], _sql)
            schema = ("ФИО водителя", "Сумма заказов (₽)", "Выполнено заказов", "Месяц", "Год")
            if not product_result:
                return "Repeat input"
            return render_template('rep.html', schema=schema, result=product_result, rep_date=rep_date, rep_name=rep_name)
        else:
            return "Repeat input"
