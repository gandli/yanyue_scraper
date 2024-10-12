import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin


def main():
    # 定义目标URL
    url = "https://www.yanyue.cn/tobacco"

    # 禁用代理
    proxies = {
        "http": None,
        "https": None,
    }

    # 请求头，伪装成浏览器访问
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.102 Safari/537.36"
    }

    try:
        # 发送GET请求获取页面内容
        response = requests.get(url, headers=headers, proxies=proxies, timeout=10)
        response.raise_for_status()  # 检查请求是否成功

        # 确保正确的编码
        response.encoding = response.apparent_encoding

        # 使用BeautifulSoup解析HTML
        soup = BeautifulSoup(response.text, "html.parser")

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

            # 查找与当前分类 id 对应的 div
            brand_section = soup.find("div", id=tab_id)

            if brand_section:
                # 查找该 div 下的所有 ul 标签
                ul_elements = brand_section.find_all("ul")

                # 遍历每个 ul
                for ul in ul_elements:
                    # 在每个 ul 中找到所有 li 标签
                    list_items = ul.find_all("li")
                    for item in list_items:
                        # 在每个 li 中找到 a 标签
                        brand = item.find("a")
                        if brand:
                            brand_name = brand.get("title")  # 获取卷烟品牌名称
                            brand_url = brand.get("href")  # 获取品牌链接

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
            else:
                print(f"没有找到分类 {category_name} 的品牌信息")

        # 打印所有品牌名称和链接
        if all_brands:
            for brand in all_brands:
                print(
                    f"分类: {brand['category']}, 品牌名称: {brand['name']}, 链接: {brand['url']}"
                )
        else:
            print("没有找到任何品牌信息")

    except requests.exceptions.RequestException as e:
        print(f"请求失败: {e}")
    except Exception as e:
        print(f"发生错误: {e}")


if __name__ == "__main__":
    main()
