# backendDp

### 目录结构

```
|-- baseDp 差分隐私查询App
|		|-- views.py       接受前端的查询请求,返回真实值和隐私值
|-- config Django基础配置
|		|-- urls.py        配置Django路由表
|-- fileReceiver 文件读取App
|		|-- views.py       接受前端的上传文件(数据库)请求
|-- data 文件存放目录
|-- utils.py 差分隐私工具类
```

### 运行

```
python manage.py runserver 0.0.0.0:8000
```

