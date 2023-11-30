from selenium import webdriver
from selenium.webdriver.common.by import By
from tabulate import tabulate
import time
import re

driver = webdriver.Safari()
targetURL = 'https://ibestpark2.ito.tw/csfmtw/'

driver.set_window_size(1920, 1080)   
# 進入目標網址 設定 cookie temporaryVerifyCode = ok domain:https://ibestpark2.ito.tw/csfmtw/
driver.add_cookie({'name':'temporaryVerifyCode', 'value':'ok', 'domain': 'ibestpark2.ito.tw'})
driver.get(targetURL)
driver.refresh()

# 顯示進入網站的提示
print('進入網站:' + targetURL)

# 模擬滾動到最下方
driver.execute_script('window.scrollTo(0, document.body.scrollHeight);')

# 檢查是否有 element 的 id 或 className 具有 ad 開頭的元素
# 如果沒有，就顯示訊息
adElements = driver.find_elements(By.CSS_SELECTOR, "[id^='ad'],[class^='ad']")
if len(adElements) > 0:
    print('具有 ad 開頭的元素有:')
    for element in adElements:
        outerHTML = element.get_attribute('outerHTML')
        outerHTML = re.sub(r"\s+", "", outerHTML)
        print(outerHTML)
else:
    print('沒有具有 ad 開頭的元素')

# 檢查 h1 - h5 的數量及內容
for i in range(1, 6):
    headerTextElements = driver.find_elements(By.CSS_SELECTOR,'h' + str(i))
    if len(headerTextElements) > 0:
        print('h' + str(i) + ' 元素有' + str(len(headerTextElements)) + '個')
        for element in headerTextElements:
            text_without_newlines = element.text.replace('\n', '')
            text_without_newlines = text_without_newlines.replace(' ', '')
            text_without_newlines = re.sub(r"\s+", "", text_without_newlines)
            print(text_without_newlines)   
        print('-------------------------')     
    else:
        print('沒有 h' + str(i) + ' 元素')

# 回傳執行 js getCopy() 的結果
copy_result = driver.execute_script('return getCopy()')
print('getCopy() 結果: ' + str(copy_result))

# 切換多個裝置大小並截圖
# 先將各個裝置尺寸變成物件
device_sizes = {
    'iPhone 6/7/8': {'width': 375, 'height': 667},
    'iPhone 6/7/8 Plus': {'width': 414, 'height': 736},
    'iPhone X': {'width': 375, 'height': 812},
    'iPad': {'width': 768, 'height': 1024},
    'iPad Pro': {'width': 1024, 'height': 1366},
    'Desktop': {'width': 1920, 'height': 1080}
}

# 逐一切換裝置大小並全頁截圖
for device_name, device_size in device_sizes.items():
    driver.set_window_size(device_size['width'], device_size['height'])   
    total_height = driver.execute_script("return document.body.parentNode.scrollHeight")        
    driver.set_window_size(device_size['width'], total_height)   
    # 等到網頁載入完畢
    time.sleep(5)
    driver.save_screenshot(device_name + '.png')
    total_height = driver.execute_script('$(".m_menu").find("a.main").click()')
    time.sleep(3)
    driver.save_screenshot(device_name + 'menuOpen.png')
# 關閉瀏覽器
driver.quit()







