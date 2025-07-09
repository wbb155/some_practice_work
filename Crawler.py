"""
常用爬虫<br>
包括百度和豆瓣,可以直接插入到mysql中,但请先创建好表格和列
"""
import requests
from bs4 import BeautifulSoup
import re

class BaiduCrawler:
    def __init__(self):
        """
        用于获取百度热搜前十<br>
        并且可以存储到sql中去
        """
        pass

    def get_top10(self):
        """
        向百度发出请求,获得热搜前十
        """
        # 百度热搜URL
        url = "https://top.baidu.com/board?tab=realtime"
    
        # 设置请求头，模拟浏览器访问
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
    
        try:
            # 发送HTTP请求
            response = requests.get(url, headers=headers)
            response.raise_for_status()  # 检查请求是否成功
        
            # 使用BeautifulSoup解析HTML
            soup = BeautifulSoup(response.text, 'html.parser')
        
            # 查找热搜条目 - 根据百度热搜页面结构可能需要调整
            hot_items = soup.find_all('div', class_='category-wrap_iQLoo', limit=10)
        
            # 提取热搜标题和热度
            hot_searches = []
            for index, item in enumerate(hot_items[:10], 1):
                title = item.find('div', class_='c-single-text-ellipsis').text.strip()
                hot_index = item.find('div', class_='hot-index_1Bl1a').text.strip()
                hot_searches.append({
                    'rank': index,
                    'title': title,
                    'hot_index': hot_index
                })
            self.hot_searches = hot_searches
            return hot_searches
    
        except Exception as e:
            print(f"获取百度热搜失败: {e}")
            return []
        
    def print_news(self):
        """
        将新闻打印出来
        """
        if self.hot_searches:
            print("百度热搜前十:")
            # data = []
            for item in self.hot_searches:
                print(f"{item['rank']}. {item['title']} (热度: {item['hot_index']})")
                # data.append((item['rank'],item['title'],item['hot_index']))
        else:
            print("未能获取百度热搜")
    
    def save_to_sql(self,table:str,host:str,user:str,password:str,database:str,port:int=3306,charset: str = 'utf8mb4'):
        """
        用于存储到sql中去
        初始化数据库连接<br>
        :param host: 主机地址<br>
        :param user: 用户名<br>
        :param password: 密码<br>
        :param database: 数据库名<br>
        :param port: 端口号,默认3306<br>
        :param charset: 字符集,默认utf8mb4
        """
        from MySqlHelper import MySqlHelper
        if self.hot_searches:
            print("存储中")
            data = []
            for item in self.hot_searches:
                # print(f"{item['rank']}. {item['title']} (热度: {item['hot_index']})")
                data.append((item['rank'],item['title'],item['hot_index']))

            db = MySqlHelper(
                host=host,
                user=user,
                password=password,
                database=database,
                port=port,
                charset=charset
            )
            db.connect()
            db.execute_insert_list(table,['item_rank','titles','hot_index'],data)
            db.close()
        else:
            print("未能获取百度热搜,无法存储")


