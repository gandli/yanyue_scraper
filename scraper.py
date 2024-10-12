from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from urllib.parse import urljoin
import time


def init_driver():
    """初始化 Chrome 驱动"""
    # 设置 Chrome 驱动路径
    service = Service("chromedriver.exe")  # 根据你的路径设置
    chrome_options = Options()

    # 配置伪装头和反爬选项
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_argument(
        "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.102 Safari/537.36"
    )
    # chrome_options.add_argument("--headless")  # 如果不想打开浏览器界面可以加上这行

    # 初始化浏览器
    return webdriver.Chrome(service=service, options=chrome_options)


def get_all_brands(driver):
    """从分类页面抓取所有品牌的名称和链接"""
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

        return all_brands

    except Exception as e:
        print(f"发生错误: {e}")
        return []

def get_brand_products(driver, brand_url):
    """从品牌页面抓取该品牌下的所有品名和其他详细信息"""
    try:
        # 访问品牌页面
        driver.get(brand_url)
        time.sleep(3)  # 等待页面加载完成

        product_list = []

        # 查找产品信息部分
        product_sections = driver.find_elements(By.CLASS_NAME, "table clearfix")

        if product_sections:
            for product_section in product_sections:
                # 获取品名、类型、焦油含量、价格等信息
                product_name = product_section.find_element(By.CLASS_NAME, "name2").text
                product_type = product_section.find_element(By.CLASS_NAME, "type2").text
                tar_content = product_section.find_element(By.CLASS_NAME, "tar2").text
                price = product_section.find_element(By.CLASS_NAME, "price2").text

                # 获取评分信息
                subcontents = product_section.find_elements(By.CLASS_NAME, "subcontent3")
                taste_score = subcontents[0].find_element(By.CLASS_NAME, "c").text
                appearance_score = subcontents[1].find_element(By.CLASS_NAME, "c").text
                overall_score = subcontents[2].find_element(By.CLASS_NAME, "c").text

                product_list.append({
                    "品名": product_name,
                    "类型": product_type,
                    "焦油含量": tar_content,
                    "价格": price,
                    "口味评分": taste_score,
                    "外观评分": appearance_score,
                    "综合评分": overall_score
                })

        return product_list

    except Exception as e:
        print(f"无法抓取品牌页面 {brand_url}: {e}")
        return []


def main():
    # 初始化 Selenium 驱动
    driver = init_driver()

    try:
        # 第一步：获取所有品牌
        all_brands = get_all_brands(driver)

        # 第二步：抓取每个品牌页面的所有品名信息
        for brand in all_brands:
            print(f"\n正在抓取品牌: {brand['name']}")
            products = get_brand_products(driver, brand['url'])

            if products:
                print(f"{brand['name']} 共有 {len(products)} 个产品:")
                for product in products:
                    print(
                        f"品名: {product['品名']}, 类型: {product['类型']}, 焦油含量: {product['焦油含量']}, 价格: {product['价格']}, "
                        f"口味评分: {product['口味评分']}, 外观评分: {product['外观评分']}, 综合评分: {product['综合评分']}"
                    )

    finally:
        driver.quit()  # 关闭浏览器


if __name__ == "__main__":
    main()
