# backendDp

### 目录结构

```
|-- baseDp		差分隐私查询App
|		|-- views.py       接受前端的查询请求,返回真实值和隐私值
|-- charts		绘图App
|		|-- views.py       接受前端的查询请求,返回绘图所需要的数据
|-- config		Django基础配置
|		|-- urls.py        配置Django路由表
|-- data		前端数据文件暂存处
|-- dpDecisionMaker   差分隐私决策APP
|		|-- views.py       接受前端的查询请求,返回满足要求的隐私预算
|-- fileReceiver 文件读取App
|		|-- views.py       接受前端的上传文件(数据库)请求
|-- HOPs		HOP(Hypothetical outcome plots) APP
|		|-- views.py       接受前端的查询请求,返回噪声数组
|-- tools		工具包
|		|-- df_processor.py				dataframe统计类
|		|-- init_mech_instance.py		机制初始化统一接口
|		|-- Laplace.py					Laplace类
|		|-- sensitivity.py				敏感度计算函数
|		|-- StatistucsWithPrivacy.py	返回带有噪声的隐私保护
|		|-- utils.py					常用函数
|-- requirements.txt 环境依赖模块
|-- test.py 测试文件
```

### 运行

```
python manage.py runserver 0.0.0.0:8000
```

