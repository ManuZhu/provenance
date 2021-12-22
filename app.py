# -*- coding: utf-8 -*-
import tensorflow.keras
from flask import Flask, flash, request, render_template, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from flask_bootstrap import Bootstrap
from flask_wtf import FlaskForm, CSRFProtect
from wtforms.validators import DataRequired, Length
from wtforms.fields import *

import myModel
import asyncio
import subprocess
import websockets
import numpy as np
from Spade import *
from myCharts import *
import lstm_fc_gan
import process_data
import os, sys, time, math, shutil, threading, datetime, random

app = Flask(__name__)
app.secret_key = 'dev'

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(app.root_path, 'isid.db')

# set default button sytle and size, will be overwritten by macro parameters
app.config['BOOTSTRAP_BTN_STYLE'] = 'primary'
app.config['BOOTSTRAP_BTN_SIZE'] = 'sm'
# app.config['BOOTSTRAP_BOOTSWATCH_THEME'] = 'lumen'  # uncomment this line to test bootswatch theme

# set default icon title of table actions
app.config['BOOTSTRAP_TABLE_VIEW_TITLE'] = 'Read'
app.config['BOOTSTRAP_TABLE_EDIT_TITLE'] = 'Update'
app.config['BOOTSTRAP_TABLE_DELETE_TITLE'] = 'Remove'
app.config['BOOTSTRAP_TABLE_NEW_TITLE'] = 'Create'

pre_num = 0
all_num = 0
intrusion = 0
x_vol = None
model_a = None
moedl_b = None
db = SQLAlchemy(app)
csrf = CSRFProtect(app)
bootstrap = Bootstrap(app)


def build_server():
    new_loop = asyncio.new_event_loop()
    asyncio.set_event_loop(new_loop)
    start_server = websockets.serve(main_logic, "localhost", 5678)
    asyncio.get_event_loop().run_until_complete(start_server)
    asyncio.get_event_loop().run_forever()


t = threading.Thread(target=build_server, args=())
t.start()

os.remove("my.log")
f = open("my.log", mode="w+")
f.close()


class filenameForm(FlaskForm):
    filename = StringField('文件名', validators=[DataRequired(), Length(1, 20)])
    category = StringField('模型类型', validators=[DataRequired(), Length(1, 20)])
    submit = SubmitField()


class fileForm(FlaskForm):
    filename = StringField('文件名', validators=[DataRequired(), Length(1, 20)])
    dot = FileField()
    attribute = FileField()
    relation = FileField()
    submit = SubmitField()


class GAN(FlaskForm):
    vector = FileField()
    filename = StringField('存储位置', validators=[DataRequired(), Length(1, 20)])
    submit = SubmitField()


class submitForm(FlaskForm):
    submit = SubmitField()


class Model(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.Text, nullable=False)
    owner = db.Column(db.String(100), nullable=False)
    category = db.Column(db.String(100), nullable=False)
    path = db.Column(db.String(100), nullable=False)
    update_at = db.Column(db.DateTime, default=datetime.datetime.now, onupdate=datetime.datetime.now)


class Graph(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.Text, nullable=False)
    owner = db.Column(db.String(100), nullable=False)
    category = db.Column(db.String(100), nullable=False)
    path = db.Column(db.String(100), nullable=False)
    upload_at = db.Column(db.DateTime, default=datetime.datetime.now)


@app.route('/')
def index():
    return render_template('index.html')


@app.route("/get_importance")
def get_node_importance():
    return origin_provenance_with_SI().dump_options_with_quotes()


@app.route('/importance')
def node_importance():
    return render_template('importance.html')


@app.route("/get_classify")
def get_node_classify():
    return provenance_with_label().dump_options_with_quotes()


@app.route('/classify')
def node_classify():
    return render_template('classify.html')


@app.route('/get_center')
def get_node_center():
    return provenance_with_center_node().dump_options_with_quotes()


@app.route('/center')
def node_center():
    return render_template('center.html')


@app.route('/get_vector')
def get_node_vector():
    return provenance_to_vector().dump_options_with_quotes()


@app.route('/vector')
def node_vector():
    return render_template('vector.html')


@app.route('/get_loss')
def get_node_loss():
    return loss_log().dump_options_with_quotes()


