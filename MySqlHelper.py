import pymysql
from typing import List, Dict, Union, Optional, Any

class MySqlHelper:
    def __init__(self,host:str,user:str,password:str,database:str,port:int=3306,charset: str = 'utf8mb4'):
        """
        初始化数据库连接<br>
        :param host: 主机地址<br>
        :param user: 用户名<br>
        :param password: 密码<br>
        :param database: 数据库名<br>
        :param port: 端口号，默认3306<br>
        :param charset: 字符集，默认utf8mb4
        """
        self.conn_params = {
            'host': host,
            'user': user,
            'password': password,
            'database': database,
            'port': port,
            'charset': charset,
            'cursorclass': pymysql.cursors.DictCursor  # 返回字典形式的结果
        }
        self.connection = None

    def __enter__(self):
        """支持with上下文管理"""
        self.connect() # 创建类的时候会直接连接
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """退出上下文时自动关闭连接"""
        self.close()
    
    def connect(self):
        """连接数据库"""
        try:
            self.connection = pymysql.connect(**self.conn_params)  # 连接数据库
        except pymysql.Error as e:
            raise ConnectionError(f"数据库连接失败: {str(e)}")
        
    def close(self):
        """关闭数据库连接"""
        if self.connection and self.connection.open:
            self.connection.close()
    
    def execute_query(self, sql: str, params: Optional[Union[tuple, dict]] = None) -> List[Dict[str, Any]]:
        """
        执行查询操作，返回多条记录
        :param sql: SQL语句，可以使用%s占位符
        :param params: 参数，可以是元组或字典
        :return: 查询结果列表，每个元素是字段名到值的字典
        """
        try:
            with self.connection.cursor() as cursor:
                cursor.execute(sql, params)
                return cursor.fetchall()
        except pymysql.Error as e:
            raise RuntimeError(f"查询执行失败: {str(e)}")

    def execute_single(self, sql: str, params: Optional[Union[tuple, dict]] = None) -> Optional[Dict[str, Any]]:
        """
        执行查询操作，返回单条记录
        :param sql: SQL语句
        :param params: 参数
        :return: 单条记录字典或None
        """
        try:
            with self.connection.cursor() as cursor:
                cursor.execute(sql, params)
                return cursor.fetchone()
        except pymysql.Error as e:
            raise RuntimeError(f"查询执行失败: {str(e)}")


    def execute_update(self, sql: str, params: Optional[Union[tuple, dict]] = None) -> int:
        """
        执行INSERT/UPDATE/DELETE操作
        :param sql: SQL语句
        :param params: 参数
        :return: 受影响的行数
        """
        try:
            with self.connection.cursor() as cursor:
                affected_rows = cursor.execute(sql, params)
                self.connection.commit()
                return affected_rows
        except pymysql.Error as e:
            self.connection.rollback()
            raise RuntimeError(f"更新操作失败: {str(e)}")

    def execute_many(self, sql: str, params_list: List[Union[tuple, dict]]) -> int:
        """
        批量执行相同SQL语句
        :param sql: SQL语句
        :param params_list: 参数列表
        :return: 受影响的总行数
        """
        try:
            with self.connection.cursor() as cursor:
                affected_rows = cursor.executemany(sql, params_list)
                self.connection.commit()
                return affected_rows
        except pymysql.Error as e:
            self.connection.rollback()
            raise RuntimeError(f"批量操作失败: {str(e)}")

    def execute_quick(self, Select:list, From:list, Where:str=None, Group:list=None, Having:str=None, Order:dict=None):
        """
        可以不写SQL语句,快速查找需要的数据,不支持太复杂的逻辑<br>
        Select:传入需要查询的字段的列表,以字符串形式传入<br>
        From:传入涉及到的表<br>
        Where:给出查询条件,字符串形式传入<br>
        Group:聚合的字段<br>
        Having:聚合的条件<br>
        Order:顺序,用字典传入,key表示字段,value表示按照该字段顺序还是逆序排列,顺序为“ASC”,逆序为“DESC”
        """  
        sql = "SELECT "
        for i in Select:
            sql += f'{i},'
        sql = sql.strip(',')
        sql += " FROM "
        for i in From:
            sql += f'{i},'
        sql = sql.strip(',')
        if Where!=None:
            sql += f' WHERE {Where}'
        if Group!=None:
            sql += " Group BY "
            for i in Group:
                sql += f'{i},'
            sql = sql.strip(',')
            sql += f' HAVING {Having} '
        
        if Order!=None:
            sql += " ORDER BY "
            for k,v in Order.items():
                sql += f'{k} {v},'
            sql = sql.strip(',')

        print(f'sql:{sql}')
        result = self.execute_query(sql)
        return result
        

    def get_table_columns(self, table_name: str) -> List[str]:
        """
        获取表的列名列表
        :param table_name: 表名
        :return: 列名列表
        """
        sql = f"DESCRIBE {table_name}"
        result = self.execute_query(sql)
        return [column['Field'] for column in result]
    
    def table_exists(self, table_name: str) -> bool:
        """
        检查表是否存在
        :param table_name: 表名
        :return: 是否存在
        """
        sql = "SHOW TABLES LIKE %s"
        result = self.execute_single(sql, (table_name,))
        return result is not None
    


if __name__=="__main__":
    db = MySqlHelper(
        host="localhost",
        user='root',
        password="",
        database="Student_Information",
    )

    db.connect()

    # 正确示例 - 插入多行数据
    sql = "INSERT INTO Student (studentName, studentNo, height) VALUES (%s, %s, %s)"
    params_list = [
    ('张三', '0000000001', 175.6),
    ('李四', '0000000002', 180),
    ('王五', '0000000003', 169)
    ]
    count = db.execute_many(sql, params_list)

    sql = "SELECT studentName, height FROM Student WHERE height<170 "
    res = db.execute_query(sql)
    print(res)

    res = db.execute_quick(['studentName','height'],['Student'],"height>170",Order={'height':'DESC'})
    print(res)

