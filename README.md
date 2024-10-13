# 烟悦网卷烟产品信息抓取器

本项目通过 Selenium 和 BeautifulSoup 从烟悦网抓取卷烟品牌及其产品信息，并下载产品图片。

## 功能

- 抓取所有卷烟品牌信息
- 抓取每个品牌的产品列表（包括名称、价格、评分等）
- 下载产品图片
- 保存品牌和产品信息到 JSON 文件

## 运行环境

- Python 3.x
- Selenium
- BeautifulSoup
- Chrome 浏览器和 ChromeDriver

## 安装步骤

1. 克隆项目到本地：

   ```bash
   git clone https://github.com/your-username/yanyue-scraper.git
   cd yanyue-scraper
   ```

2. 安装所需的 Python 库：

   ```bash
   pip install -r requirements.txt
   ```

3. 下载并安装 Chrome 浏览器，确保 ChromeDriver 的版本与 Chrome 浏览器匹配。可以从 [这里](https://sites.google.com/a/chromium.org/chromedriver/downloads) 下载 ChromeDriver，并将其放在系统路径中。

## 使用方法

1. 启动抓取程序：

   ```bash
   python scraper.py
   ```

2. 抓取完成后，所有品牌及其产品信息将保存在 `data` 目录下的 JSON 文件中：
   - `all_brands.json`: 包含所有卷烟品牌的信息。
   - `all_products.json`: 包含所有品牌的产品详细信息。
   - 各品牌的产品信息也会保存到单独的 JSON 文件中，例如 `brand_name_products.json`。

3. 所有产品的图片将下载到 `images` 目录下，以品牌名称分类保存。

## 注意事项

- 程序运行过程中可能需要较长时间，取决于网络速度和数据量。
- 确保 Chrome 浏览器与 ChromeDriver 版本匹配，否则可能会导致 Selenium 无法正常工作。
- 遵守目标网站的抓取规则，避免对服务器造成过多压力。

## 许可证

MIT License