@app.route('/loss')
def node_loss():
    return render_template('loss.html')


@app.route('/graph')
def graph():
    page = request.args.get('page', 1, type=int)
    pagination = Graph.query.paginate(page, per_page=10)
    graphs = pagination.items
    titles = [('id', '#'), ('text', '溯源图名称'), ('owner', '提交者'), ('category', '溯源图来源'), ('path', '存储路径'),
              ('upload_at', '上传时间')]
    return render_template('graph.html', messages=graphs, titles=titles, pagination=pagination)


@app.route('/graph/<graph_id>/delete', methods=['GET', 'POST'])
def delete_graph(graph_id):
    graph = Graph.query.get(graph_id)
    if graph:
        shutil.rmtree(graph.path)
        db.session.delete(graph)
        db.session.commit()
        return f'Graph{graph_id}已经被删除。将返回<a href="/graph">溯源图界面</a>。'
    return f'Graph{graph_id}并不存在因此删除失败。将返回<a href="/graph">溯源图界面</a>。'


@app.route('/graph/<graph_id>/compress', methods=['GET', 'POST'])
def data_compress(graph_id):
    graph = Graph.query.get(graph_id)
    if graph:
        path = graph.path
        filename = graph.text + ".dot"
        pre_size = get_FileSize(graph.path + "/" + filename)
        f = os.popen("java -jar compress.jar " + path + "/" + filename + " " + path + "/" + filename)
        print(f.read())
        now_size = get_FileSize(graph.path + "/" + filename)
        rate = int((1 - now_size / pre_size) * 100)
        return f'Graph{graph_id}压缩成功,压缩率为{rate}%。即将返回<a href="/graph">溯源图界面</a>。'
    return f'Graph{graph_id}并不存在因此压缩失败。即将返回<a href="/graph">溯源图界面</a>。'


def get_FileSize(filePath):
    fsize = os.path.getsize(filePath)
    fsize = fsize/float(1024)
    return round(fsize,2)


@app.route('/graph/<graph_id>/change', methods=['GET', 'POST'])
def data_change(graph_id):
    graph = Graph.query.get(graph_id)
    if graph:
        path = graph.path
        walkFile(path)
        return f'Graph{graph_id}转化成功。将返回<a href="/graph">溯源图界面</a>。'
    return f'Graph{graph_id}并不存在因此转化失败。将返回<a href="/graph">溯源图界面</a>。'


@app.route('/graph/upload', methods=["GET", "POST"])
def upload_graph():
    if request.method == "POST":
        filename = request.form.get('filename')
        dot = request.files.get('dot')
        attribute = request.files.get('attribute')
        relation = request.files.get('relation')

        dirname = "data/" + time.strftime('%Y-%m-%d-%H-%M-%S', time.localtime(time.time())) + "-" + filename
        os.mkdir(dirname)

        if attribute and relation:
            attribute.save(dirname + "/attribute.txt")
            relation.save(dirname + "/relation.txt")
        elif dot:
            dot.save(dirname + "/" + filename + ".dot")

        g = Graph(
            text=filename,
            owner='manu',
            category='SPADE',
            path=dirname
        )
        db.session.add(g)
        db.session.commit()
        return '溯源图上传成功！即将返回<a href="/graph">溯源图界面</a>。'
    return render_template('upload.html', form=fileForm())


@app.route('/graph/<graph_id>/preprocess', methods=['GET', 'POST'])
def preprocess_graph(graph_id):
    graph = Graph.query.get(graph_id)
    t = threading.Thread(target=process_thread, args=(graph.path, ))
    t.start()
    return '溯源图运行成功！即将返回<a href="/graph">溯源图界面</a>。'


@app.route('/preprocess-watching')
def preprocess_watching():
    global pre_num
    if pre_num == 0:
        flash('正在读取attribute.txt和relation.txt并装入分布式数据库中', 'danger')
    elif pre_num == 1:
        flash('正在读取attribute.txt和relation.txt并装入分布式数据库中', 'danger')
        flash('正在计算节点权重', 'warning')
    elif pre_num == 2:
        flash('正在读取attribute.txt和relation.txt并装入分布式数据库中', 'danger')
        flash('正在计算节点权重', 'warning')
        flash('正在进行事件聚类', 'primary')
    elif pre_num == 3:
        flash('正在读取attribute.txt和relation.txt并装入分布式数据库中', 'danger')
        flash('正在计算节点权重', 'warning')
        flash('正在进行事件聚类', 'primary')
        flash('正在进行标签传播', 'info')
    else:
        flash('正在读取attribute.txt和relation.txt并装入分布式数据库中', 'danger')
        flash('正在计算节点权重', 'warning')
        flash('正在进行事件聚类', 'primary')
        flash('正在进行标签传播', 'info')
        flash('样本预处理完成，可以开始模型训练', 'success')

    return render_template('watching.html')


