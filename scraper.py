from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from urllib.parse import urljoin
import time


def main():
    # 设置 Chrome 驱动路径
    service = Service("chromedriver.exe")  # 根据你的路径设置
    chrome_options = Options()

    # 配置伪装头和反爬选项
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_argument(
        "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.102 Safari/537.36"
    )
    chrome_options.add_argument("--headless")  # 如果不想打开浏览器界面可以加上这行

    # 初始化浏览器
    driver = webdriver.Chrome(service=service, options=chrome_options)

    # 定义目标URL
    url = "https://www.yanyue.cn/tobacco"

    try:
        # 访问页面
        driver.get(url)
        time.sleep(5)  # 等待页面加载完成

        # 初始化品牌分类和品牌列表
        categories = {
            "mainland": "大陆品牌",
            "foreign": "国外品牌",
            "HKMT": "港澳台品牌",
            "history": "历史品牌",
        }
        all_brands = []

        # 遍历每个品牌分类的 id 和名称
        for tab_id, category_name in categories.items():
            print(f"\n正在处理分类：{category_name}")

            try:
                # 查找与当前分类 id 对应的 div
                brand_section = driver.find_element(By.ID, tab_id)

                # 查找该 div 下的所有 ul 标签
                ul_elements = brand_section.find_elements(By.TAG_NAME, "ul")

                # 遍历每个 ul
                for ul in ul_elements:
                    # 在每个 ul 中找到所有 li 标签
                    list_items = ul.find_elements(By.TAG_NAME, "li")
                    for item in list_items:
                        # 在每个 li 中找到 a 标签
                        brand = item.find_element(By.TAG_NAME, "a")
                        brand_name = brand.get_attribute("title")  # 获取卷烟品牌名称
                        brand_url = brand.get_attribute("href")  # 获取品牌链接

                        if brand_name and brand_url:
                            full_brand_url = urljoin(
                                "https://www.yanyue.cn/", brand_url
                            )
                            all_brands.append(
                                {
                                    "category": category_name,
                                    "name": brand_name,
                                    "url": full_brand_url,
                                }
                            )
            except Exception as e:
                print(f"无法处理分类 {category_name}: {e}")

        # 打印所有品牌名称和链接
        if all_brands:
            for brand in all_brands:
                print(
                    f"分类: {brand['category']}, 品牌名称: {brand['name']}, 链接: {brand['url']}"
                )
        else:
            print("没有找到任何品牌信息")

    except Exception as e:
        print(f"发生错误: {e}")

    finally:
        driver.quit()  # 关闭浏览器


if __name__ == "__main__":
    main()
