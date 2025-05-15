from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import json

# 初始化 Chrome 浏览器
option = webdriver.ChromeOptions()
option.add_argument('--headless')  # 无头模式

browser = webdriver.Chrome(options=option)

# 定义函数获取电影概览页信息和详情页URL
def get_movie_info(page_number):
  detail_urls = []
  url = f"http://spa2.scrape.center/page/{page_number}"
  browser.get(url)
  try:
     WebDriverWait(browser, 10).until(
    EC.presence_of_all_elements_located((By.CSS_SELECTOR, ".el-card.item.m-t.is-hover-shadow"))         #这个是等待下面的电影名加载出来，否则直接执行下面代码找不到数据会报错
    )
        
     # 获取每部电影的详情页URL
     movies = browser.find_elements(By.CSS_SELECTOR, ".el-card.item.m-t.is-hover-shadow")     #选择器要这么写，返回一类元素列表，详情页的html会有一类像<div data-v-8a85e5c6="" class="el-card item m-t is-hover-shadow">的元素存着每部电影的信息，详情页url就在其中类名为name的a标签中
     for movie in movies:
        detail_url = movie.find_element(By.CSS_SELECTOR, "a.name").get_attribute('href')    #遍历每个元素，找到类名为name的a标签的链接属性就是电影详情页链接
        detail_urls.append(detail_url)
            
  except TimeoutException:
        print(f"页面 {page_number} 加载超时，跳过该页。")
    
  return detail_urls

# 定义爬取电影详情信息的函数
def scrape_movie_details(detail_url):
    info_dict = {}       #定义字典存每部电影信息，方便保存为json，最后返回
    browser.get(detail_url)
    try:
        # 等待详情页加载完成
        WebDriverWait(browser, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "h2.m-b-sm"))
        )
        
        # 提取电影名称
        name = browser.find_element(By.CSS_SELECTOR, "h2.m-b-sm").text
        
        # 提取电影类别
        categories = [cat.text for cat in browser.find_elements(By.CSS_SELECTOR, ".category span")]
        
        # 提取电影分数
        score = browser.find_element(By.CSS_SELECTOR, ".score").text
        
        # 提取电影简介
        summary = browser.find_element(By.CSS_SELECTOR, ".drama p").text
        

        info_dict = {'名称':name, '类别':categories, '分数':score, '简介':summary}       #定义字典存每部电影信息，方便保存为json，最后返回
        
    except TimeoutException:
        print(f"详情页 {detail_url} 加载超时，跳过该电影。")
    
    return info_dict

#准备URL数组
all_detail_urls = []
for i in range(1, 6):
    all_detail_urls.extend(get_movie_info(i))

# 爬取所有电影的详情信息
all_info = []
for i in all_detail_urls:
    all_info.append(scrape_movie_details(i))

# 关闭浏览器
browser.quit()


#保存为json
with open(r'.\info.json', 'w', encoding='utf-8') as f: 
    json.dump(all_info, f, ensure_ascii=False, indent=2)

#保存为txt
with open(r'.\info.txt', 'w', encoding = 'utf-8') as f:
    for i in all_info:
        f.write(f"名称: {i['名称']}, 类别: {i['类别']}, 分数: {i['分数']}, \n简介: {i['简介']}\n\n\n")



# 打印提取的信息
for i in all_info:
        print(f"名称: {i['名称']}, 类别: {i['类别']}, 分数: {i['分数']}, \n简介: {i['简介']}\n\n\n")
