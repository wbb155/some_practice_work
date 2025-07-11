import requests
from bs4 import BeautifulSoup
from MySqlHelper import MySqlHelper

def get_baidu_hot_searches():
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
        
        return hot_searches
    
    except Exception as e:
        print(f"获取百度热搜失败: {e}")
        return []

# 获取并打印热搜前十
hot_searches = get_baidu_hot_searches()

if hot_searches:
    print("百度热搜前十:")
    data = []
    for item in hot_searches:
        print(f"{item['rank']}. {item['title']} (热度: {item['hot_index']})")
        data.append((item['rank'],item['title'],item['hot_index']))
else:
    print("未能获取百度热搜")



print(data)

db = MySqlHelper(
    host="localhost",
    user='root',
    password="",
    database="online_information",
)

db.connect()


db.execute_insert_list('News',['item_rank','titles','hot_index'],data)


db.close()
