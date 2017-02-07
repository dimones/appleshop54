from flask import *
import os,pymysql,sys,base64,itertools, smtplib,uuid
from email.mime.text import MIMEText
from werkzeug.utils import secure_filename
app = Flask(__name__)
from os import listdir
from os.path import isfile, join
from requests.compat import basestring
from datetime import timedelta
from flask import make_response, request, current_app
from functools import update_wrapper
import Auth
UPLOAD_FOLDER = app.root_path
ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])

dict_data = { "телефоны-apple" : {"name": "ТЕЛЕФОНЫ APPLE", "name_top": "Телефоны Apple","cat" : 1, 'cat_1_name': 'Гигабайты',
                                      'cat_2_name': None, 'cat2_color': True, 'cat_1_def': 'Все объемы'},
             "планшеты": {"name": "ПЛАНШЕТЫ", "name_top": "Планшеты", "cat": 2},

             "smart-часы": {"name": "SMART ЧАСЫ", "name_top": "Smart часы", "cat": 3},

             "чехлы": {"name": "ЧЕХЛЫ", "name_top": "Чехлы", "cat": 4, 'cat_1_name': 'Тип чехла', 'cat_2_name': None, 'cat2_color': True,'cat_1_def': 'Все типы'},

             "фитнес-браслеты": {"name": "ФИТНЕС БРАСЛЕТЫ", "name_top": "Фитнес браслеты", "cat": 5, 'cat_1_name': 'Производитель',
                                 'cat_2_name': None, 'cat2_color': True, 'cat1_vendor': True, 'cat_1_def': 'Все производители'},

             "защита-экрана": {"name": "ЗАЩИТА ЭКРАНА", "name_top": "Защита экрана", "cat": 6, 'cat_1_name': 'Тип защиты', 'cat_2_name': 'Покрытие', 'cat_1_def': 'Все типы', 'cat_2_def': 'Все покрытия' },

             "другие-устройства": {"name": "ДРУГИЕ УСТРОЙСТВА", "name_top": "Другие устройства", "cat": 7,
                                   'cat_1_name': 'Тип устройства','cat_2_name': None, 'cat2_color': True, 'cat_1_def': 'Все устройства'},

             "аксессуары": {"name": "АКСЕССУАРЫ", "name_top": "Аксессуары", "cat": 8, 'cat_1_name': 'Тип',
                            'cat_2_name': 'Семейство','availible':'Зарядные устройства', 'cat2_color': None, 'cat_2_def': 'Все семейства', 'cat_1_def': 'Все типы'}}
#Роли пользователей
"""
-1 - никто
1 - админ
2 - seo manager
3 - добавлятор продуктов
4 - продавец
"""
print(json.dumps(dict_data,ensure_ascii=False))

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def roleError():
    return "У Вас нет доступа в этот раздел!"

def flat_to_nest(data, keys):
    """Преобразование "плоских" данных во вложенные
    """
    new_data = {}
    for key, group in itertools.groupby(data, lambda x: x[keys[0]]):
        group =  map(lambda x: dict((i, x[i]) for i in x if i != keys[0]), list(group))
        name = ""
        temp = flat_to_nest(group, keys[1:]) if keys[1:] else list(group)
        # print(temp)
        if isinstance(temp, list):
            print(temp[0]['category_name'])
            name = temp[0]['category_name']
            # pass
        new_data.update( {key:temp,'name': name} )
    return new_data

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

def get_conn():
    return pymysql.connect(host='82.146.41.220',
                             user='root',
                             password='jmXQF97JqkeNxV5B%',
                             db='appleshop54',
                             charset='utf8')
def get_conn_1():
    return pymysql.connect(host='82.146.41.220',
                             user='root',
                             password='jmXQF97JqkeNxV5B%',
                             db='appleshop54',
                             charset='utf8',
                             cursorclass=pymysql.cursors.DictCursor)

def product_getTypesFixed():
    connection = get_conn_1()
    try:
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT id,type_name FROM type_products")
            data = cursor.fetchall()
            _dat = {}
            for dat in data:
                _dat[dat['id']] = dat['type_name'].replace(' ','-').lower()
            connection.close()
            return json.dumps(_dat,ensure_ascii=False)
    except Exception as e:
        print(str(e), file=sys.stderr)
        return json.dumps({'succeed': False, "error": str(e)})
@app.route('/')
def main():
    connection = get_conn_1()
    data = None
    try:
        with connection.cursor() as cursor:
            cursor.execute("""
                                    SELECT
                            pr.id ,
                            pr.type_product ,
                            pr. NAME,
                            REPLACE(pr. NAME,'/',',') NAME_LINK,
                            pr.price ,
                            pr.main_image image_id ,
                            (
                                SELECT
                                    LOWER(REPLACE(tp.type_name , ' ' , '-')) link
                                FROM
                                    type_products tp
                                WHERE
                                    tp.id = pr.type_product
                            ) tp
                        FROM
                            products pr
                        WHERE
                            pr.is_special = 1""")
            connection.close()
            data = cursor.fetchall()
    except Exception as e:
        print(str(e), file=sys.stderr)
        return json.dumps({'succeed': False, "error": str(e)})
    return render_template('index.html',body=render_template('main.html',data=data))

@app.route('/ad/auth')
def ad_auth():
    return render_template('login.html')

@app.route('/admin/auth', methods=['POST'])
def admin_auth():
    username = request.form["username"]
    password = request.form["password"]
    device_id = request.form["device_id"]
    a = Auth.AdminAuther(username, password, device_id)
    obj = a.auth_user()
    print(obj)
    del a
    response = current_app.make_response(obj)
    j_obj = json.loads(obj)
    if j_obj['succeed'] is True:
        response.set_cookie('device_id', value=device_id)
        response.set_cookie('device_token', value=j_obj['device_token'])
    return response

@app.route('/контакты')
def contacts():
    return render_template('index.html',body=render_template('page.html',body=render_template('contacts.html')))
@app.route('/акции')
def discount():
    return render_template('index.html',body=render_template('page.html',body=render_template('discount.html')))
@app.route('/как-купить')
def how_tp_buys():
    return render_template('index.html',body=render_template('page.html',body=render_template('howtobuy.html')))
@app.route('/ремонт')
def repair():
    return render_template('index.html',body=render_template('page.html',body=render_template('repair.html')))
@app.route('/поиск')
def search():
    return render_template('index.html',body=render_template('page.html',body=render_template('search.html')))
@app.route('/доставка-и-оплата')
def delivery():
    return render_template('index.html',body=render_template('page.html',body=render_template('delivery.html')))
