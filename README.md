工作中常用python程序的总结。


1: send_mail.py --- 发送文本，html，带附件的邮件;

2: libpycurl.py --- 使用 pycurl 库，完成 https 的get post请求，并上传/下载文件到 ftp.

3: singleton.py --- 单例模式的实现

4: libcsv.py --- 使用csv库，读取/写入 csv 文件

5: libpostgresql.py  ---  postgresql 基础的操作

6: libscheduler.py   ---  APScheduler

7: regular_expression.py  ---  正则表达式匹配字符

8: tornado_server.py  ---  使用tornado进行访问数据库性能测试<环境python3.7>；分别使用同步方式、异步方式、异步数据库pool、uvloop测试。

    测试结果：同步方式：大约100QPS； [异步方式使用默认的asyncio]异步方式：150-250QPS； 异步数据库pool：400-500QPS； uvloop数据库pool：500-600QPS  

9: tornado-websocket --- 一个简单的 tornado 的web socket程序