def process_thread(path):
    global pre_num
    pre_num = 0
    f = os.popen("func/databaseInstall " + path)
    print(f.read())
    f.close()
    pre_num = 1
    f = os.popen("func/computeSI " + path)
    print(f.read())
    f.close()
    pre_num = 2
    f = os.popen("func/labelPropagation " + path)
    print(f.read())
    f.close()
    pre_num = 3
    f = os.popen("func/provenanceToVector " + path)
    print(f.read())
    f.close()
    pre_num = 4


@app.route('/model')
def model():
    page = request.args.get('page', 1, type=int)
    pagination = Model.query.paginate(page, per_page=10)
    models = pagination.items
    titles = [('id', '#'), ('text', '模型名称'), ('owner', '创建者'), ('category', '模型类型'), ('path', '存储路径'),
              ('update_at', '更新时间')]
    return render_template('model.html', messages=models, titles=titles, pagination=pagination)


@app.route('/model/<model_id>/delete', methods=['GET', 'POST'])
def delete_model(model_id):
    model = Model.query.get(model_id)
    if model:
        if model.category == 'CNN':
            os.remove(model.path)
        db.session.delete(model)
        db.session.commit()
        return f'Model{model_id}已经被删除。将返回<a href="/model">模型界面</a>。'
    return f'Model{model_id}并不存在因此删除失败。将返回<a href="/model">模型界面</a>。'


@app.route('/model/<model_id>/edit', methods=['GET', 'POST'])
def edit_model(model_id):
    return f'正在编辑Model{model_id}，编辑功能将在未来开放，将返回<a href="/model">模型界面</a>。'


@app.route('/model/upload', methods=["GET", "POST"])
def add_model():
    if request.method == "POST":
        filename = request.form.get('filename')
        category = request.form.get('category')
        m = Model(
            text=filename,
            owner='manu',
            category=category,
            path="model/" + filename + ".h5"
        )
        db.session.add(m)
        db.session.commit()
        if category == 'CNN':
            model = myModel.create()
            model.save(m.path)
        return '模型创建成功！即将返回<a href="/model">模型界面</a>。'
    return render_template('upload.html', form=filenameForm())


@app.route('/model/<model_id>/train', methods=["GET", "POST"])
def train_model(model_id):
    global model_a
    flag = request.args.get('flag')
    if flag == '1':
        model_a = Model.query.get(model_id)
        if model_a.category == 'GAN':
            return gan_train_model()
        page = request.args.get('page', 1, type=int)
        pagination = Graph.query.paginate(page, per_page=10)
        graphs = pagination.items
        titles = [('id', '#'), ('text', '溯源图名称'), ('owner', '提交者'), ('category', '溯源图来源'), ('path', '存储路径'),
                  ('upload_at', '上传时间')]
        return render_template('train.html', messages=graphs, titles=titles, pagination=pagination)

    if flag == '2':
        graph = Graph.query.get(model_id)
        ff = open(graph.path + '/nodeAddress.txt')
        rr = ff.readlines()
        x_train = []
        y_train = []
        for i in range(len(rr)):
            x_train.append(list(map(float, rr[i].split(' ')[:256])))
            y_train.append(list(map(float, rr[i].split(' ')[256:258])))
        ff.close()

        x_train = np.array(x_train)
        y_train = np.array(y_train)
        x_train = x_train.reshape(x_train.shape[0], x_train.shape[1], 1)
        y_train = y_train.reshape((y_train.shape[0], 2))

        model = tensorflow.keras.models.load_model(model_a.path)
        model.fit(x_train, y_train, batch_size=10, epochs=100)
        model.save(model_a.path)
        return '模型训练成功！即将返回<a href="/model">模型界面</a>。'


