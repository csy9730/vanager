# vanager

- update 20230529
- update 20230908


## Project setup
```
npm install
```

### Compiles and hot-reloads for development

编译vue框架，启动node服务器

```
npm run serve
```


```
  App running at:
  - Local:   http://localhost:8081/

```


### Compiles and minifies for production
```
npm run build
```

清空dist文件夹，重新生成dist文件。

### Run your unit tests
```
npm run test:unit
```

### Lints and fixes files
```
npm run lint
```

### Customize configuration
See [Configuration Reference](https://cli.vuejs.org/config/).

## prepare

### vue packages
``` bash
npm i -g @vue/cli

vue create vananager
npm i mockjs axios axios-mock-adapter
npm i less
```

### flask
``` bash

set FLASK_APP=app.py

flask db init && flask db migrate && flask db upgrade

flask run
```

## arch
- 架构
    - 前端 vue ，使用 8081端口
    - 后端 flask ， 使用5000端口
        - mock 开启
        - 路由模式 默认使用 # history 模式，可以使用 正常production模式
- 前端后端交互
    - 前端服务器暴露给用户，前端服务器 和 后端服务器 交互
    - 后端服务器暴露给用户，前端静态打包 

#### 暴露前端服务器 
暴露前端服务器

- 开启后端服务 `flask run`
- 开启前端服务 `npm run serve`
- 访问 http://localhost:8081

#### 后端服务器

- 打包vue生成静态文件 `npm run build`
- 开启后端服务 `flask run`
- 访问 http://localhost:5000

### 功能

#### 流控制
src\views\ZmcQueryView.vue


- /api/zmcrun/start
- /api/zmcrun/stop
- /api/zmcrun/get_state
- /api/zmcrun/is_running


|verb|uri|param|response|description|
|---|---|---|---|---|
|post|/api/zmcrun/start|[{"args": [3,4]}]|{"errCode": 0}|运动开始|
|post|/api/zmcrun/stop |{}|{"errCode": 0}|运动停止|
|get|/api/zmcrun/get_state|offset=0|{"data": [], 'offset': 0, 'next_ofs':100}|获取输出|
|get|/api/zmcrun/is_running|gidx=0|{"is_running": true}|获取状态|



- content 对应文件内容
- lines 对应行列表
- data 对应数据
- frame 

```
content  == stdout 
lines		info state
data		motData stream
```


- zmc
- zmot
- zapi

#### 流控制2
- /api/zmcrun/start       /zmcjson
- /api/zmcrun/stop        /stop
- /api/zmcrun/get_state   /fstream
- /api/zmcrun/is_running  /status


#### 流式接口3

|verb|uri|param|response|description|
|---|---|---|---|---|
|post|/api/zmcrun/start|---|---|运动开始，获取输出|
|post|/api/zmcrun/stop |---|---|运动停止|







