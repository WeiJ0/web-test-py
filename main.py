from selenium import webdriver
from selenium.webdriver.safari.options import Options
from selenium.webdriver.common.by import By
import sys
import os
import time
import re
import json
import sqlite3
import uuid

def checkHaveAdElement(driver):
    adElements = driver.find_elements(By.CSS_SELECTOR, "[id^='ad'],[class^='ad']")
    # 排除 id & class 為 address
    adElements = [element for element in adElements if element.get_attribute('id') != 'address' and element.get_attribute('class') != 'address']
    if len(adElements) > 0:
        print('具有 ad 開頭的元素有:')
        for element in adElements:
            outerHTML = element.get_attribute('outerHTML')
            outerHTML = re.sub(r"\s+", "", outerHTML)
            print(outerHTML)
            return outerHTML
    else:
        print('沒有具有 ad 開頭的元素')
        return '沒有具有 ad 開頭的元素'
    
def recordHeaderElements(driver):
    result = {}
    result = driver.execute_script("return [...document.querySelectorAll('h1,h2,h3,h4,h5,h6')].map(item => item.nodeName + ':' + item.innerText.trim())")
    return result

def getScreenshot(driver, current_page, device_name, id):        
    # driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")    
    required_width = driver.execute_script('return document.documentElement.scrollWidth')
    required_height = driver.execute_script('return document.documentElement.scrollHeight')
    driver.set_window_size(required_width, required_height)    
    time.sleep(2.5)
    driver.save_screenshot('./' + id + '/' +current_page + '_' + device_name + '.png')    

def createRecord(id):
    conn = sqlite3.connect('db.db')
    c = conn.cursor()
    c.execute("INSERT INTO result (run_id, is_done, run_time) VALUES ('" + id + "', 0, datetime('now'))");
    conn.commit()
    conn.close()

def updateRecord(id):
    conn = sqlite3.connect('db.db')
    c = conn.cursor()
    c.execute("UPDATE result SET is_done = 1 WHERE run_id = '" + id + "'");
    conn.commit()
    conn.close()

# 先將各個裝置尺寸變成物件
device_configs = {
    'Desktop': {'width': 1920, 'height': 1080},
    'iPhone 6': {'width': 375, 'height': 667},
    'iPhone 6 Plus': {'width': 414, 'height': 736},
    'iPhone SE': {'width': 320, 'height': 568},
    'iPad': {'width': 768, 'height': 1024},
    'iPad Pro': {'width': 1024, 'height': 1366},
    'macbook': {'width': 1440, 'height': 900},
    'iMac': {'width': 2560, 'height': 1440},
}

print(sys.argv)

# 參數 -P 網址
targetURL = sys.argv[1]

# 參數 -U 單元

if len(sys.argv) >= 3:    
    units = sys.argv[2].split(',')  
else:
    units = []

pages = []
pages.append(targetURL)

# 將所有單元整理成 array
for unit in units:
    pages.append(targetURL + unit)

# 儲存結果的物件
result = {}

id = str(uuid.uuid4())
createRecord(id)

# 根目錄建立一個名為 id 的資料夾
if not os.path.exists(id):
    os.makedirs(id)

# 開啟瀏覽器
options = Options()
options.add_argument('--headless')
driver = webdriver.Safari(Options)

driver.set_window_size(1920, 1080)
# 進入目標網址 設定 cookie temporaryVerifyCode = ok 避免驗證
driver.add_cookie({'name':'temporaryVerifyCode', 'value':'ok', 'domain': 'park-ibf2011.ito.tw'})

for page in pages:
    driver.get(page)
    # 重新整理跳開 loading 畫面        
    driver.refresh()
    # 顯示進入網站的提示
    print('進入網站:' + page)       
    result[page] = {}         

    # 移除淡入淡出動畫
    driver.execute_script("if(window.sr) Object.values(sr.store.elements).map(item => item.domEl).forEach(item => {item.removeAttribute('style')})")
    driver.execute_script("if(window.sr) Object.values(sr.store.elements).map(item => [item.config.beforeReveal,item.config.afterReveal]).forEach(item => {item[0](),item[1]()})")
    ### todo 移除 scrollReveal 的 resize & scroll 事件
    
    # 移除 lazyload
    driver.execute_script("[...document.querySelectorAll('.observerSlick, .observer')].forEach(item => item.classList.add('loaded'))")        
    # 暫停輪播
    driver.execute_script("$('.slick-slider').each(function(index,item) {$(item).slick('slickPause')});")

    if result[page].get('hasADElement') == None:
        # 寫入 result 物件格式為 {page: {'hasADElement': outerHTML}}           
        print('檢查是否有廣告元素')
        result[page]['hasADElement'] = checkHaveAdElement(driver)
    
    if result[page].get('headerElement') == None:
        # 寫入 result 物件格式為 {page: { 'headerElement' : {h1: [], h2: [], h3: [], h4: [], h5: []}}}
        print('檢查是否有標題元素')
        result[page]['headerElement'] = recordHeaderElements(driver)

    # 若當前頁面為首頁，則將頁面名稱設為 index
    current_page = page == targetURL and 'index' or page.replace(targetURL, '')
    # 進行截圖
    for device_name, device_config in device_configs.items():        
        driver.set_window_size(device_config['width'], device_config['height'])
        # 暫停 1 秒等待網頁元素讀取
        time.sleep(1)
        getScreenshot(driver, current_page, device_name, id)           

# 輸出 result 物件成 json 到 result.json    
with open('result.json', 'w') as fp:
    json.dump(result, fp, ensure_ascii=False)

updateRecord(id)

# 關閉瀏覽器
driver.quit()
