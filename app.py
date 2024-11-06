from typing import List, Dict
import time
import os
import math
from flask import request, redirect, render_template, make_response
from flask import Flask, render_template, jsonify, send_file
from flask_cors import CORS
from flask import Blueprint
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, SmallInteger, DateTime
from sqlalchemy.orm import relationship
import datetime as dt
from cmdHelper import PopWrap, PopWrapMgr, readFileContent, genCmdline
from config_misc import MyConfigWrap, getLogger
from zmcHelper import ZmcRunner, FooRunner

pfn = os.path.join(os.path.dirname(os.path.abspath(__file__)), "vanager.ini")

conf = MyConfigWrap(pfn)
LOG_FILE = conf.get('default','log_file')
RUNLOG_FILE = conf.get('default','name') + "_%s.log"
logger = getLogger(__name__, log_file=LOG_FILE)
basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'hard to guess string'
    FLASKY_MAIL_SUBJECT_PREFIX = '[Flasky]'
    FLASKY_MAIL_SENDER = 'Flasky Admin <flasky@example.com>'
    FLASKY_ADMIN = os.environ.get('FLASKY_ADMIN')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('DEV_DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'vanager.sqlite')

    @staticmethod
    def init_app(app):
        pass

db = SQLAlchemy()
v_bp = Blueprint("bleloc", __name__, url_prefix="/bleloc")
rl_bp = Blueprint("runlog", __name__, url_prefix="/runlog")
bp = Blueprint("public", __name__)
cors = CORS(resources={r"/api/*": {"origins": "*"}, r"/runlog/*": {"origins": "*"}})

g_popMgr = PopWrapMgr()

def create_app():
    import logging
    # root_path="./"
    app = Flask(__name__,
            static_folder = "./dist",
            template_folder = "./dist", static_url_path='')
    app.config.from_object(Config)
    # config[config_name].init_app(app)

    app.logger = logger
    app.logger.info('vanager app begin')

    db.init_app(app)
    cors.init_app(app)
    app.register_blueprint(bp) 
    app.register_blueprint(v_bp) 
    app.register_blueprint(rl_bp) 

    # from flask_migrate import Migrate
    # migrate = Migrate()
    # migrate.init_app(app, db)
    return app


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


class CmdTask(Base):
    __tablename__ = 'cmd_task' 
    id = Column(Integer, primary_key=True)
    name = Column(String(60))
    pid = Column(Integer, default=0)
    returncode = Column(SmallInteger, nullable=True)
    status = Column(SmallInteger, nullable=True)
    cmdline = Column(String(512))
    outfile = Column(String(512))
    cwd = Column(String(512))
    # created_at = db.Column(db.TIMESTAMP, default=get_now_timestamp)
    created_at = Column(DateTime, nullable=False, default=dt.datetime.now)
    destroy_at = Column(DateTime, nullable=True)                           
    
    def __repr__(self):
        return '<Account %s %s>' % (self.id, self.name)

    def to_dict(self):
        KEYS = ('id', "name", "pid", "cmdline", "outfile", "cwd", "returncode", "status")
        return {k: v for k, v in self.__dict__.items() if k in KEYS}

    def from_dict(self, dat):
        for k, v in dat.items():
            if k != 'id':
                setattr(self, k, v)

def updateReturncode(popw, rlog:CmdTask):
    rlog.returncode = popw._returncode
    rlog.status = popw._stat
    rlog.destroy_at = dt.datetime.now()
    db.session.add(rlog)
    db.session.commit()

@bp.route('/hello')
def say_hello():
    return 'hello'

@bp.route('/api/random')
def random_number():
    import random
    response = {
        'randomNumber': random.randint(1, 100)
    }
    return jsonify(response)


@bp.route('/api/todo/list')
def todo_list():
    tds:List[Todolist] = Todolist.query.order_by(Todolist.id.desc())
    response = {
        'todos': [td.to_dict() for td in tds]
    }
    return jsonify(response)

@bp.route('/api/todo/listId')
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

@bp.route('/api/todo/addTodo', methods=["POST"])
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

@bp.route('/api/todo/editTodo', methods=["POST"])
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

@bp.route('/api/todo/addRecord', methods=["POST"])
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

@bp.route('/api/todo/editRecord', methods=["POST"])
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


foo = FooRunner()


@bp.route('/api/tmp_run/start', methods=['POST'])
def tmp_start():
    tm = int(time.time())
    foo.start()
    return jsonify({"errCode": 0, "timestamp": tm})

@bp.route('/api/tmp_run/stop', methods=['POST'])
def tmp_stop():
    foo.stop()
    tm = int(time.time())
    return jsonify({"errCode": 0, "timestamp": tm})

@bp.route('/api/tmp_run/recent_state')
def tmp_query_recent():
    idx, val = foo.getRecentState()
    dct = {"state": val}
    return jsonify(dct)

@bp.route('/api/tmp_run/get_state')
def tmp_query():
    tm = int(time.time())
    timestamp = int(request.args.get("timestamp", tm))
    timestamp = min([timestamp, tm])
    idx = int(request.args.get("offset", 0))
    cnt = foo.getState(idx, timestamp)
    next_ofs = idx + len(cnt)
    dct = {"state": cnt, 'offset': idx, 'next_ofs': next_ofs, "timestamp": timestamp}
    return jsonify(dct)

@bp.route('/api/tmp_run/is_running')
def tmp_isrunning():
    tm = int(time.time())
    timestamp = int(request.args.get("timestamp", tm))
    timestamp = min([timestamp, tm])
    # new Date(Math.floor(Date.now()/100)*100)
    dct = {"is_running": foo.getRunning(timestamp), "timestamp": timestamp, 'tmp_ts': foo.stop_at}
    return jsonify(dct)


zmcWrp = ZmcRunner()
    
@bp.route('/api/zmcrun/start', methods=['POST'])
def zmc_start():
    tm = int(time.time())
    zmcWrp.add_cmd()
    return jsonify({"errCode": 0, "timestamp": tm})

@bp.route('/api/zmcrun/stop', methods=['POST'])
def zmc_stop():
    # zmcWrp.stop()
    tm = int(time.time())
    return jsonify({"errCode": 0, "timestamp": tm})

@bp.route('/api/zmcrun/get_state')
def zmc_query():
    tm = int(time.time())
    timestamp = int(request.args.get("timestamp", tm))
    timestamp = min([timestamp, tm])
    idx = int(request.args.get("offset", 0))
    cnt = zmcWrp.getState(idx, timestamp)
    # next_ofs = idx + len(cnt)
    dct = {"state": cnt, 'offset': idx, 'next_ofs': cnt["next_ofs"], "timestamp": timestamp}
    return jsonify(dct)

@bp.route('/api/zmcrun/is_running')
def zmc_isrunning():
    tm = int(time.time())
    timestamp = int(request.args.get("timestamp", tm))
    timestamp = min([timestamp, tm])
    # new Date(Math.floor(Date.now()/100)*100)
    dct = {"is_running": zmcWrp.getRunning(timestamp), "timestamp": timestamp, 'tmp_ts': foo.stop_at}
    return jsonify(dct)

# 主页面
@bp.route('/')
@bp.route('/index')
def index():
    return render_template('index.html')

@bp.errorhandler(403)
def forbidden(e):
    return make_response(render_template('index.html'), 403)
    # return redirect('/#403', code=403)
    # return render_template('403.html'), 403

@bp.errorhandler(404)
def page_not_found(e):
    # note that we set the 404 status explicitly
    return make_response(render_template('index.html'), 404)
    # return redirect('/#404', code=404)
    # return render_template('404.html'), 404

@bp.errorhandler(500)
def internal_server_error(e):
    return make_response(render_template('index.html'), 500)
    return redirect('/#500', code=500)
    # return render_template('500.html'), 500


@rl_bp.route('/api/start', methods=['POST'])
def train():
    args = request.get_json()
    logger.info(args)
    cmd = args.get("cmds", "ping localhost")
    cwd = args.get("cwd", None)
    shell = args.get("shell", False)
    cmdTmpl = args.get("cmdTmpl")
    useCmdTmpl = args.get("useCmdTmpl")
    
    params = { "appDirPath": os.path.dirname(__file__)}
    params.update(args)
    if useCmdTmpl:
        cmds = genCmdline(cmdTmpl, params)
    else:
        cmds = cmd
    logger.info(cmds)
    ts = dt.datetime.timestamp(dt.datetime.now())
    fn = RUNLOG_FILE % ts

    g_pop = PopWrap.genByCmdline(cmds, outfile=fn, cwd=cwd, shell=shell) # 
    rlog = CmdTask(cmdline=cmds, outfile=fn, cwd=cwd, status=g_pop._stat)
    dct = {"cmd": cmds, "cwd": cwd, "timestamp": ts}
    if not g_pop.is_running(): 
        rlog.returncode = 1
        rlog.status = g_pop._stat
        rlog.destroy_at = dt.datetime.now()
        dct.update({"returncode": 1, "status": g_pop._stat})
    else:
        rlog.pid = g_pop._pop.pid
    db.session.add(rlog)
    db.session.commit()
    g_popMgr.put(rlog.id, g_pop)
    dct.update({"is_running": g_pop.is_running(), "id":rlog.id})
    return jsonify(dct)

@rl_bp.route('/api/stop', methods=['PUT'])
def cmdtask_stop_api_2():
    args = request.get_json()
    id = int(args.get("id", 0))
    return _cmdtask_stop_api(id)

@rl_bp.route('/api/<int:id>/stop', methods=['PUT'])
def cmdtask_stop_api(id):
    return _cmdtask_stop_api(id)

def _cmdtask_stop_api(id):
    ts = dt.datetime.timestamp(dt.datetime.now())
    rlog = CmdTask.query.filter_by(id=id).first()
    if not rlog:
        return jsonify({"errCode": 404, "errorMessage": 'not found'})
    g_pop = g_popMgr.get(id)
    stat = g_pop._stat
    ret = g_pop.kill_popen()
    logger.info(ret)    
    if stat != ret:
        updateReturncode(g_pop, rlog)
    return jsonify({"timestamp": ts, "is_running": g_pop.is_running(), "returncode": g_pop._returncode, "popstat": g_pop._stat})

@rl_bp.route('/api/list_id')
def get_cmdtask_id_api():
    id = int(request.args.get('id', 0))
    rlog = CmdTask.query.filter_by(id=id).first()
    if not rlog:
        return jsonify({"errCode": 404, "errorMessage": 'not found'})
    else:
        return jsonify(rlog.to_dict())

@rl_bp.route('/api/<int:id>/returncode')
@rl_bp.route('/api/<int:id>/is_running')
def runlog_isrunning(id):
    rlog = CmdTask.query.filter_by(id=id).first()
    if not rlog:
        return jsonify({"errCode": 404, "errorMessage": 'not found'})
    g_pop = g_popMgr.get(id)
    if g_pop.checkIsRunning():
        updateReturncode(g_pop, rlog)
    dct = {"is_running": g_pop.is_running(), "returncode": g_pop._returncode, "popstat": g_pop._stat}
    return jsonify(dct)

@rl_bp.route('/api/recent/returncode')
@rl_bp.route('/api/recent/is_running')
def runlog_recent_isrunning():
    rlog = CmdTask.query.order_by(CmdTask.id.desc()).first()
    if not rlog:
        return jsonify({"errCode": 404, "errorMessage": 'not found'})
    g_pop = g_popMgr.get(id)
    if g_pop.checkIsRunning():
        updateReturncode(g_pop, rlog)
    dct = {"is_running": g_pop.is_running(), "returncode": g_pop._returncode, "popstat": g_pop._stat, "id":rlog.id}
    return jsonify(dct)


@rl_bp.route('/api/<int:id>/stdout/read')
def train_stdout_read(id):
    rlog = CmdTask.query.filter_by(id=id).first()
    if not rlog:
        return jsonify({"errCode": 404, "errorMessage": 'not found'})
    g_pop = g_popMgr.get(id)
    offset = int(request.args.get('offset', 0))
    size = request.args.get('size', 65535, type=int)
    cnt = b''
    if not g_pop._outfile: return b''
    with open(g_pop._outfile, 'rb') as fp:
        fp.seek(offset, 0)
        cnt = fp.read(size)
    return cnt

@rl_bp.route('/api/<int:id>/stdout/file')
def train_stdout_file(id):
    rlog = CmdTask.query.filter_by(id=id).first()
    if not rlog:
        return jsonify({"errCode": 404, "errorMessage": 'not found'})
    g_pop = g_popMgr.get(id)
    offset = int(request.args.get('offset', 0))
    filename = request.args.get('filename', 'file.txt')
    if not g_pop._outfile: return b''
    fp = open(g_pop._outfile, 'rb')
    fp.seek(offset, 1)
    return send_file(fp, attachment_filename=filename)


@rl_bp.route('/api/<int:id>/stdout/readlines')
def train_stdout_readlines(id):
    rlog = CmdTask.query.filter_by(id=id).first()
    if not rlog:
        return jsonify({"errCode": 404, "errorMessage": 'not found'})
    g_pop = g_popMgr.get(id)
    offset = int(request.args.get('offset', 0))
    cnt = [b'']
    if not g_pop._outfile: return b''
    with open(g_pop._outfile, 'rb') as fp:
        fp.seek(offset, 0)
        cnt = fp.readlines()
    # FIXME error ?
    return cnt

@rl_bp.route('/api/<int:id>/stdout')
@rl_bp.route('/api/<int:id>/stdout/json')
def train_stdout(id):
    rlog = CmdTask.query.filter_by(id=id).first()
    if not rlog:
        return jsonify({"errCode": 404, "errorMessage": 'not found'})
    g_pop = g_popMgr.get(id)
    offset = int(request.args.get('offset', 0))
    limit = int(request.args.get('limit', -1))
    is_byte = bool(request.args.get('is_byte', False))
    is_line = request.args.get('is_line', True, type=bool) 
    if not g_pop._outfile: return b''
    dct = readFileContent(g_pop._outfile, offset=offset, limit=limit, is_byte=False, use_line=is_line)
    return jsonify(dct)
    # TypeError: Object of type 'bytes' is not JSON serializable

@rl_bp.route('/api/data')
def get_cmdtask_data_api():
    id = int(request.args.get('id', 0))
    return _get_cmdtask_data_api(id, request)

@rl_bp.route('/api/<int:id>/data')
def get_cmdtask_data_api_2(id):
    return _get_cmdtask_data_api(id, request)

def _get_cmdtask_data_api(id, request):
    offset = int(request.args.get('offset', 0))
    limit = int(request.args.get('limit', 0))
    encoding = request.args.get('encoding', 'utf8')
    filename = request.args.get('filename')
    rlog = CmdTask.query.filter_by(id=id).first()
    if not rlog:
        return jsonify({"errCode": 404, "errorMessage": 'not found'})
    g_pop = g_popMgr.get(id)
    if g_pop.checkIsRunning():
        updateReturncode(g_pop, rlog)
    dct = {"is_running": g_pop.is_running(), "returncode": g_pop._returncode, "errCode": 0}
    if filename: fn = filename
    else: 
        fn = g_pop._outfile 
    if not fn: 
        fn = rlog.outfile
    if not fn:
        dct.update({"errCode": 1})
        return jsonify(dct)
    if not os.path.exists(fn): 
        dct.update({"errCode": 2})
        return jsonify(dct)
    dct["filename"] = fn
    rdf = readFileContent(fn, offset=offset, limit=limit, is_byte=False, use_line=True, encoding=encoding)
    rdf["is_covered"] = not dct["is_running"] # rdf["offset"] == rdf["ends"] and 
    dct["data"] = rdf
    return jsonify(dct)

@rl_bp.route('/api/watchfile')
def get_watchfile():
    offset = int(request.args.get('offset', 0))
    limit = int(request.args.get('limit', -1))
    is_byte = bool(request.args.get('is_byte', False))
    is_line = request.args.get('is_line', True, type=bool) 
    filename = request.args.get('filename')
    if not filename: return b''
    dct = readFileContent(filename, offset=offset, limit=limit, is_byte=False, use_line=is_line)
    dct["filename"] = filename
    return jsonify(dct)


def initDb(dbPath:str):
    if os.path.exists(dbPath):
        return 
    print("initDb", dbPath)
    from sqlalchemy import create_engine
    engine = create_engine(dbPath)
    db.Model.metadata.create_all(engine, checkfirst=True)

def parse_args(cmds=None):
    import argparse
    parser = argparse.ArgumentParser(description='bleloc server')
    parser.add_argument('--port', '-p', type=int, default=5000, help='server port')
    parser.add_argument('--no-debug', action='store_true', help='not use debug mode')
    parser.add_argument('--host', help='host')
    parser.add_argument('--init-db', action='store_true', help='init database')
    return parser.parse_args(cmds)

if __name__ == '__main__':
    app = create_app()
    args = parse_args()
    if args.init_db:
        initDb(Config.SQLALCHEMY_DATABASE_URI)
    app.run(host=args.host, debug=not args.no_debug, port=args.port)
