from typing import List, Dict
import time
import os
from flask import request, redirect, render_template, make_response
from flask import Flask, render_template, jsonify
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from sqlalchemy.orm import relationship

app = Flask(__name__,
            static_folder = "./dist",
            template_folder = "./dist", static_url_path='') # , root_path="./"
# app = Flask(__name__,
#             static_folder = "./dist/static",
#             template_folder = "./dist", static_url_path='static')
cors = CORS(app, resources={r"/api/*": {"origins": "*"}})

basedir = os.path.abspath(os.path.dirname(__file__))
DB = 'sqlite:///' + os.path.join(basedir, 'pwdb.sqlite')

app.config['SQLALCHEMY_DATABASE_URI'] = DB
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy()
db.init_app(app)

Base = db.Model
class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    name = Column(String(50), unique=True)
    email = Column(String(120), unique=True)

    def __init__(self, name=None, email=None):
        self.name = name
        self.email = email

    def __repr__(self):
        return f'<User {self.name!r}>'

class Todolist(Base):
    __tablename__ = 'todolists'
    id = Column(Integer, primary_key=True)
    title = Column(String(50))
    isDelete = Column(Boolean, default=False)
    locked = Column(Boolean, default=False)
    record = relationship('Todorecord', backref='todolists', lazy='dynamic')

    def to_dict(self):
        KEYS = ('id', "title", "isDelete", "locked")
        dct = {k:v for k, v in self.__dict__.items() if k in KEYS}
        dct["record"] = [r.to_dict() for r in self.record]
        dct["count"] = len(dct["record"])
        return dct

    def from_dict(self, dat:Dict):
        for k, v in dat.items():
            setattr(self, k, v)

class Todorecord(Base):
    __tablename__ = 'todorecords'
    id = Column(Integer, primary_key=True)
    text = Column(String(250))
    isDelete = Column(Boolean, default=False)
    checked = Column(Boolean, default=False)
    index = Column(Integer)
    todo_id = Column(Integer, ForeignKey('todolists.id'))

    def to_dict(self):
        KEYS = ('id', "text", "isDelete", "checked", "index", "todo_id")
        dct = {k:v for k, v in self.__dict__.items() if k in KEYS}
        return dct

    def from_dict(self, dat:Dict):
        for k, v in dat.items():
            if k in ("text", "isDelete", "checked", "index", "todo_id"):
                setattr(self, k, v)

from flask_migrate import Migrate
migrate = Migrate()
migrate.init_app(app, db)


@app.route('/api/random')
def random_number():
    import random
    response = {
        'randomNumber': random.randint(1, 100)
    }
    return jsonify(response)


@app.route('/api/todo/list')
def todo_list():
    tds:List[Todolist] = Todolist.query.order_by(Todolist.id.desc())
    response = {
        'todos': [td.to_dict() for td in tds]
    }
    return jsonify(response)

@app.route('/api/todo/listId')
def todo_id():
    tid = request.args.get('id')
    print(tid)
    todo:Todolist = Todolist.query.filter_by(id=tid).first()
    print(todo)
    if todo:
        response = {
            "todo": todo.to_dict()
        }
        return jsonify(response)
    else:
        return jsonify({"todo":{}}), 404

@app.route('/api/todo/addTodo', methods=["POST"])
def todo_add():
    todo = {
        # "id": id,
        "title": 'newList',
        "isDelete": False,
        "locked": False,
        "record": []
    }
    tsk = Todolist(**todo)
    db.session.add(tsk)
    db.session.commit()
    return jsonify(todo)

@app.route('/api/todo/editTodo', methods=["POST"])
def todo_edit_id():
    td = request.get_json()['todo']
    print(td)
    tid = td["id"]
    todo:Todolist = Todolist.query.filter_by(id=tid).first()
    todo.from_dict(td)
    db.session.add(todo)
    db.session.commit()

    return jsonify({
        "err": 200
    })