@app.route('/search_products')
def search_products():
    conn = get_conn_1()
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT pr.id,pr.type_product , pr. NAME , pr.price ,"
                           "pr.main_image image_id"
                           " FROM products pr WHERE pr.NAME LIKE '%" + request.args.get('query') + "%'")
            return render_template('products.html', products=cursor.fetchall(), types=product_getTypesFixed(), _path='телефоны-apple')
    except Exception as e:
        print(e)
    finally:
        conn.close()

def cat(_id):
    connection = get_conn_1()
    data = None
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT pr.id,pr.type_product , pr. NAME , pr.price ,"
                           "pr.main_image image_id"
                           " FROM products pr WHERE pr.type_product=%s" % _id)
            connection.close()
            data = cursor.fetchall()
    except Exception as e:
        print(str(e), file=sys.stderr)
        return json.dumps({'succeed': False, "error": str(e)})
    return data

def cat_prices(_id):
    connection = get_conn_1()
    data = None
    try:
        with connection.cursor() as cursor:
            if _id == -1:
                cursor.execute("SELECT MIN(pr.price) min, MAX(pr.price) max FROM products pr")
            else:
                cursor.execute("SELECT MIN(pr.price) min, MAX(pr.price) max FROM products pr WHERE pr.type_product=%s" % _id)
            data = cursor.fetchone()
            connection.close()
    except Exception as e:
        print(str(e), file=sys.stderr)
        return json.dumps({'succeed': False, "error": str(e)})
    ret_data = {}
    if data['min'] is None:
        data['min'] = 0

    if data['max'] is None:
        data['max'] = 0
    ret_data.update({'min':data['min']})
    ret_data.update({'max':data['max']})
    ret_data.update({'pr_min':int(data['min'] * 1.2)})
    ret_data.update({'pr_max':int(data['max'] * 0.88)})
    return ret_data

def getCatData(_id):
    connection = get_conn_1()
    data = None
    try:
        print(_id)
        with connection.cursor() as cursor:
            cursor.execute('SELECT c.id, c.category_name name FROM product_categ c WHERE c.type_id = %s' % _id)
            da = cursor.fetchall()
            out_data = {}
            for dat in da:
                cursor.execute("SELECT s.id sid,s.categ_id,s.subcateg_name FROM product_subcat s WHERE s.categ_id = %s"
                               % dat['id'])
                out_data.update({dat['id']: {'name' : dat['name'], 'data': list(cursor.fetchall())}})
            return out_data
            cursor.execute('SELECT c.id cid,c.category_name,s.id sid,s.categ_id,s.subcateg_name FROM product_categ c,'
                           'product_subcat s WHERE c.type_id=%s and (s.categ_id = c.id OR  ORDER BY cid,sid' % _id)
            data = cursor.fetchall()
            cat_data = {}
            for dat in data:
                if dat['cid'] in cat_data:
                    cat_data[dat['cid']]['data'].append({'name':dat['subcateg_name'],'sid': dat['sid']})
                else:
                    cat_data.update({ dat['cid']: { 'data': [{'name':dat['subcateg_name'],'sid': dat['sid']}],'name':dat['category_name'] }})
            connection.close()
            return cat_data
    except Exception as e:
        print(str(e), file=sys.stderr)
        return json.dumps({'succeed': False, "error": str(e)})


@app.route('/remove_order_request', methods=['POST'])
def remove_order_request():
    connection = get_conn_1()
    data = None
    try:
        with connection.cursor() as cursor:
            cursor.execute("DELETE FROM orders WHERE id = %s" % request.form['id'])
            connection.commit()
            connection.close()
            return json.dumps({'succeed': True})
    except Exception as e:
        print(str(e), file=sys.stderr)
        return json.dumps({'succeed': False, "error": str(e)})
@app.route('/order_request', methods=['POST'])
def order_request():
    connection = get_conn_1()
    data = None
    try:
        with connection.cursor() as cursor:
            print("INSERT INTO orders (name,phone,date,product_id,email,comment) VALUES('%s','%s',NOW(),%s,'%s','%s')"
                           % (request.form['name'],request.form['phone'],request.form['product_id'],request.form['email'],request.form['comment']))
            cursor.execute("INSERT INTO orders (name,phone,date,product_id,email,comment) VALUES('%s','%s',NOW(),%s,'%s','%s')"
                           % (request.form['name'],request.form['phone'],request.form['product_id'],request.form['email'],request.form['comment']))
            connection.commit()
            name_product = ""
            cursor.execute('SELECT name FROM products WHERE id = %s' % request.form['product_id'])
            name_product = cursor.fetchone()['name']
            connection.close()

            me = 'system@appleshop54.com'
            smtp_server = 'smtp.yandex.ru'
            msg = MIMEText('Новый заказ на %s на звонок от %s по номеру %s' % (name_product,request.form['name'],request.form['phone']), 'html')
            msg['Subject'] = 'Новый заказ!'
            msg['From'] = me
            msg['To'] = 'direct@appleshop54.com'
            # print(text)
            s = smtplib.SMTP_SSL(host=smtp_server, port=465)
            s.login(me, 'qkeNxV5B')
            s.sendmail(me, ['direct@appleshop54.com'], msg.as_string())
            s.quit()
            return json.dumps({'succeed': True})
    except Exception as e:
        print(str(e), file=sys.stderr)
        return json.dumps({'succeed': False, "error": str(e)})
@app.route('/remove_call_request',methods=['POST'])
def remove_call_request():
    connection = get_conn_1()
    data = None
    try:
        with connection.cursor() as cursor:
            cursor.execute("DELETE FROM call_requests WHERE id = %s" % (request.form['id']))
            connection.commit()
            connection.close()
            return json.dumps({'succeed':True})
    except Exception as e:
        print(str(e), file=sys.stderr)
        return json.dumps({'succeed': False, "error": str(e)})
@app.route('/call_request', methods=['POST'])
def call_request():
    connection = get_conn_1()
    data = None
    try:
        with connection.cursor() as cursor:
            cursor.execute("INSERT INTO call_requests (name,phone,date,is_called) VALUES('%s','%s',NOW(),0)" % (request.form['name'],request.form['phone']))
            connection.commit()
            connection.close()
            me = 'system@appleshop54.com'
            smtp_server = 'smtp.yandex.ru'
            msg = MIMEText('Новый запрос на звонок от %s по номеру %s' % (request.form['name'],request.form['phone']), 'html')
            msg['Subject'] = 'Новый запрос на звонок!'
            msg['From'] = me
            msg['To'] = 'direct@appleshop54.com'
            # print(text)
            s = smtplib.SMTP_SSL(host=smtp_server, port=465)
            s.login(me, 'qkeNxV5B')
            s.sendmail(me, ['direct@appleshop54.com'], msg.as_string())
            s.quit()
            return json.dumps({'succeed': True})
    except Exception as e:
        print(str(e), file=sys.stderr)
        return json.dumps({'succeed': False, "error": str(e)})
    return data
