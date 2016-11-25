from flask import *
import os,pymysql,sys,base64,itertools
from werkzeug.utils import secure_filename
app = Flask(__name__)

UPLOAD_FOLDER = app.root_path
ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def flat_to_nest(data, keys):
    """Преобразование "плоских" данных во вложенные
    """
    new_data = []
    for key, group in itertools.groupby(data, lambda x: x[keys[0]]):
        group =  map(lambda x: dict((i, x[i]) for i in x if i != keys[0]), list(group))
        new_data.append( {keys[0]: key,"data":
                          flat_to_nest(group, keys[1:]) if keys[1:] else list(group)} )
    return new_data
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

def get_conn():
    return pymysql.connect(host='127.0.0.1',
                             user='root',
                             password='jmXQF97JqkeNxV5B%',
                             db='appleshop54',
                             charset='utf8')
def get_conn_1():
    return pymysql.connect(host='127.0.0.1',
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
    return render_template('index.html',body=render_template('main.html'))

@app.route('/контакты')
def contacts():
    return render_template('index.html',body=render_template('page.html',body=render_template('contacts.html')))

def cat(_id):
    connection = get_conn_1()
    data = None
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT pr.id,pr.type_product , pr. NAME , pr.price ,"
                           "( SELECT image FROM product_images WHERE product_id = pr.id AND is_main = 1) image ,"
                           "( SELECT extension FROM product_images WHERE product_id = pr.id AND is_main = 1) extension FROM products pr WHERE pr.type_product=%s" % _id)
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
            print('price %s' % (str(data)))

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
    ret_data.update({'pr_min':int(data['min'] * 1.7)})
    ret_data.update({'pr_max':int(data['max'] * 0.88)})
    return ret_data

def getCatData(_id):
    connection = get_conn_1()
    data = None
    try:
        with connection.cursor() as cursor:
            cursor.execute('SELECT c.id cid,c.category_name,s.id sid,s.categ_id,s.subcateg_name FROM product_categ c,'
                           'product_subcat s WHERE c.type_id=1 and s.categ_id = c.id ORDER BY cid,sid')
            data = cursor.fetchall()
            print('price %s' % (str(flat_to_nest(data,['cid','sid']))))

            connection.close()
            return flat_to_nest(data,['cid','sid'])
    except Exception as e:
        print(str(e), file=sys.stderr)
        return json.dumps({'succeed': False, "error": str(e)})



@app.route('/каталог/<string:path>/')
@app.route('/каталог/<string:path>')
def catalog_path(path):
    print(path)
    print('catalogue')
    dict_data = { "телефоны-apple" : {"name": "ТЕЛЕФОНЫ APPLE", "name_top": "Телефоны Apple","cat" : 1, 'cat_1_name': 'Гигабайты', 'cat_2_name': 'Цвет'},
             "планшеты": {"name": "ПЛАНШЕТЫ", "name_top": "Планшеты", "cat": 2},
             "smart-часы": {"name": "SMART ЧАСЫ", "name_top": "Smart часы", "cat": 3},
             "чехлы": {"name": "ЧЕХЛЫ", "name_top": "Чехлы", "cat": 4, 'cat_1_name': 'Тип чехла', 'cat_2_name': None},
             "фитнес-браслеты": {"name": "ФИТНЕС БРАСЛЕТЫ", "name_top": "Фитнес браслеты", "cat": 5, 'cat_1_name': 'Производитель', 'cat_2_name': None},
             "защита-экрана": {"name": "ЗАЩИТА ЭКРАНА", "name_top": "Защита экрана", "cat": 6, 'cat_1_name': 'Тип защиты', 'cat_2_name': 'Покрытие'},
             "другие-устройства": {"name": "ДРУГИЕ УСТРОЙСТВА", "name_top": "Другие устройства", "cat": 7, 'cat_1_name': 'Тип устройства','cat_2_name': None},
             "аксессуары": {"name": "АКСЕССУАРЫ", "name_top": "Аксессуары", "cat": 8, 'cat_1_name': 'Тип', 'cat_2_name': 'Семейство','availible':'Зарядные устройства'}}
    return render_template('index.html', body=render_template('page.html', body=render_template('catalog.html',
                                                                                                products=render_template(
                                                                                                    'products.html',
                                                                                                    products=cat(dict_data[path]['cat']),
                                                                                                    types=product_getTypesFixed(),
                                                                                                    _path = path),
                                                                                                name=dict_data[path]['name'],
                                                                                                name_top=dict_data[path]['name_top'],
                                                                                                prices=cat_prices(dict_data[path]['cat']),data=dict_data[path],
                                                                                                cat_data=getCatData(dict_data[path]['cat']))))



