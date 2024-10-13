import os
import time
import json
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from selenium import webdriver
from selenium.webdriver.chrome.options import Options


# 下载图片到本地目录的函数
def download_image(img_url, save_dir):
    """下载图片到本地"""
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)

    img_name = img_url.split("/")[-1]
    img_path = os.path.join(save_dir, img_name)

    try:
        response = requests.get(
            img_url, proxies={"http": None, "https": None}, verify=False
        )
        if response.status_code == 200:
            with open(img_path, "wb") as f:
                f.write(response.content)
            print(f"图片下载成功: {img_path}")
            return img_path
        else:
            print(f"图片下载失败，状态码: {response.status_code}")
            return None
    except Exception as e:
        print(f"图片下载出错: {e}")
        return None


# 从品牌页面抓取产品列表并处理分页的函数
def fetch_brand_products(driver, brand_url):
    """从品牌页面抓取所有页码的产品列表并下载图片"""
    driver.get(brand_url)
    time.sleep(3)  # 等待页面加载完成

    all_products = []

    while True:
        # 解析当前页面的产品信息
        soup = BeautifulSoup(driver.page_source, "html.parser")
        product_list = []
        product_sections = soup.find_all("div", class_="table clearfix")

        if product_sections:
            for product_section in product_sections:
                # 获取品名
                product_name = (
                    product_section.find("div", class_="name2").get_text(strip=True)
                    if product_section.find("div", class_="name2")
                    else None
                )
                # 如果没有品名，跳过当前循环
                if not product_name:
                    continue

                # 获取图片URL
                img_tag = product_section.find("div", class_="img2").find("img")
                img_url = img_tag.get("src") if img_tag else None
                
                # 下载图片到本地目录并获取本地路径
                img_local_path = (
                    download_image(img_url, "./images") if img_url else "无图片"
                )

                # 获取品名和其他信息
                product_name = (
                    product_section.find("div", class_="name2").get_text(strip=True)
                    if product_section.find("div", class_="name2")
                    else None
                )
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
                more_info_section = product_section.find("div", class_="more")
                product_url = (
                    more_info_section.find("a")["href"]
                    if more_info_section and more_info_section.find("a")
                    else None
                )
                full_product_url = (
                    f"https://www.yanyue.cn{product_url}" if product_url else None
                )
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
                        "图片路径": img_local_path or "无图片",
                    }
                )
                print(
                    f"找到产品：{product_name}, 类型: {product_type}, 焦油含量: {tar_content}, 价格: {price}, 图片: {img_local_path}"
                )

        all_products.extend(product_list)

        # 检查是否有“下一页”按钮
        next_page_button = (
            soup.find("li", class_="page-item")
            .find_next("li", class_="page-item")
            .find("a", string="下一页")
        )
        if next_page_button:
            next_page_url = urljoin(brand_url, next_page_button["href"])
            driver.get(next_page_url)
            time.sleep(3)  # 等待下一页加载完成
        else:
            break

    return all_products


# 抓取所有品牌的链接和名称
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


# 保存为 JSON 文件的函数
def save_to_json(data, filename):
    """将数据保存到 JSON 文件"""
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
    print(f"数据保存到 {filename} 完成")


# 主程序入口
def main():
    # 设置Selenium的Chrome选项
    chrome_options = Options()
    # 注释掉无头模式
    # chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")  # 禁用GPU

    driver = webdriver.Chrome(options=chrome_options)

    # 抓取所有品牌信息
    print("开始抓取所有品牌信息...")
    all_brands = fetch_all_brands(driver)
    save_to_json(all_brands, "all_brands.json")

    # 对每个品牌的产品信息进行抓取
    for brand in all_brands:
        brand_name = brand["name"]
        brand_url = brand["url"]
        print(f"\n开始抓取品牌 {brand_name} 的产品信息...")
        products = fetch_brand_products(driver, brand_url)

        # 保存品牌产品信息
        filename = f"{brand_name}_products.json"
        save_to_json(products, filename)

    # 关闭浏览器
    driver.quit()


if __name__ == "__main__":
    main()