@app.route('/get_image/<id>')
def get_image(id):
    connection = get_conn()
    data = None
    try:
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT image,extension FROM product_images WHERE id = %s" % id)
            data = cursor.fetchone()
            return Response(base64.b64decode(data[0]), mimetype=data[1])
            return 'data:%s;base64,%s' % (data[1], data[0])
    except Exception as e:
        print(str(e), file=sys.stderr)
        return json.dumps({'succeed': False, "error": str(e)})

@app.route('/getProductsBy',methods=['GET'])
def getProductsBy():
    connection = get_conn_1()
    data = None
    try:
        with connection.cursor() as cursor:
            cat = request.args.get('cat')
            subcat = request.args.get('subcat')
            color = request.args.get('color')
            type_id = request.args.get('type')
            path = request.args.get('path')
            vendor = request.args.get('vendor')
            priceMin = request.args.get('priceMin')
            priceMax = request.args.get('priceMax')
            print(priceMax)
            if priceMin == '':
                priceMin = 0
            if priceMax == '':
                priceMax = 0
            if cat != '' and subcat != '' and color != '':
                cursor.execute("SELECT pr.id,pr.type_product , pr. NAME , pr.price ,"
                               "pr.main_image image_id"
                               " FROM products pr WHERE pr.categ_id = %s AND pr.color_id = %s AND pr.subcateg_id = %s AND ( price <= %s AND price >= %s)" % (cat,color,subcat,priceMax,priceMin))
                print("SELECT pr.id,pr.type_product , pr. NAME , pr.price ,"
                               "pr.main_image image_id"
                               " FROM products pr WHERE pr.categ_id = %s AND pr.color_id = %s AND pr.subcateg_id = %s AND ( price <= %s AND price >= %s)" % (cat,color,subcat,priceMax,priceMin))
            elif cat!= '' and color != '':
                cursor.execute("SELECT pr.id,pr.type_product , pr. NAME , pr.price ,"
                               "pr.main_image image_id"
                               " FROM products pr WHERE pr.categ_id = %s AND pr.color_id = %s  AND ( price <= %s AND price >= %s)" % (
                               cat, color,priceMax,priceMin))
                print("SELECT pr.id,pr.type_product , pr. NAME , pr.price ,"
                               "pr.main_image image_id"
                               " FROM products pr WHERE pr.categ_id = %s AND pr.color_id = %s  AND ( price <= %s AND price >= %s)" % (
                               cat, color,priceMax,priceMin))
            elif cat!= '' and subcat != '':
                cursor.execute("SELECT pr.id,pr.type_product , pr. NAME , pr.price ,"
                               "pr.main_image image_id "
                               "FROM products pr WHERE pr.categ_id = %s AND pr.subcateg_id = %s  AND ( price <= %s AND price >= %s)" % (
                               cat, subcat,priceMax,priceMin))
                print("SELECT pr.id,pr.type_product , pr. NAME , pr.price ,"
                               "pr.main_image image_id "
                               "FROM products pr WHERE pr.categ_id = %s AND pr.subcateg_id = %s  AND ( price <= %s AND price >= %s)" % (
                               cat, subcat,priceMax,priceMin))
            elif cat!= '':
                cursor.execute("SELECT pr.id,pr.type_product , pr. NAME , pr.price,"
                               "pr.main_image image_id"
                               " FROM products pr WHERE pr.categ_id = %s  AND ( price <= %s AND price >= %s)" % (
                               cat,priceMax,priceMin))
                print("SELECT pr.id,pr.type_product , pr. NAME , pr.price,"
                               "pr.main_image image_id"
                               " FROM products pr WHERE pr.categ_id = %s  AND ( price <= %s AND price >= %s)" % (
                               cat,priceMax,priceMin))
            elif color!= '':
                cursor.execute("SELECT pr.id,pr.type_product , pr. NAME , pr.price ,"
                               "pr.main_image image_id"
                               " FROM products pr WHERE pr.color_id = %s  AND ( price <= %s AND price >= %s)" % (
                               color,priceMax,priceMin))
                print("SELECT pr.id,pr.type_product , pr. NAME , pr.price ,"
                               "pr.main_image image_id"
                               " FROM products pr WHERE pr.color_id = %s  AND ( price <= %s AND price >= %s)" % (
                               color,priceMax,priceMin))
            elif subcat!= '':
                cursor.execute("SELECT pr.id,pr.type_product , pr. NAME , pr.price ,"
                               "pr.main_image image_id"
                               " FROM products pr WHERE pr.subcateg_id = %s  AND ( price <= %s AND price >= %s)" % (
                               subcat,priceMax,priceMin))
                print("SELECT pr.id,pr.type_product , pr. NAME , pr.price ,"
                               "pr.main_image image_id"
                               " FROM products pr WHERE pr.subcateg_id = %s  AND ( price <= %s AND price >= %s)" % (
                               subcat,priceMax,priceMin))
            elif vendor!= '':
                cursor.execute("SELECT pr.id,pr.type_product , pr. NAME , pr.price ,"
                               "pr.main_image image_id"
                               " FROM products pr WHERE pr.vendor = '%s'  AND ( price <= %s AND price >= %s)" % (
                               vendor,priceMax,priceMin))
            elif type_id!= '':
                cursor.execute("SELECT pr.id,pr.type_product , pr. NAME , pr.price ,"
                               "pr.main_image image_id"
                               " FROM products pr WHERE pr.type_product = %s AND ( price <= %s AND price >= %s)" % (
                               type_id,priceMax,priceMin))
                print("SELECT pr.id,pr.type_product , pr. NAME , pr.price ,"
                               "pr.main_image image_id"
                               " FROM products pr WHERE pr.type_product = %s AND ( price <= %s AND price >= %s)" % (
                               type_id,priceMax,priceMin))
            connection.close()
            data = cursor.fetchall()
    except Exception as e:
        print(str(e), file=sys.stderr)
        return json.dumps({'succeed': False, "error": str(e)})
    return render_template('products.html', products=data,types=product_getTypesFixed(),_path = 'телефоны-apple')

@app.route('/getColorsByType', methods=['GET'])
def getColorByType():
    connection = get_conn_1()
    data = None
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT DISTINCT(pr.color_id),(SELECT color_name FROM product_colors WHERE id = pr.color_id) color FROM "
                           "products pr WHERE pr.color_id > 0 AND pr.type_product = %s" % request.args.get('id'))
            connection.close()
            data = cursor.fetchall()
    except Exception as e:
        print(str(e), file=sys.stderr)
        return json.dumps({'succeed': False, "error": str(e)})
    return json.dumps(data,ensure_ascii=False)