@app.route('/каталог/<string:path>/<string:name_cat>/')
@app.route('/каталог/<string:path>/<string:name_cat>')
def catalog_path_name_cat(path,name_cat=None):
    connection = get_conn_1()
    data = None
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT pr.id,pr.type_product , pr. NAME , pr.price ,"
                           "( SELECT image FROM product_images WHERE product_id = pr.id AND is_main = 1) image ,"
                           "( SELECT extension FROM product_images WHERE product_id = pr.id AND is_main = 1) extension FROM products pr WHERE pr.id = %s" % request.args.get(
                'product_id'))
            connection.close()
            data = cursor.fetchone()
    except Exception as e:
        print(str(e), file=sys.stderr)
        return json.dumps({'succeed': False, "error": str(e)})
    return render_template('index.html', body=render_template('page.html', body=render_template('catalog.html',
                                                                                                products=render_template(
                                                                                                    'product_detailed.html',
                                                                                                    product=data),
                                                                                                name=data[
                                                                                                    'NAME'].upper(),
                                                                                                name_top=data[
                                                                                                    'NAME'],
                                                                                                types=product_getTypesFixed())))
@app.route('/каталог')
def catalog():
    connection = get_conn_1()
    data = None
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT pr.id,pr.type_product , pr. NAME , pr.price ,"
                           "( SELECT image FROM product_images WHERE product_id = pr.id AND is_main = 1) image ,"
                           "( SELECT extension FROM product_images WHERE product_id = pr.id AND is_main = 1) extension FROM products pr")
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
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT pr.id,pr.type_product , pr. NAME , pr.price ,"
                           "( SELECT image FROM product_images WHERE product_id = pr.id AND is_main = 1) image ,"
                           "( SELECT extension FROM product_images WHERE product_id = pr.id AND is_main = 1) extension FROM products pr WHERE pr.id = %s" % request.args.get('product_id'))
            connection.close()
            data = cursor.fetchone()
    except Exception as e:
        print(str(e), file=sys.stderr)
        return json.dumps({'succeed': False, "error": str(e)})
    return render_template('index.html', body=render_template('page.html', body=render_template('catalog.html',
                                                                                                products=render_template(
                                                                                                    'product_detailed.html',
                                                                                                    product=data),
                                                                                                name=data['NAME'].upper(),
                                                                                                name_top=data['NAME'],
                                                                                                types=product_getTypesFixed(), prices=cat_prices(-1))))


@app.route('/ad')
def admin():
    connection = get_conn_1()
    data = None
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT pr.id,pr.type_product , pr. NAME , pr.price ,"
                           "( SELECT image FROM product_images WHERE product_id = pr.id AND is_main = 1) image ,"
                           "( SELECT extension FROM product_images WHERE product_id = pr.id AND is_main = 1) extension FROM products pr")
            connection.close()
            data = cursor.fetchall()
            print(data)
    except Exception as e:
        print(str(e), file=sys.stderr)
        return json.dumps({'succeed': False, "error": str(e)})
    return render_template('admin.html',product_list=render_template('product_list.html',products=data))
