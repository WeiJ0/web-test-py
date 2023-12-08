from selenium import webdriver
from selenium.webdriver.safari.options import Options
from selenium.webdriver.common.by import By
import time
import re
import tkinter as tk
import json

def checkHaveAdElement(driver):
    adElements = driver.find_elements(By.CSS_SELECTOR, "[id^='ad'],[class^='ad']")
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
    for i in range(1, 6):
        headerTextElements = driver.find_elements(By.CSS_SELECTOR,'h' + str(i))
        if len(headerTextElements) > 0:
            result['h' + str(i)] = []
            for element in headerTextElements:
                text_without_newlines = element.text.replace('\n', '')
                text_without_newlines = text_without_newlines.replace(' ', '')
                text_without_newlines = re.sub(r"\s+", "", text_without_newlines)
                result['h' + str(i)].append(text_without_newlines)
        else:
            result['h' + str(i)] = []
    return result

def getScreenshot(driver, current_page, device_name, device_width):    
    total_height = driver.execute_script("return document.body.parentNode.scrollHeight")        
    driver.set_window_size( device_width, total_height)   
    driver.refresh()
    # 模擬慢慢滾動到底部
    for i in range(0, total_height, 100):
        driver.execute_script("window.scrollTo(0, {});".format(i))
        time.sleep(0.1)

    # 等到網頁載入完畢
    time.sleep(5)                   
    driver.save_screenshot(current_page + '-' + device_name + '.png')
    driver.execute_script('$(".slideMenuTrigger").click()')
    time.sleep(3)
    driver.save_screenshot(current_page + '-' + device_name + 'menuOpen.png')

def initialize_driver_with_user_agent(user_agent):    
    options = Options()
    options.add_argument('--user-agent=' + user_agent)
    print('user_agent: ' + user_agent)
    driver = webdriver.Safari(Options)
    return driver


# user agent
user_agents = {
    'Desktop': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko)',            
    'iPad': 'Mozilla/5.0 (iPad; CPU OS 14_4 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko)',
    'iPhone': 'Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1',                
}

# 先將各個裝置尺寸變成物件
device_configs = {
    'iPhone 6': {'width': 375, 'height': 667, 'user_agent': user_agents['iPhone']},
    'iPhone 6 Plus': {'width': 414, 'height': 736, 'user_agent': user_agents['iPhone']},
    'iPhone SE': {'width': 320, 'height': 568, 'user_agent': user_agents['iPhone']},
    'iPad': {'width': 768, 'height': 1024, 'user_agent': user_agents['iPad']},
    'iPad Pro': {'width': 1024, 'height': 1366, 'user_agent': user_agents['iPad']},
    'macbook': {'width': 1440, 'height': 900, 'user_agent': user_agents['Desktop']},
    'Desktop': {'width': 1920, 'height': 1080, 'user_agent': user_agents['Desktop']},
    'iMac': {'width': 2560, 'height': 1440, 'user_agent': user_agents['Desktop']},
}

def submit():
    # 設定目標網址 (首頁)
    targetURL = input_text.get()
    # 設定單元網址名稱
    units = textarea.get("1.0", "end-1c").split('\n')    

    pages = []
    pages.append(targetURL)

    # 將所有單元整理成 array
    for unit in units:
        pages.append(targetURL + unit)
    # 儲存結果的物件
    result = {}

    for device_name, device_config in device_configs.items():        
        driver = initialize_driver_with_user_agent(device_config['user_agent'])
        driver.set_window_size(device_config['width'], device_config['height'])
        # 進入目標網址 設定 cookie temporaryVerifyCode = ok 避免驗證
        driver.add_cookie({'name':'temporaryVerifyCode', 'value':'ok', 'domain': 'ibestpark2.ito.tw'})
        for page in pages:
            driver.get(page)
            # 重新整理跳開 loading 畫面
            user_agent = driver.execute_script("return navigator.userAgent")
            print('user_agent: ' + user_agent)
            driver.refresh()
            # 顯示進入網站的提示
            print('進入網站:' + page)       
            result[page] = {} 

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
            getScreenshot(driver, current_page, device_name, device_config['width'])           

            # 回傳執行 js getCopy() 的結果
            if result.get('getCopy') == None:
                copy_result = driver.execute_script('return getCopy()')            
                result['getCopy'] = copy_result

    # 輸出 result 物件成 json 到 result.json    
    with open('result.json', 'w') as fp:
        json.dump(result, fp, ensure_ascii=False)        
    
    # 關閉瀏覽器
    driver.quit()


# 以下為 GUI 程式碼
root = tk.Tk()

input_label = tk.Label(root, text="目標網址：")
input_label.pack()

input_text = tk.Entry(root, width=40)
input_text.pack()

textarea_label = tk.Label(root, text="單元網址名稱：")
textarea_label.pack()

textarea = tk.Text(root, height=20, width=80)
textarea.pack()

submit_button = tk.Button(root, text="送出", command=submit)
submit_button.pack()

root.mainloop()