@app.route('/getVendorsByType', methods=['GET'])
def getVendorsByType():
    connection = get_conn_1()
    data = None
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT DISTINCT(pr.vendor) FROM products pr WHERE pr.type_product = %s" % request.args.get('id'))
            connection.close()
            data = cursor.fetchall()
    except Exception as e:
        print(str(e), file=sys.stderr)
        return json.dumps({'succeed': False, "error": str(e)})
    return json.dumps(data,ensure_ascii=False)





@app.route('/каталог/<string:path>/')
@app.route('/каталог/<string:path>')
def catalog_path(path):
    print(path)
    print('catalogue')
    #TODO ну это пиздец. Не смог нормально придумать

    return render_template('index.html', body=render_template('page.html', body=render_template('catalog.html',
                                                                                                products=render_template(
                                                                                                    'products.html',
                                                                                                    products=cat(dict_data[path]['cat']),
                                                                                                    types=product_getTypesFixed(),
                                                                                                    _path = path),
                                                                                                name=dict_data[path]['name'],
                                                                                                name_top=dict_data[path]['name_top'],
                                                                                                prices=cat_prices(dict_data[path]['cat']),data=dict_data[path],
                                                                                                cat_data=getCatData(dict_data[path]['cat']), js_data = json.dumps(dict_data[path]))))

@app.route('/каталог/<string:path>/<string:name_cat>/')
@app.route('/каталог/<string:path>/<string:name_cat>')
def catalog_path_name_cat(path,name_cat=None):
    connection = get_conn_1()
    data = None
    data_specs = None
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT pr.id,pr.type_product , pr. NAME , pr.price ,pr.description,pr.type_product,"
                           "pr.main_image image_id FROM products pr WHERE pr.id = %s" % request.args.get(
                'product_id'))
            data = cursor.fetchone()
            cursor.execute('SELECT * FROM product_specs WHERE product_id = %s ' % request.args.get('product_id'))
            data_specs = cursor.fetchall()
            print(data_specs)
            connection.close()
    except Exception as e:
        print(str(e), file=sys.stderr)
        return json.dumps({'succeed': False, "error": str(e)})
    return render_template('index.html', body=render_template('page.html', body=render_template('catalog.html',
                                                                                                products=render_template(
                                                                                                    'product_detailed.html',
                                                                                                    product=data,specs=data_specs),
                                                                                                name=data[
                                                                                                    'NAME'].upper(),
                                                                                                name_top=data[
                                                                                                    'NAME'],
                                                                                                types=product_getTypesFixed(), specs=data_specs)))
@app.route('/каталог')
def catalog():
    connection = get_conn_1()
    data = None
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT pr.id,pr.type_product , pr. NAME , pr.price ,"
                           "pr.main_image FROM products pr")
            connection.close()
            data = cursor.fetchall()
    except Exception as e:
        print(str(e), file=sys.stderr)
        return json.dumps({'succeed': False, "error": str(e)})

    return render_template('index.html', body=render_template('page.html', body=render_template('catalog.html',
                                                                                                products=render_template(
                                                                                                    'products.html',
                                                                                                    products=data),
                                                                                                name='КАТАЛОГ ПРОДУКЦИИ',
                                                                                                name_top='Все',types=product_getTypesFixed(), prices=cat_prices(-1))))
@app.route('/каталог/подробнее')
def catalog_detail():
    connection = get_conn_1()
    data = None
    specs = None
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT pr.id,pr.type_product , pr. NAME , pr.price ,"
                           "pr.main_image image_id FROM products pr WHERE pr.id = %s" % request.args.get('product_id'))
            data = cursor.fetchone()
            cursor.execute("SELECT * FROM product_specs WHERE product_id = %s" % request.args.get('product_id'))
            specs = cursor.fetchall()
            print(specs)
            connection.close()
    except Exception as e:
        print(str(e), file=sys.stderr)
        return json.dumps({'succeed': False, "error": str(e)})
    return render_template('index.html', body=render_template('page.html', body=render_template('catalog.html',
                                                                                                products=render_template(
                                                                                                    'product_detailed.html',
                                                                                                     product=data,specs=specs),
                                                                                                name=data['NAME'].upper(),
                                                                                                name_top=data['NAME'],
                                                                                                types=product_getTypesFixed(), prices=cat_prices(-1))))

@app.route('/ad')
def admin():
    if 'device_token' not in request.cookies or 'device_id' not in request.cookies:
        print('cookie fail')
        return redirect(url_for('ad_auth'))
    a_h = Auth.AdminHelper(request.cookies['device_token'], request.cookies['device_id'])
    if a_h.isValid() != True:
        print('token fail')
        return redirect(url_for('ad_auth'))
    connection = get_conn_1()
    data = None
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT pr.id,pr.type_product , pr. NAME , pr.price ,pr.is_special,"
                           "pr.main_image image_id FROM products pr")
            connection.close()
            data = cursor.fetchall()
    except Exception as e:
        print(str(e), file=sys.stderr)
        return json.dumps({'succeed': False, "error": str(e)})
    if int(a_h.getRole()) is 1:
        return render_template('admin.html', product_list=render_template('product_list.html',products=data), admin_level=a_h.getRole())
    elif int(a_h.getRole()) is 2:
        return render_template('seo.html',admin_level = 2)
@app.route('/ad/new')
def admin_new():
    if 'device_token' not in request.cookies or 'device_id' not in request.cookies:
        return redirect(url_for('ad_auth'))
    a_h = Auth.AdminHelper(request.cookies['device_token'], request.cookies['device_id'])
    if a_h.isValid() != True:
        return redirect(url_for('ad_auth'))
    if int(a_h.getRole()) not in [1,4]:
        return roleError()
    return render_template('admin_new_product.html',admin_level=a_h.getRole())
@app.route('/ad/seo')
def ad_seo():
    if 'device_token' not in request.cookies or 'device_id' not in request.cookies:
        return redirect(url_for('ad_auth'))
    a_h = Auth.AdminHelper(request.cookies['device_token'], request.cookies['device_id'])
    if a_h.isValid() != True:
        return redirect(url_for('ad_auth'))
    if int(a_h.getRole()) not in [1, 2]:
        return roleError()
    return render_template('seo.html',admin_level = a_h.getRole())

@app.route('/ad/users')
def ad_users():
    if 'device_token' not in request.cookies or 'device_id' not in request.cookies:
        return redirect(url_for('ad_auth'))
    a_h = Auth.AdminHelper(request.cookies['device_token'], request.cookies['device_id'])
    if a_h.isValid() != True:
        return redirect(url_for('ad_auth'))
    if int(a_h.getRole()) not in [1, 2]:
        return roleError()
    return render_template('users.html',admin_level = a_h.getRole(),users=ad_users_get_html())