async def send_msg(websocket):
    log_path = "my.log"
    number = 0
    position = 0
    with open(log_path, mode='r') as f:
        while True:
            line = f.readline().strip()
            if line:
                number += 1
                response_text = f"[number %s] %s" %(number, line)
                await websocket.send(response_text)
            cur_position = f.tell()  # record last time file read position
            if cur_position == position:
                time.sleep(0.1)  # currently no line udpated, wait a while
                continue
            else:
                position = cur_position


async def main_logic(websocket, path):
    await send_msg(websocket)


@app.route('/model/gan_train', methods=["GET", "POST"])
def gan_train_model():
    process_data.main()
    lstm_fc_gan.run()
    dirpath = os.path.join(app.root_path, 'out/flash')
    return send_from_directory(dirpath, path="flashRes_6_5_Random.txt", as_attachment=True)


@app.route('/model/<model_id>/predict', methods=["GET", "POST"])
def predict_model(model_id):
    global model_b, x_vol
    flag = request.args.get('flag')
    if flag == '1':
        model_b = Model.query.get(model_id)
        page = request.args.get('page', 1, type=int)
        pagination = Graph.query.paginate(page, per_page=10)
        graphs = pagination.items
        titles = [('id', '#'), ('text', '溯源图名称'), ('owner', '提交者'), ('category', '溯源图来源'), ('path', '存储路径'),
                  ('upload_at', '上传时间')]
        return render_template('predict.html', messages=graphs, titles=titles, pagination=pagination)

    if flag == '2':
        graph_a = Graph.query.get(model_id)
        ff = open(graph_a.path + '/nodeAddress.txt')
        rr = ff.readlines()
        x_vol = []
        for i in range(len(rr)):
            x_vol.append(list(map(float,rr[i].split(' ')[:256])))
        ff.close()
        x_vol = np.array(x_vol)
        x_vol = x_vol.reshape(x_vol.shape[0], x_vol.shape[1], 1)

        page = request.args.get('page', 1, type=int)
        pagination = Graph.query.paginate(page, per_page=10)
        graphs = pagination.items
        titles = [('id', '#'), ('text', '溯源图名称'), ('owner', '提交者'), ('category', '溯源图来源'), ('path', '存储路径'),
                  ('upload_at', '上传时间')]
        return render_template('test.html', messages=graphs, titles=titles, pagination=pagination)

    if flag == '3':
        graph_b = Graph.query.get(model_id)
        ff = open(graph_b.path + '/nodeAddress.txt')
        rr = ff.readlines()
        x_test = []
        for i in range(len(rr)):
            x_test.append(list(map(float, rr[i].split(' ')[:256])))
        ff.close()
        x_test = np.array(x_test)
        x_test = x_test.reshape(x_test.shape[0], x_test.shape[1], 1)

        model = tensorflow.keras.models.load_model(model_b.path)
        full_connect_layer_model = tensorflow.keras.Model(inputs=model.input, outputs=model.get_layer('full_connect_layer').output)
        full_output_vol = full_connect_layer_model.predict(x_vol)
        full_output_test = full_connect_layer_model.predict(x_test)

        global intrusion, all_num
        all_num = 0
        intrusion = 0
        for i in full_output_test:
            dis = sys.maxsize
            for j in full_output_vol:
                temp = Euclidean(i, j)
                if (temp < dis):
                    dis = temp
            if (dis > 5):  # 设定距离
                intrusion += 1
            all_num += 1
            print(all_num, " ", dis)
        print(all_num)
        print(intrusion)

        return render_template('result.html')


@app.route('/get_result')
def get_train_result():
    global intrusion, all_num
    return train_result(all_num - intrusion, intrusion).dump_options_with_quotes()


def Euclidean(vector1 , vector2):
    npvector1 ,npvector2 = np.array(vector1),np.array(vector2)
    return math.sqrt(((npvector1 - npvector2)**2).sum())


@app.route('/download')
def download_pdf():
    num = random.randint(2, 6)
    dirpath = os.path.join(app.root_path, 'metadata')
    return send_from_directory(dirpath, path="prov-abnormal-00" + str(num) + ".pdf", as_attachment=True)


if __name__ == '__main__':
    app.run(debug=True)