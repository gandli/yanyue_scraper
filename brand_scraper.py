import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin


def fetch_brand_details(brand_url, page_number=None):
    """从品牌页面抓取品牌介绍和品名列表，包括评分等详细信息"""
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.102 Safari/537.36"
        }
        proxies = {
            "http": None,
            "https": None,
        }

        if page_number:
            brand_url = f"{brand_url}/p/{page_number}"

        response = requests.get(brand_url, headers=headers, proxies=proxies, timeout=10)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, "html.parser")

        brand_intro_section = soup.find("div", class_="desparea")
        if brand_intro_section:
            brand_name = (
                brand_intro_section.find("h3").get_text(strip=True)
                if brand_intro_section.find("h3")
                else "未知品牌"
            )
            brand_intro = (
                brand_intro_section.find("div", class_="desparea_content").get_text(
                    strip=True
                )
                if brand_intro_section.find("div", class_="desparea_content")
                else "无介绍"
            )
            print(f"品牌名称: {brand_name}")
            print(f"品牌介绍: {brand_intro}")
        else:
            print("未找到品牌介绍")

        product_list = []
        product_sections = soup.find_all("div", class_="table clearfix")

        if product_sections:
            for product_section in product_sections:
                product_name = (
                    product_section.find("div", class_="name2").get_text(strip=True)
                    if product_section.find("div", class_="name2")
                    else None
                )
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

                # 获取详情页URL
                more_info_section = product_section.find("div", class_="more")
                product_url = (
                    more_info_section.find("a")["href"]
                    if more_info_section and more_info_section.find("a")
                    else None
                )
                full_product_url = (
                    f"https://www.yanyue.cn{product_url}" if product_url else None
                )

                # 确保评分部分存在
                subcontents = product_section.find_all("div", class_="subcontent3")
                taste_score = (
                    subcontents[0].find("div", class_="c").get_text(strip=True)
                    if len(subcontents) > 0 and subcontents[0].find("div", class_="c")
                    else None
                )
                appearance_score = (
                    subcontents[1].find("div", class_="c").get_text(strip=True)
                    if len(subcontents) > 1 and subcontents[1].find("div", class_="c")
                    else None
                )
                overall_score = (
                    subcontents[2].find("div", class_="c").get_text(strip=True)
                    if len(subcontents) > 2 and subcontents[2].find("div", class_="c")
                    else None
                )

                # 只有在所有关键信息存在时，才加入 product_list
                if product_name and product_type and tar_content and price:
                    product_list.append(
                        {
                            "品名": product_name,
                            "类型": product_type,
                            "焦油含量": tar_content,
                            "价格": price,
                            "详情页": full_product_url
                            if full_product_url
                            else "无详情页",
                            "口味评分": taste_score if taste_score else "无评分",
                            "外观评分": appearance_score
                            if appearance_score
                            else "无评分",
                            "综合评分": overall_score if overall_score else "无评分",
                        }
                    )

        if product_list:
            for product in product_list:
                print(f"\n品名: {product['品名']}")
                print(
                    f"类型: {product['类型']}, 焦油含量: {product['焦油含量']}, 价格: {product['价格']}"
                )
                print(f"详情页: {product['详情页']}")
                print(
                    f"口味评分: {product['口味评分']}, 外观评分: {product['外观评分']}, 综合评分: {product['综合评分']}"
                )
        else:
            print("未找到任何有效的品名信息")

        pagination_info = soup.find("nav", class_="pagenav_mainarea")
        if pagination_info:
            total_records = (
                pagination_info.find("div", class_="ml-1").get_text(strip=True)
                if pagination_info.find("div", class_="ml-1")
                else "未知总记录数"
            )
            current_page = (
                pagination_info.find("span", class_="pagenav_currentpage").get_text(
                    strip=True
                )
                if pagination_info.find("span", class_="pagenav_currentpage")
                else "1"
            )
            total_pages = (
                pagination_info.find("span", class_="pagenav_totalnum").get_text(
                    strip=True
                )
                if pagination_info.find("span", class_="pagenav_totalnum")
                else "1"
            )
            # print(
            #     f"\n总记录数: {total_records}, 当前页: {current_page}, 总页数: {total_pages}"
            # )

            return int(total_pages)

        return None

    except requests.exceptions.RequestException as e:
        print(f"请求品牌页面失败: {e}")
    except Exception as e:
        print(f"发生错误: {e}")
        return None


def main():
    # 测试的品牌页面URL
    base_brand_url = "https://www.yanyue.cn/sort/14"  # 示例品牌页面

    # 抓取第一页并获取总页数
    total_pages = fetch_brand_details(base_brand_url)

    if total_pages:
        # 从第二页开始抓取，直到最后一页
        for page in range(2, total_pages + 1):
            # print(f"\n抓取第 {page} 页数据...")
            fetch_brand_details(base_brand_url, page)


if __name__ == "__main__":
    main()