@app.route('/ad/users/get_html')
def ad_users_get_html():
    connection = get_conn_1()
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM MYNSTU_ADMIN_USERS")
            data = cursor.fetchall()
            return render_template('users_list.html',users=data)
    except Exception as e:
        print(e)
#users
@app.route('/ad/users/get',methods=['GET'])
def ad_users_get():
    connection = get_conn_1()
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM MYNSTU_ADMIN_USERS")
            data = cursor.fetchall()
            return json.dumps(data,ensure_ascii=False)
    except Exception as e:
        print(e)
@app.route('/ad/users/add',methods=['POST'])
def ad_users_add():
    connection = get_conn_1()
    print(request.form)
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT id FROM MYNSTU_ADMIN_USERS WHERE username = '%s'"
                           % (request.form['username']))
            if cursor.rowcount == 0:
                cursor.execute("INSERT INTO MYNSTU_ADMIN_USERS(username,password,role) " +
                               "VALUES ('%s','%s',%s)" % (request.form['username'],
                                                          request.form['password'], request.form['role']))
                connection.commit()
                connection.close()
                return json.dumps({"succeed": True})
            else:
                return json.dumps({"succeed": False })
    except Exception as e:
        print(e)
@app.route('/ad/users/remove',methods=['GET'])
def ad_users_remove():
    connection = get_conn_1()
    try:
        with connection.cursor() as cursor:
            cursor.execute("DELETE FROM MYNSTU_ADMIN_USERS WHERE id = %s"
                           % (request.args.get('id')))
            connection.commit()
            connection.close()
            return json.dumps({"succeed": True})
    except Exception as e:
        print(e)
@app.route('/ad/users/set_role',methods=['GET'])
def ad_users_set_role():
    connection = get_conn_1()
    try:
        with connection.cursor() as cursor:
            cursor.execute("UPDATE MYNSTU_ADMIN_USERS SET role = %s WHERE id=%s" %
                           (request.args.get('role'),request.args.get('user_id')))
            connection.commit()
            return json.dumps({"succeed":True},ensure_ascii=False)
    except Exception as e:
        print(e)
@app.route('/ad/users/change_password',methods=['POST'])
def ad_users_change_password():
    connection = get_conn_1()
    try:
        with connection.cursor() as cursor:
            cursor.execute("UPDATE MYNSTU_ADMIN_USERS SET password = '%s' WHERE id=%s" %
                           (request.form['password'],request.form['user_id']))
            connection.commit()
            return json.dumps({"succeed":True },ensure_ascii=False)
    except Exception as e:
        print(e)

@app.route('/ad/clients/get_data')
def clients_getData():
    connection = get_conn_1()
    data = None
    data_Orders = None
    try:
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT * FROM call_requests")
            data = cursor.fetchall()
            cursor.execute("SELECT o.id,o.name,o.phone,o.email,o.comment, o.date,"
                           "(SELECT name FROM products WHERE id = o.product_id) product FROM orders o")
            data_Orders = cursor.fetchall()
            connection.close()
    except Exception as e:
        print(str(e), file=sys.stderr)
        return json.dumps({'succeed': False, "error": str(e)})
    return json.dumps({'calls': render_template('client/calls.html',calls=data),'orders': render_template('client/orders.html',orders=data_Orders)},ensure_ascii=False)
@app.route('/ad/clients')
def admin_calls():
    if 'device_token' not in request.cookies or 'device_id' not in request.cookies:
        print('cookie fail')
        return redirect(url_for('ad_auth'))
    a_h = Auth.AdminHelper(request.cookies['device_token'], request.cookies['device_id'])
    if a_h.isValid() != True:
        print('token fail')
        return redirect(url_for('ad_auth'))

    if int(a_h.getRole()) not in [1, 2]:
        return roleError()
    connection = get_conn_1()
    data = None
    data_Orders = None
    try:
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT * FROM call_requests")
            data = cursor.fetchall()
            cursor.execute("SELECT o.id,o.name,o.phone,o.email,o.comment, o.date,"
                           "(SELECT name FROM products WHERE id = o.product_id) product FROM orders o")
            data_Orders = cursor.fetchall()
            connection.close()
    except Exception as e:
        print(str(e), file=sys.stderr)
        return json.dumps({'succeed': False, "error": str(e)})
    return render_template('calls.html',calls=render_template('client/calls.html',calls=data),
                           orders=render_template('client/orders.html',orders=data_Orders),
                           admin_level = a_h.getRole())

@app.route('/ad/change/<product_id>')
def admin_change_product(product_id):
    if 'device_token' not in request.cookies or 'device_id' not in request.cookies:
        print('cookie fail')
        return redirect(url_for('ad_auth'))
    a_h = Auth.AdminHelper(request.cookies['device_token'], request.cookies['device_id'])
    if a_h.isValid() != True:
        print('token fail')
        return redirect(url_for('ad_auth'))
    if int(a_h.getRole()) not in [1,3]:
        return roleError()
    connection = get_conn_1()
    data = None
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT pr.id,pr.type_product , pr. NAME , pr.price ,pr.description,pr.categ_id,pr.subcateg_id,pr.vendor,pr.color_id,"
                           "( SELECT image FROM product_images WHERE product_id = pr.id AND is_main = 1 LIMIT 0,1) image ,"
                           "( SELECT extension FROM product_images WHERE product_id = pr.id AND is_main = 1 LIMIT 0,1) extension FROM products pr WHERE pr.id = %s" % product_id)
            connection.close()
            data = cursor.fetchone()
    except Exception as e:
        print(str(e), file=sys.stderr)
        return json.dumps({'succeed': False, "error": str(e)})
    return render_template('change_product.html',product_id=product_id,data=data,
                           admin_level=a_h.getRole())

@app.route('/ad/change/special/set', methods=['GET'])
def special_set():
    connection = get_conn_1()
    try:
        with connection.cursor() as cursor:
            print(request.args.get)
            if int(request.args.get('is_special')) is 1:
                cursor.execute("SELECT count(id) c FROM products WHERE is_special = 1")
                t = cursor.fetchone()['c']
                print(t)
                if t >= 8:
                    return json.dumps({'succeed': False })
                cursor.execute(
                    "UPDATE products SET is_special = %s WHERE id = %s" % (request.args.get('is_special'),request.args.get('product_id')))
            else:
                cursor.execute(
                    "UPDATE products SET is_special = %s WHERE id = %s" % (request.args.get('is_special'),request.args.get('product_id')))

            connection.commit()
            connection.close()
            return json.dumps({"success":True}, ensure_ascii=False)
    except Exception as e:
        print(str(e), file=sys.stderr)
        return json.dumps({'succeed': False, "error": str(e)})

