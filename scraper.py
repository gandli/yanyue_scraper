from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import time
import json


def fetch_all_brands(driver):
    """抓取所有品牌的链接和名称"""
    base_url = "https://www.yanyue.cn/tobacco"
    driver.get(base_url)
    time.sleep(3)  # 等待页面加载完成

    soup = BeautifulSoup(driver.page_source, "html.parser")

    categories = {
        "mainland": "大陆品牌",
        "foreign": "国外品牌",
        "HKMT": "港澳台品牌",
        "history": "历史品牌",
    }
    all_brands = []

    # 遍历每个品牌分类
    for tab_id, category_name in categories.items():
        print(f"\n正在处理分类：{category_name}")

        brand_section = soup.find("div", id=tab_id)

        if brand_section:
            ul_elements = brand_section.find_all("ul")

            # 遍历所有 ul 标签，提取 li 中的品牌数据
            for ul in ul_elements:
                list_items = ul.find_all("li")

                for item in list_items:
                    brand = item.find("a")
                    if brand:
                        brand_name = brand.get("title")  # 获取品牌名称
                        brand_url = brand.get("href")  # 获取品牌链接

                        if brand_name and brand_url:
                            full_brand_url = urljoin(base_url, brand_url)
                            all_brands.append(
                                {
                                    "category": category_name,
                                    "name": brand_name,
                                    "url": full_brand_url,
                                }
                            )
                            print(
                                f"找到品牌：{brand_name} - {full_brand_url}"
                            )  # 打印品牌信息
        else:
            print(f"没有找到分类 {category_name} 的品牌信息")

    return all_brands


def fetch_brand_products(driver, brand_url):
    """从品牌页面抓取所有页码的品名列表"""
    driver.get(brand_url)
    time.sleep(3)  # 等待页面加载完成

    all_products = []

    while True:
        # 抓取当前页面的产品信息
        soup = BeautifulSoup(driver.page_source, "html.parser")
        product_list = []
        product_sections = soup.find_all("div", class_="table clearfix")

        if product_sections:
            for product_section in product_sections:
                # 获取品名信息
                product_name = (
                    product_section.find("div", class_="name2").get_text(strip=True)
                    if product_section.find("div", class_="name2")
                    else None
                )

                # 如果没有品名信息，跳过该产品
                if not product_name:
                    continue

                product_type = (
                    product_section.find("div", class_="type2").get_text(strip=True)
                    if product_section.find("div", class_="type2")
                    else None
                )
                tar_content = (
                    product_section.find("div", class_="tar2").get_text(strip=True)
                    if product_section.find("div", class_="tar2")
                    else None
                )
                price = (
                    product_section.find("div", class_="price2").get_text(strip=True)
                    if product_section.find("div", class_="price2")
                    else None
                )

                # 获取更多信息的URL
                more_info_section = product_section.find("div", class_="more")
                product_url = (
                    more_info_section.find("a")["href"]
                    if more_info_section and more_info_section.find("a")
                    else None
                )
                full_product_url = (
                    f"https://www.yanyue.cn{product_url}" if product_url else None
                )

                # 评分信息
                subcontents = product_section.find_all("div", class_="subcontent3")
                taste_score = (
                    subcontents[0].find("div", class_="c").get_text(strip=True)
                    if len(subcontents) > 0 and subcontents[0].find("div", "c")
                    else None
                )
                appearance_score = (
                    subcontents[1].find("div", class_="c").get_text(strip=True)
                    if len(subcontents) > 1 and subcontents[1].find("div", "c")
                    else None
                )
                overall_score = (
                    subcontents[2].find("div", class_="c").get_text(strip=True)
                    if len(subcontents) > 2 and subcontents[2].find("div", "c")
                    else None
                )

                # 将每个产品的详细信息加入列表
                product_list.append(
                    {
                        "品名": product_name,
                        "类型": product_type or "未知类型",
                        "焦油含量": tar_content or "未知含量",
                        "价格": price or "未知价格",
                        "更多信息": full_product_url or "无更多信息",
                        "口味评分": taste_score or "无评分",
                        "外观评分": appearance_score or "无评分",
                        "综合评分": overall_score or "无评分",
                    }
                )
                print(
                    f"找到产品：{product_name}, 类型: {product_type}, 焦油含量: {tar_content}, 价格: {price}, 更多信息: {full_product_url}"
                )

        all_products.extend(product_list)

        # 检查是否有“下一页”按钮
        next_page_button = soup.find("a", class_="next")
        if next_page_button and "disabled" not in next_page_button.get("class", []):
            # 点击“下一页”按钮
            next_page_url = urljoin(brand_url, next_page_button["href"])
            driver.get(next_page_url)
            time.sleep(3)  # 等待下一页加载完成
        else:
            # 没有“下一页”按钮，或者按钮被禁用，结束循环
            break

    return all_products


def save_to_json(data, filename="products.json"):
    """将抓取的数据保存为 JSON 文件"""
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)


def main():
    # 配置 Selenium 的无头浏览器
    options = Options()
    # options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_argument("start-maximized")
    options.add_argument("disable-infobars")
    options.add_argument(
        "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.159 Safari/537.36"
    )
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option("useAutomationExtension", False)

    driver = webdriver.Chrome(options=options)

    try:
        # 修改浏览器的 User-Agent 以避免被检测为自动化工具
        driver.execute_cdp_cmd(
            "Network.setUserAgentOverride",
            {
                "userAgent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.159 Safari/537.36"
            },
        )
        driver.execute_script(
            "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
        )

        # 获取所有品牌
        brands = fetch_all_brands(driver)
        print(f"\n共找到 {len(brands)} 个品牌。")

        # 初始化用于存储所有品牌产品的列表
        all_brand_products = []

        # 对每个品牌抓取品名列表
        for brand in brands:
            print(f"\n抓取品牌：{brand['name']} - {brand['url']}")
            products = fetch_brand_products(driver, brand["url"])

            if products:
                print(f"在品牌 {brand['name']} 下找到 {len(products)} 个品名。")
                all_brand_products.append({brand["name"]: products})
            else:
                print(f"未找到品牌 {brand['name']} 的品名信息。")

        # 保存到 JSON 文件
        save_to_json(all_brand_products)

    finally:
        driver.quit()


if __name__ == "__main__":
    main()
