from flask import *
import os,pymysql,sys,base64
from werkzeug.utils import secure_filename
app = Flask(__name__)

UPLOAD_FOLDER = app.root_path
ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
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
@app.route('/')
def main():
    return render_template('index.html',body=render_template('main.html'))

@app.route('/contacts')
def contacts():
    return render_template('index.html',body=render_template('page.html',body=render_template('contacts.html')))

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
    app.run(host="0.0.0.0", debug=True)