@app.route('/ad/change/special/unset', methods=['GET'])
def special_unset():
    connection = get_conn_1()
    try:
        with connection.cursor() as cursor:
            cursor.execute(
                "UPDATE products SET is_special = %s WHERE id = " % (request.args.get('is_special')))
            connection.commit()
            connection.close()
            return json.dumps(cursor.fetchall(), ensure_ascii=False)
    except Exception as e:
        print(str(e), file=sys.stderr)
        return json.dumps({'succeed': False, "error": str(e)})

@app.route('/upload/<_id>', methods=['GET', 'POST'])
def upload_file_2(_id):
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        # if user does not select file, browser also
        # submit a empty part without filename
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            next_id = -1
            connection = get_conn()

            if _id != -1:
                mypath = app.config['UPLOAD_FOLDER'] + '/static/img/products/tmp/' + str(_id) + '/'
                if os.path.exists(app.config['UPLOAD_FOLDER'] + '/static/img/products/tmp/' + str(_id) ) != True:
                    os.mkdir(app.config['UPLOAD_FOLDER'] + '/static/img/products/tmp/' + str(_id))
                file.save(os.path.join(app.config['UPLOAD_FOLDER'] + '/static/img/products/tmp/' + str(_id) + '/',
                                       str(uuid.uuid4().hex) + '.' +filename.rsplit('.', 1)[1]))
                # buffer = None
                # try:
                #     with connection.cursor() as cursor:
                #         cursor.execute(
                #             "INSERT INTO product_images(id,product_id,is_main,extension) VALUES (%s,%s,%s,'image/%s')" % (next_id,base64.b64encode(buffer).decode('utf8'),-1,0,filename.rsplit('.', 1)[1]))
                #         connection.commit()
                #         connection.close()
                #         return json.dumps({'imgId': cursor.lastrowid})
                # except Exception as e:
                #     print(str(e), file=sys.stderr)
                #     return json.dumps({'succeed': False, "error": str(e)})
                # file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                return 'good'

