# -2025年实习写的代码
收集了2025年实习的时候写的所有代码，主要面向sql和python

## MySqlHelper
简化了python和sql之间的交互
最大的特色是增加了一个快速查询的功能，考虑到我们在python中写sql语句时不会有提示出现，导致书写比较麻烦，增加了一个符合python风格的查询接口
可以通过传入列表或者字符串直接拼接sql语句
### 接口介绍
首先使用MySqlHelper类创建一个对象，执行connect用于连接数据库
```
db = MySqlHelper(
        host="",
        user='',
        password="",
        database="",
    )

    db.connect()
```
然后就可以调用下面的接口:
1. execute_query:执行查询操作，返回多条记录
2. execute_single:执行查询操作，返回单条记录
3. execute_update:执行INSERT/UPDATE/DELETE操作
4. execute_many:批量执行相同SQL语句
5. execute_quick:可以不写SQL语句,快速查找需要的数据,不支持太复杂的逻辑
6. get_table_columns:获取表的列名列表
7. table_exists:检查表是否存在

### 使用案例：（如果想要测试下面的代码，可以使用仓库中的sql文件创建一个学生信息表）
**1. 连接数据库**
```
db = MySqlHelper(
        host="localhost",
        user='root',
        password="",
        database="Student_Information",
    )

    db.connect()
```
**2. 执行批量插入**
```
sql = "INSERT INTO Student (studentName, studentNo, height) VALUES (%s, %s, %s)"
    params_list = [
    ('张三', '0000000001', 175.6),
    ('李四', '0000000002', 180),
    ('王五', '0000000003', 169)
    ]
    count = db.execute_many(sql, params_list)
```
**3. 执行查询**
```
sql = "SELECT studentName, height FROM Student WHERE height<170 "
    res = db.execute_query(sql)
    print(res)
```
**4. 执行简单查询**
```
sql = "SELECT studentName, height FROM Student WHERE height<170 "
    res = db.execute_query(sql)
    print(res)
```

## 豆瓣爬虫
针对豆瓣的爬虫
