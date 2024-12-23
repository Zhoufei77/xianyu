from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
import pandas as pd
import time

class XianYuCrawler:
    def __init__(self, seller_url):
        # 配置 Chrome 选项
        chrome_options = Options()
        chrome_options.add_argument("--start-maximized")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--headless")  # 添加无头模式
        chrome_options.add_argument("--disable-gpu")  # 禁用 GPU 加速
        chrome_options.add_argument("--log-level=3")  # 减少日志输出
        
        # 使用 WebDriver Manager 自动管理 ChromeDriver
        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service, options=chrome_options)
        
        self.seller_url = seller_url
        self.items_data = []

    def crawl(self, max_items=100):
        try:
            self.driver.get(self.seller_url)
            time.sleep(5)  # 等待页面加载
        except Exception as e:
            print(f"打开网页失败: {e}")
            return

        # 无限滚动
        last_height = self.driver.execute_script("return document.body.scrollHeight")
        while len(self.items_data) < max_items:
            # 滚动到页面底部
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(3)

            # 获取商品卡片
            try:
                cards = self.driver.find_elements(By.CSS_SELECTOR, ".cardWarp--dZodM57A")
            except Exception as e:
                print(f"查找商品卡片失败: {e}")
                break
            
            for card in cards:
                if len(self.items_data) >= max_items:
                    break

                try:
                    title = card.find_element(By.CSS_SELECTOR, ".main-title--sMrtWSJa").text
                    price = card.find_element(By.CSS_SELECTOR, ".number--NKh1vXWM").text
                    want_count = card.find_element(By.CSS_SELECTOR, ".text--MaM9Cmdn").text
                    item_link = card.find_element(By.CSS_SELECTOR, "a").get_attribute("href")
                    
                    item_data = {
                        "商品标题": title,
                        "价格": price,
                        "想要数": want_count,
                        "商品链接": item_link
                    }

                    if item_data not in self.items_data:
                        self.items_data.append(item_data)
                        print(f"已采集 {len(self.items_data)} 个商品")

                except Exception as e:
                    print(f"采集商品信息时出错: {e}")

            # 检查是否还能继续滚动
            new_height = self.driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                break
            last_height = new_height

    def save_data(self):
        if self.items_data:
            df = pd.DataFrame(self.items_data)
            df.to_csv("xianyu_items.csv", index=False, encoding="utf-8-sig")
            print(f"已保存 {len(self.items_data)} 个商品到 xianyu_items.csv")

    def __del__(self):
        if hasattr(self, 'driver'):
            self.driver.quit()

def main():
    seller_url = input("请输入闲鱼卖家主页网址: ")
    crawler = XianYuCrawler(seller_url)
    crawler.crawl(max_items=50)  # 可以调整采集数量
    crawler.save_data()
    input("采集完成，按回车键退出...")

if __name__ == "__main__":
    main()