@app.route('/upload', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        # if user does not select file, browser also
        # submit a empty part without filename
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            next_id = -1
            connection = get_conn()
            try:
                with connection.cursor() as cursor:
                    cursor.execute(
                        "SELECT AUTO_INCREMENT FROM information_schema. tables WHERE table_name = 'product_images' AND table_schema = DATABASE();")

                    connection.close()
                    next_id = cursor.fetchone()[0]
            except Exception as e:
                print(str(e), file=sys.stderr)
                return json.dumps({'succeed': False, "error": str(e)})
            if next_id != -1:
                if os.path.exists(app.config['UPLOAD_FOLDER'] + '/static/img/products/tmp/' + str(next_id) + '/') != True:
                    os.mkdir(app.config['UPLOAD_FOLDER'] + '/static/img/products/tmp/' + str(next_id) + '/')
                file.save(os.path.join(app.config['UPLOAD_FOLDER'] + '/static/img/products/tmp/' + str(next_id) + '/',
                                       str(next_id) + '.' +filename.rsplit('.', 1)[1]))
                buffer = None
                try:
                    with connection.cursor() as cursor:
                        cursor.execute(
                            "INSERT INTO product_images(id,product_id,is_main,extension) VALUES (%s,%s,%s,'image/%s')" % (next_id,base64.b64encode(buffer).decode('utf8'),-1,0,filename.rsplit('.', 1)[1]))
                        connection.commit()
                        connection.close()
                        return json.dumps({'imgId': cursor.lastrowid})
                except Exception as e:
                    print(str(e), file=sys.stderr)
                    return json.dumps({'succeed': False, "error": str(e)})
                # file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                return 'good'

@app.route('/ad/product/data')
def product_categLoad():
    connection = get_conn_1()
    try:
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT categ_id,subcateg_id,type_product FROM products WHERE id = %s" % request.args.get('prod_id'))
            connection.close()
            return json.dumps(cursor.fetchall(), ensure_ascii=False)
    except Exception as e:
        print(str(e), file=sys.stderr)
        return json.dumps({'succeed': False, "error": str(e)})
@app.route('/ad/product/categ/all')
def product_categAll():
    connection = get_conn_1()
    try:
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT * FROM product_categ WHERE type_id = %s" % request.args.get('type_id'))

            connection.close()
            return json.dumps(cursor.fetchall(), ensure_ascii=False)
    except Exception as e:
        print(str(e), file=sys.stderr)
        return json.dumps({'succeed': False, "error": str(e)})

@app.route('/ad/product/categ/add')
def product_categAdd():
    connection = get_conn_1()
    try:
        with connection.cursor() as cursor:
            cursor.execute(
                "INSERT INTO product_categ(category_name,type_id) VALUES('%s',%s)" % (request.args.get('categ_name'),request.args.get('type_id')))
            connection.commit()
            connection.close()
            return json.dumps({'succeed': True}, ensure_ascii=False)
    except Exception as e:
        print(str(e), file=sys.stderr)
        return json.dumps({'succeed': False, "error": str(e)})

@app.route('/ad/product/sub_categ/all')
def product_sub_categAll():
    connection = get_conn_1()
    try:
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT * FROM product_subcat WHERE categ_id = %s" % (request.args.get('categ_id')))

            connection.close()
            return json.dumps(cursor.fetchall(), ensure_ascii=False)
    except Exception as e:
        print(str(e), file=sys.stderr)
        return json.dumps({'succeed': False, "error": str(e)})

@app.route('/ad/product/sub_categ/add')
def product_sup_categAdd():
    connection = get_conn_1()
    try:
        with connection.cursor() as cursor:
            cursor.execute(
                "INSERT INTO product_subcat(subcateg_name,categ_id) VALUES('%s',%s)" % (request.args.get('subcateg_name'),request.args.get('categ_id')))
            connection.commit()
            connection.close()
            return json.dumps(cursor.fetchall(), ensure_ascii=False)
    except Exception as e:
        print(str(e), file=sys.stderr)
        return json.dumps({'succeed': False, "error": str(e)})
@app.route('/ad/product/get_by_type')
def product_getByType():
    connection = get_conn_1()
    data = None
    try:
        with connection.cursor() as cursor:
            if request.args.get('type') is None:
                cursor.execute("SELECT pr.id,pr.type_product , pr. NAME , pr.price ,"
                               "( SELECT image FROM product_images WHERE product_id = pr.id AND is_main = 1 LIMIT 0,1) image ,"
                               "( SELECT extension FROM product_images WHERE product_id = pr.id AND is_main = 1 LIMIT 0,1) extension FROM products pr")
            else:
                cursor.execute("SELECT pr.id,pr.type_product , pr. NAME , pr.price ,"
                               "( SELECT image FROM product_images WHERE product_id = pr.id AND is_main = 1 LIMIT 0,1) image ,"
                               "( SELECT extension FROM product_images WHERE product_id = pr.id AND is_main = 1 LIMIT 0,1) extension FROM products pr WHERE pr.type_product = %s" % (request.args.get('type')))
            connection.close()
            data = cursor.fetchall()
            return render_template('product_list.html',products=data)
    except Exception as e:
        print(str(e), file=sys.stderr)
        return json.dumps({'succeed': False, "error": str(e)})
@app.route('/ad/product/get_types', methods=['GET'])
def product_getTypes():
    connection = get_conn_1()
    try:
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT id,type_name FROM type_products")

            connection.close()
            return json.dumps(cursor.fetchall(),ensure_ascii=False)
    except Exception as e:
        print(str(e), file=sys.stderr)
        return json.dumps({'succeed': False, "error": str(e)})

@app.route('/ad/product/add_colors', methods=['GET'])
def product_addColors():
    connection = get_conn_1()
    try:
        with connection.cursor() as cursor:
            cursor.execute('SELECT id FROM product_colors WHERE color_name =\'%s\'' % request.args.get('color_name'))
            if cursor.rowcount == 0:
                cursor.execute(
                    "INSERT INTO product_colors(color_name) VALUES('%s')" % request.args.get('color_name'))
                connection.commit()
                connection.close()
            return json.dumps('', ensure_ascii=False)
    except Exception as e:
        print(str(e), file=sys.stderr)
        return json.dumps({'succeed': False, "error": str(e)})
@app.route('/ad/product/get_colors', methods=['GET'])
def product_getColors():
    connection = get_conn_1()
    try:
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT * FROM product_colors")

            connection.close()
            return json.dumps(cursor.fetchall(), ensure_ascii=False)
    except Exception as e:
        print(str(e), file=sys.stderr)
        return json.dumps({'succeed': False, "error": str(e)})
@app.route('/ad/product/del_color', methods=['GET'])
def product_delColor():
    connection = get_conn_1()
    try:
        with connection.cursor() as cursor:
            cursor.execute(
                "DELETE FROM product_colors WHERE id = %s" % (
                request.args.get('color_id')))
            connection.commit()
            connection.close()
            return json.dumps(cursor.fetchall(), ensure_ascii=False)
    except Exception as e:
        print(str(e), file=sys.stderr)
        return json.dumps({'succeed': False, "error": str(e)})
@app.route('/ad/product/set_color', methods=['GET'])
def product_setColor():
    connection = get_conn_1()
    try:
        with connection.cursor() as cursor:
            cursor.execute(
                "UPDATE products SET color_id = %s WHERE id = %s" % (request.args.get('color_id'),request.args.get('product_id')))
            connection.commit()
            connection.close()
            return json.dumps(cursor.fetchall(), ensure_ascii=False)
    except Exception as e:
        print(str(e), file=sys.stderr)
        return json.dumps({'succeed': False, "error": str(e)})
@app.route('/ad/product/add', methods=['GET'])
def product_add():
    connection = get_conn()
    try:
        with connection.cursor() as cursor:
            cursor.execute("INSERT INTO products(type_product,name,price,description,vendor,categ_id,subcateg_id,is_special,main_image) VALUES(%s,'%s',%s,'%s','%s',%s,%s,0,'%s')"
                           %(request.args.get('type_product'),request.args.get('name'),
                             request.args.get('price'),request.args.get('description'),request.args.get('vendor'),
                             request.args.get('categ'),request.args.get('sub_categ'),request.args.get('main_image')))
            connection.commit()
            connection.close()
            return json.dumps({'succeed':True})
    except Exception as e:
        print(str(e), file=sys.stderr)
        return json.dumps({'succeed': False, "error": str(e)})

@app.route('/ad/product/update', methods=['GET'])
def product_update():
    print(request.args)
    connection = get_conn()
    try:
        with connection.cursor() as cursor:
            print("UPDATE products SET type_product=%s, NAME='%s', price = %s , description='%s' , vendor = '%s'"
                           " , categ_id=%s , subcateg_id=%s, main_image=%s WHERE id=%s"
                           %(request.args.get('type_product'),request.args.get('name'),
                             request.args.get('price'),request.args.get('description'),request.args.get('vendor'),
                             request.args.get('categ'),request.args.get('sub_categ'),request.args.get('main_image'),request.args.get('product_id')))
            cursor.execute("UPDATE products SET type_product=%s, NAME='%s', price = %s , description='%s' , vendor = '%s'"
                           " , categ_id=%s , subcateg_id=%s, main_image='%s' WHERE id=%s"
                           %(request.args.get('type_product'),request.args.get('name'),
                             request.args.get('price'),request.args.get('description'),request.args.get('vendor'),
                             request.args.get('categ'),request.args.get('sub_categ'),request.args.get('main_image'),request.args.get('product_id')))
            connection.commit()
            connection.close()
            return json.dumps({'succeed':True})
    except Exception as e:
        print(str(e), file=sys.stderr)
        return json.dumps({'succeed': False, "error": str(e)})

@app.route('/ad/product/remove',methods= ['GET'])
def product_remove():
    connection = get_conn()
    try:
        with connection.cursor() as cursor:
            print(request.args.get('product_id'))
            cursor.execute("DELETE FROM products WHERE id = %s" % request.args.get('product_id'))
            connection.commit()
            connection.close()
            return json.dumps({'succeed': True})
    except Exception as e:
        print(str(e), file=sys.stderr)
        return json.dumps({'succeed': False, "error": str(e)})

@app.route('/ad/product/load_spec')
def product_loadSpec():
    connection = get_conn_1()
    try:
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT * FROM product_specs WHERE product_id = %s" % request.args.get('product_id'))
            connection.close()
            return json.dumps(cursor.fetchall(), ensure_ascii=False)
    except Exception as e:
        print(str(e), file=sys.stderr)
        return json.dumps({'succeed': False, "error": str(e)})
@app.route('/ad/product/set_spec',methods=['POST'])
def product_setSpec():
    connection = get_conn()
    try:
        with connection.cursor() as cursor:
            productSpecs = json.loads(request.form['specs'])
            productId = request.form['product_id']
            cursor.execute("SELECT * FROM product_specs WHERE product_id = %s" % productId)
            if cursor.rowcount > 0:
                cursor.execute("DELETE FROM product_specs WHERE product_id = %s" % productId)
                connection.commit()
            for spec in productSpecs:
                cursor.execute("INSERT INTO product_specs(specName,specValue,product_id) VALUES('%s','%s',%s)"
                               % (spec['specName'],spec['specValue'],productId))
            connection.commit()
            connection.close()
            return json.dumps({'succeed': True})
    except Exception as e:
        print(str(e), file=sys.stderr)
        return json.dumps({'succeed': False, "error": str(e)})
@app.route('/ad/product/next', methods=['GET'])
def product_next():
    connection = get_conn()
    try:
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT AUTO_INCREMENT FROM information_schema. tables WHERE table_name = 'products' AND table_schema = DATABASE();")

            connection.close()
            return json.dumps({'productId': cursor.fetchone()[0]})
    except Exception as e:
        print(str(e), file=sys.stderr)
        return json.dumps({'succeed': False, "error": str(e)})

@app.route('/ad/img/setProductID', methods=['GET'])
def img_setProductID():
    connection = get_conn()
    try:
        with connection.cursor() as cursor:
            cursor.execute(
                "UPDATE product_images SET product_id = %s WHERE id = %s" % (request.args.get('product_id'),request.args.get('image_id')))
            connection.commit()
            connection.close()
            return json.dumps({'succeed': True})
    except Exception as e:
        print(str(e), file=sys.stderr)
        return json.dumps({'succeed': False, "error": str(e)})

@app.route('/ad/img/remove', methods=['GET'])
def img_remove():
    connection = get_conn()
    try:
        with connection.cursor() as cursor:
            print(app.config['UPLOAD_FOLDER'] + '/static/img/products/tmp/' + str(request.args.get('prod_id')) + '/' + request.args.get('image_id'))
            if isfile(app.config['UPLOAD_FOLDER'] + '/static/img/products/tmp/' + str(request.args.get('prod_id')) + '/' + request.args.get('image_id')):
                os.remove(app.config['UPLOAD_FOLDER'] + '/static/img/products/tmp/' + str(request.args.get('prod_id')) + '/' + request.args.get('image_id'))
            return json.dumps({'succeed': True})
    except Exception as e:
        print(str(e), file=sys.stderr)
        return json.dumps({'succeed': False, "error": str(e)})

@app.route('/ad/img/setMain', methods=['GET'])
def img_setMain():
    connection = get_conn()
    try:
        with connection.cursor() as cursor:
            #
            # if request.args.get('product_id') != None:
            #     cursor.execute('UPDATE product_images SET is_main = 0 WHERE  product_id = %s AND is_main = 1 ' %request.args.get('product_id'))
            # else:
            #     cursor.execute('UPDATE product_images SET is_main = 0 WHERE  product_id = -1 AND is_main = 1 ')
            # connection.commit()
            # if request.args.get('product_id') != None:
            #     cursor.execute(
            #         "UPDATE product_images SET is_main = 1 WHERE  product_id = %s AND id = %s" % (request.args.get('product_id'),
            #         request.args.get('image_id')))
            # else:
            #     cursor.execute(
            #         "UPDATE product_images SET is_main = 1 WHERE  product_id = -1 AND id = %s" % (request.args.get('image_id')))
            connection.commit()
            connection.close()
            return json.dumps({'succeed': True})
    except Exception as e:
        print(str(e), file=sys.stderr)
        return json.dumps({'succeed': False, "error": str(e)})

@app.route('/ad/img/all')
def img_all():
    connection = get_conn()
    try:
        with connection.cursor() as cursor:
            mypath = app.config['UPLOAD_FOLDER'] + '/static/img/products/tmp/' + str(request.args.get('product_id')) + '/'
            onlyfiles = [f for f in listdir(mypath) if isfile(join(mypath, f))]
            if len(onlyfiles)  > 0:
                print(onlyfiles)
                out_files = []
                for file in onlyfiles:
                    if allowed_file(file):
                        out_files.append(file)
                return json.dumps(out_files)
            else:
                return json.dumps([])
            # if request.args.get('product_id') != None:
            #     cursor.execute('SELECT id,image,extension,is_main FROM product_images WHERE product_id = %s' % request.args.get('product_id'))
            # else:
            #     cursor.execute(
            #         "SELECT id,extension,is_main FROM product_images WHERE product_id = -1")
            images = []
            for data in cursor.fetchall():
                images.append({'id':data[0] ,'extension':data[1].split('/')[1], 'is_main' :bool(data[2]) })
            connection.close()
            return json.dumps(images)
    except Exception as e:
        print(str(e), file=sys.stderr)
        return json.dumps({'succeed': False, "error": str(e)})

def fixImages():
    connection = get_conn()
    try:
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT image,extension,product_id,id FROM product_images")
            if cursor.rowcount > 0:
                data = cursor.fetchall()
                print(len(data))
                for dat in data:
                    if os.path.exists(app.config['UPLOAD_FOLDER'] + '/static/img/products/tmp/' + str(dat[2])) != True:
                        os.mkdir(app.config['UPLOAD_FOLDER'] + '/static/img/products/tmp/' + str(dat[2]))
                    with open(os.path.join(app.config['UPLOAD_FOLDER'] + '/static/img/products/tmp/' + str(dat[2]) + '/',
                                           str(dat[3]) + '.' + dat[1].split('/')[1]), "wb") as f:
                        f.write(base64.b64decode(dat[0]))
                        f.close()
                    cursor.execute("UPDATE products SET main_image = '%s' WHERE id = %s" %
                                   (str(dat[3]) + '.' + dat[1].split('/')[1],dat[2]))
            connection.commit()
            connection.close()
    except Exception as e:
        print(str(e), file=sys.stderr)
        return json.dumps({'succeed': False, "error": str(e)})
@app.route('/ad/img')
def img():
    connection = get_conn()
    try:
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT image,extension FROM product_images WHERE id = %s" % (request.args.get('image_id')))
            if cursor.rowcount > 0:
                data = cursor.fetchone()
                connection.close()
                return 'data:image/%s;base64,%s' % (data[1],data[0])
            return json.dumps({'succeed': True})
    except Exception as e:
        print(str(e), file=sys.stderr)
        return json.dumps({'succeed': False, "error": str(e)})

@app.route('/f32d73dc8d1d.html')
def f32d73dc8d1d():
    return 'a1a24e65907a'

if __name__ == '__main__':
    # getCatData(1)
    # fixImages()
    # from operator import *
    # data = [{'c1': 1, 'c2': 10, 'c3': 4},
    #         {'c1': 1, 'c2': 10, 'c3': 5},
    #         {'c1': 2, 'c2': 20, 'c3': 6},
    #         {'c1': 2, 'c2': 20, 'c3': 7},
    #         ]
    #
    # grouper = itemgetter("c1", "c2")
    # for key, group in itertools.groupby(data, itemgetter("c1", "c2")):
    #     print(key)
    #     print(list(group))
    app.run(host="0.0.0.0",port=5000, debug=True)
