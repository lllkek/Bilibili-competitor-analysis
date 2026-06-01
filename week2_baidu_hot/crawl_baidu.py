import requests
from bs4 import BeautifulSoup
from datetime import datetime
from urllib.parse import urljoin


#1.百度热搜页面地址
url = "https://top.baidu.com/board?tab=realtime"

#2.添加请求头
headers = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/148.0.0.0 Safari/537.36"
}

#3.发送网页请求
response = requests.get(url, headers=headers, timeout=10)

#4.设置中文编码
response.encoding="utf-8"

# 5. 检查网页是否访问成功
#print("网页状态码:", response.status_code)

#6.获取HTML源码
html = response.text
#print("HTML源码前1000字符:", html[:1000])

#7.用BeautifulSoup解析HTML
soup = BeautifulSoup(html, "lxml")
#print("解析后的HTML前1000字符:", soup.prettify()[:1000])

#8.找到每一条热搜的外层容器
items = soup.select("div[class*='category-wrap']")
#print("热搜条数:", len(items))


#9.保存热搜结果
hot_list = []

for item in items[:10]:
   #热搜名称
   title_tag = item.select_one("div[class*='c-single-text-ellipsis']")

   #热度值
   hot_tag = item.select_one("div[class*='hot-index']")

   #链接
   link_tag = item.select_one("a[href]")

   keyword = title_tag.get_text(strip=True) if title_tag else ""  
   hot_score = hot_tag.get_text(strip=True) if hot_tag else ""  
   ink = link_tag.get("href") if link_tag else ""  

   #把相对链接转成完整链接
   if link:  
      link = urljoin(url, link) 
   
   #爬取日期
   crawl_date = datetime.now().strftime("%Y-%m-%d") 

   #.保存到列表
   hot_list.append({  
       "keyword": keyword,  
       "hot_score": hot_score,  
       "url": link,  
       "crawl_date": crawl_date
})  

#10.打印结果
print("百度热搜 Top10：")

for item in hot_list:
   print("热搜名称:", item["keyword"])
   print("热度值:", item["hot_score"])
   print("链接:", item["url"])
   print("日期:", item["crawl_date"])
   print("-" * 50)

print("共爬取:", len(hot_list), "条")