@app.route('/api/todo/addRecord', methods=["POST"])
def todo_addRecord():
    td = request.get_json()
    print(td)
    tid = td["id"]
    todo:Todolist = Todolist.query.filter_by(id=tid).first()
    # todo.from_dict(td)
    stodo = {
        "text": td["text"],
        "isDelete": False,
        "checked": False,
        "todo_id": tid
    }
    rec = Todorecord(**stodo)
    db.session.add(rec)
    db.session.commit()
    return jsonify({
        "err": 200
    })

@app.route('/api/todo/editRecord', methods=["POST"])
def todo_editRecord():
    td = request.get_json()
    print("todo_editRecord", td)
    tid = td["id"]
    todo:Todolist = Todolist.query.filter_by(id=tid).first()
    index = td["index"]
    rid = todo.record[index].id 
    rec = Todorecord.query.filter_by(id=rid).first()
    rec.from_dict(td["record"])
    db.session.add(rec)
    db.session.commit()
    return jsonify({
        "err": 200
    })

class FooRunner:
    def __init__(self):
        self.is_running = None
        self.data = []
        self._idx = -1
        self.stop_at = 999999999999999
        self.begin_at = 999999999999999

    def start(self):
        tm = int(time.time())
        self.data = [{"data":i, "timestamp": tm + i} for i in range(30)]
        self.is_running = True
        self.begin_at = tm

    def stop(self):
        self.is_running = False
        self.stop_at = int(time.time())

    def getState(self, idx:int, tm:int):
        i = 0
        for i, d in enumerate(self.data[idx:]):
            if tm < d["timestamp"]:
                break
        idx2 = idx + i + 1
        print(idx, idx2, i, self.data)
        return self.data[idx:idx2]

    # def getRecentState(self):
    #     self._idx += 1
    #     return self._idx, self.data[self._idx]
    
    # def getRunning(self):
    #     return self.is_running
    
    def getRunning(self, ts:int):
        if ts < self.begin_at:
            # self.stop_at:
            return None
        elif ts < self.stop_at:
            # return self.is_running
            return True
        else:
            return False

foo = FooRunner()

@app.route('/api/tmp_run/start', methods=['POST'])
def tmp_start():
    tm = int(time.time())
    foo.start()
    return jsonify({"errCode": 0, "timestamp": tm})

@app.route('/api/tmp_run/stop', methods=['POST'])
def tmp_stop():
    foo.stop()
    tm = int(time.time())
    return jsonify({"errCode": 0, "timestamp": tm})

@app.route('/api/tmp_run/recent_state')
def tmp_query_recent():
    idx, val = foo.getRecentState()
    dct = {"state": val}
    return jsonify(dct)

@app.route('/api/tmp_run/get_state')
def tmp_query():
    tm = int(time.time())
    timestamp = int(request.args.get("timestamp", tm))
    timestamp = min([timestamp, tm])
    idx = int(request.args.get("offset", 0))
    dct = {"state": foo.getState(idx, timestamp), 'offset': idx, "timestamp": timestamp}
    return jsonify(dct)

@app.route('/api/tmp_run/is_running')
def train_isrunning():
    tm = int(time.time())
    timestamp = int(request.args.get("timestamp", tm))
    timestamp = min([timestamp, tm])
    # new Date(Math.floor(Date.now()/100)*100)
    dct = {"is_running": foo.getRunning(timestamp), "timestamp": timestamp}
    return jsonify(dct)

# 主页面
@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html')

@app.errorhandler(403)
def forbidden(e):
    return make_response(render_template('index.html'), 403)
    # return redirect('/#403', code=403)
    # return render_template('403.html'), 403

@app.errorhandler(404)
def page_not_found(e):
    # note that we set the 404 status explicitly
    return make_response(render_template('index.html'), 404)
    # return redirect('/#404', code=404)
    # return render_template('404.html'), 404

@app.errorhandler(500)
def internal_server_error(e):
    return make_response(render_template('index.html'), 500)
    return redirect('/#500', code=500)
    # return render_template('500.html'), 500

if __name__ == "__main__":
    app.run(port=5001)