class DoubanCrawler:
    def __init__(self):
        pass

    def get_top_100(self):
        """
        获取豆瓣top100电影<br>
        从豆瓣top250排行榜中提取<br>
        如果要插入到sql中去,请保证表格拥有:
        item_rank,chinese_name,original_name,director,score,countries,genres这几列
        """
        url = 'https://movie.douban.com/top250'
        header = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.3.1 Safari/605.1.15',
            # 'Cookie': '__yadk_uid=hM9FXQDaKcHRJH9zTBXQlz8huBXKge8l; __utma=30149280.1419205261.1751976742.1751976742.1751976742.1; __utmb=30149280.0.10.1751976742; __utmc=30149280; __utmz=30149280.1751976742.1.1.utmcsr=baidu.com|utmccn=(referral)|utmcmd=referral|utmcct=/; ap_v=0,6.0; __utma=223695111.1004086242.1751976742.1751976742.1751976742.1; __utmb=223695111.0.10.1751976742; __utmc=223695111; __utmz=223695111.1751976742.1.1.utmcsr=baidu.com|utmccn=(referral)|utmcmd=referral|utmcct=/; _pk_id.100001.4cf6=5a170686164875d3.1751976742.; _pk_ref.100001.4cf6=%5B%22%22%2C%22%22%2C1751976742%2C%22https%3A%2F%2Fwww.baidu.com%2F%22%5D; _pk_ses.100001.4cf6=1; bid=vYy8Ip4nwTY; viewed="4001393_1918022_1698129_1017452"',
            }
        Chinese_name = []
        Original_name = []
        scores = []
        pattern = r'\s*/\s*(.+)$'
        t = 1  #开关，用于匹配中英文名字

        for s in [0,25,50,75]:
            params = {
                'start': float(s)
            }
            response = requests.get(url=url,headers=header,params=params)
            response.raise_for_status()
            soup = BeautifulSoup(response.text,'html.parser')
            titles = soup.find_all(name='span',class_='title')

            for title in titles:
                m = re.findall(pattern, title.text, re.MULTILINE)
                if not m:  # 说明这个是中文
                    Chinese_name.append(title.text)
                    if t==0:
                        Original_name.append('None')
                    t = 0

                else:  # 说明这个是英文
                    Original_name.extend(m)
                    t = 1
            score = soup.find_all(name='span',class_='rating_num',property='v:average')
            for so in score:
                scores.append(float(so.text))
            
            pattern2 = re.compile(
                r'导演:\s*([^&<]+).*?<br>\s*'  # 导演
                r'\d{4}&nbsp;/&nbsp;([^&<]+)&nbsp;/&nbsp;'  # 国家
                r'([^&<]+)',  # 类别
                re.DOTALL  # 允许跨行匹配
            )

        # 初始化结果字典
        result_dict = {
                'item_rank':list(range(1,101)),
                'chinese_name':Chinese_name,
                'original_name':Original_name,
                'score':scores,
                'director': [],
                'countries': [],
                'genres': []
        }
        for s in [0,25,50,75]:
            # 直接提取并填充到结果字典中
            for match in pattern2.finditer(response.text):
                result_dict['director'].append(match.group(1).strip())
                result_dict['countries'].append(match.group(2).strip())
                result_dict['genres'].append(match.group(3).strip())

        # print(result_dict)
        self.result_dict = result_dict        
        
        # print(len(Chinese_name),len(Original_name),len(scores),len(result_dict['director']),len(result_dict['countries']),len(result_dict['genres']))

        # print(response.text)        

    def print_film(self):
        """
        用于打印电影信息
        """
        from pandas import DataFrame
        data = DataFrame(self.result_dict)
        print(data)        

    def save_to_sql(self,table:str,host:str,user:str,password:str,database:str,port:int=3306,charset: str = 'utf8mb4'):
        """
        用于存储到sql中去
        初始化数据库连接<br>
        :param host: 主机地址<br>
        :param user: 用户名<br>
        :param password: 密码<br>
        :param database: 数据库名<br>
        :param port: 端口号,默认3306<br>
        :param charset: 字符集,默认utf8mb4
        """        
        from MySqlHelper import MySqlHelper
        if self.result_dict:
            print("存储中")

            db = MySqlHelper(
                host=host,
                user=user,
                password=password,
                database=database,
                port=port,
                charset=charset
            )
            db.connect()
            db.execuate_insert_dict(table,self.result_dict)
            db.close()
        else:
            print("未能获取百度热搜,无法存储")

if __name__=='__main__':
    """baidu = BaiduCrawler()
    baidu.get_top10()
    baidu.print_news()
    baidu.save_to_sql(
        table='News',
        host="localhost",
        user='root',
        password="Wrz040509",
        database="online_information",
    )"""

    """douban = DoubanCrawler()
    douban.get_top_100()
    douban.print_film()
    douban.save_to_sql(
        table='Films',
        host="localhost",
        user='root',
        password="Wrz040509",
        database="online_information",
    )"""