@app.route('/ad/new')
def admin_new():
    return render_template('admin_new_product.html')


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
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], 'tmp'))
            buffer = None
            with open(os.path.join(app.config['UPLOAD_FOLDER'], 'tmp'),'rb') as file:
                buffer = file.read()
                file.close()
            connection = get_conn()
            try:
                with connection.cursor() as cursor:
                    cursor.execute(
                        "INSERT INTO product_images(image,product_id,is_main,extension) VALUES ('%s',%s,%s,'image/%s')" % (base64.b64encode(buffer).decode('utf8'),-1,0,filename.rsplit('.', 1)[1]))
                    connection.commit()
                    connection.close()
                    return json.dumps({'imgId': cursor.lastrowid})
            except Exception as e:
                print(str(e), file=sys.stderr)
                return json.dumps({'succeed': False, "error": str(e)})
            # file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            return 'good'



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
                               "( SELECT image FROM product_images WHERE product_id = pr.id AND is_main = 1) image ,"
                               "( SELECT extension FROM product_images WHERE product_id = pr.id AND is_main = 1) extension FROM products pr")
            else:
                cursor.execute("SELECT pr.id,pr.type_product , pr. NAME , pr.price ,"
                               "( SELECT image FROM product_images WHERE product_id = pr.id AND is_main = 1) image ,"
                               "( SELECT extension FROM product_images WHERE product_id = pr.id AND is_main = 1) extension FROM products pr WHERE pr.type_product = %s" % (request.args.get('type')))
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
            cursor.execute(
                "INSERT INTO product_colors(color_name) VALUES('%s')" % request.args.get('color_name'))
            connection.commit()
            connection.close()
            return json.dumps(cursor.fetchall(), ensure_ascii=False)
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

@app.route('/ad/product/set_color', methods=['GET'])
def product_setColor():
    connection = get_conn_1()
    try:
        with connection.cursor() as cursor:
            cursor.execute(
                "UPDATE products SET color_id = %s WHERE id = %s" % (request.args.get('color_id'),request.args.get('device_id')))
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
            cursor.execute("INSERT INTO products(type_product,name,price,description) VALUES(%s,'%s',%s,'%s')"
                           %(request.args.get('type_product'),request.args.get('name'),
                             request.args.get('price'),request.args.get('description')))
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
@app.route('/ad/product/set_spec',methods=['POST'])
def product_setSpec():
    connection = get_conn()
    try:
        with connection.cursor() as cursor:
            productSpecs = json.loads(request.form['specs'])
            productId = request.form['product_id']
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
            cursor.execute(
                "DELETE FROM product_images WHERE id = %s" % (request.args.get('image_id')))
            connection.commit()
            connection.close()
            return json.dumps({'succeed': True})
    except Exception as e:
        print(str(e), file=sys.stderr)
        return json.dumps({'succeed': False, "error": str(e)})

@app.route('/ad/img/setMain', methods=['GET'])
def img_setMain():
    connection = get_conn()
    try:
        with connection.cursor() as cursor:
            cursor.execute('UPDATE product_images SET is_main = 0 WHERE  product_id = -1 AND is_main = 1')
            connection.commit()
            cursor.execute(
                "UPDATE product_images SET is_main = 1 WHERE  product_id = -1 AND id = %s" % (request.args.get('image_id')))
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
            cursor.execute(
                "SELECT id,image,extension,is_main FROM product_images WHERE product_id = -1")
            images = []
            for data in cursor.fetchall():
                images.append({'id':data[0] ,'image':('data:image/%s;base64,%s' %(data[2],data[1])), 'is_main' :bool(data[3]) })
            connection.close()
            return json.dumps(images)
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
                return 'data:image/%s;base64,%s' %(data[1],data[0])
            return json.dumps({'succeed': True})
    except Exception as e:
        print(str(e), file=sys.stderr)
        return json.dumps({'succeed': False, "error": str(e)})

@app.route('/f32d73dc8d1d.html')
def f32d73dc8d1d():
    return 'a1a24e65907a'

if __name__ == '__main__':
    getCatData(1)
    app.run(host="0.0.0.0", debug=True)
