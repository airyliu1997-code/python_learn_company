from playwright.sync_api import sync_playwright
from datetime import datetime
expires_str = "2027-01-01T02:02:54.030Z"
expires_ts = int(datetime.fromisoformat(expires_str.replace("Z", "+00:00")).timestamp())
cookies = [
    # Cookie1: sensorsdata2015jssdkcross
    {
        "name": "sensorsdata2015jssdkcross",
        "value": "%7B%22distinct_id%22%3A%22762066195477168140%22%2C%22first_id%22%3A%2219a2397199210cd-03833213865b29a-1e525631-2073600-19a239719931c9c%22%2C%22props%22%3A%7B%22%24latest_traffic_source_type%22%3A%22%E7%9B%B4%E6%8E%A5%E6%B5%81%E9%87%8F%22%2C%22%24latest_search_keyword%22%3A%22%E6%9C%AA%E5%8F%96%E5%88%B0%E5%80%BC_%E7%9B%B4%E6%8E%A5%E6%89%93%E5%BC%80%22%2C%22%24latest_referrer%22%3A%22%22%7D%2C%22identities%22%3A%22eyIkaWRlbnRpdHlfY29va2llX2lkIjoiMTlhMjM5NzE5OTIxMGNkLTAzODMzMjEzODY1YjI5YS0xZTUyNTYzMS0yMDczNjAwLTE5YTIzOTcxOTkzMWM5YyIsIiRpZGVudGl0eV9sb2dpbl9pZCI6Ijc2MjA2NjE5NTQ3NzE2ODE0MCJ9%22%2C%22history_login_id%22%3A%7B%22name%22%3A%22%24identity_login_id%22%2C%22value%22%3A%22762066195477168140%22%7D%2C%22%24device_id%22%3A%2219a2397199210cd-03833213865b29a-1e525631-2073600-19a239719931c9c%22%7D",
        "domain": ".rabyte.cn",  # 或具体域名alphapai-web.rabyte.cn
        "path": "/",
        "expires": expires_ts,  # 替换为实际expires
        "httpOnly": False,  # 按浏览器显示填写
        "secure": False      # 按浏览器显示填写
    },
    # Cookie2: SERVERCORSID
    {
        "name": "SERVERCORSID",
        "value": "af0c002de304807a30661279d2d228a5|1764212387|1764206998",
        "domain": "rabytetech.datasink.sensorsdata.cn",
        "path": "/",
        "expires": -1,
        "httpOnly": False,
        "secure": True,
        "SameSite": None
    },
    # Cookie3: SERVERID
    {
        "name": "SERVERID",
        "value": "af0c002de304807a30661279d2d228a5|1764212387|1764206998",
        "domain": "rabytetech.datasink.sensorsdata.cn",
        "path": "/",
        "expires": -1,
        "httpOnly": False,
        "secure": False
    }
]
from playwright.sync_api import sync_playwright
import time

with sync_playwright() as p:
    # 1. 启动浏览器时禁用自动化特征
    browser = p.chromium.launch(
        headless=False,  # 先可视化调试
        args=[
            "--disable-blink-features=AutomationControlled",
            "--disable-extensions",
            "--disable-plugins",
            "--start-maximized"  # 模拟真实窗口大小
        ]
    )
    
    # 2. 创建上下文时设置用户代理和视口
    context = browser.new_context(
        user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        viewport={"width": 1920, "height": 1080},
        locale="zh-CN",
        timezone_id="Asia/Shanghai"
    )
    
    # 3. 移除webdriver标识（关键）
    context.add_init_script("""
        Object.defineProperty(navigator, 'webdriver', {get: () => undefined});
        Object.defineProperty(navigator, 'languages', {get: () => ['zh-CN', 'zh']});
        Object.defineProperty(navigator, 'plugins', {get: () => [1, 2, 3]});
    """)
    
    context.add_cookies(cookies)
    
    # 5. 打开页面并等待足够时间
    page = context.new_page()
    # 先访问首页，再跳转目标页面（模拟用户操作）
    page.goto("https://alphapai-web.rabyte.cn", wait_until="networkidle")
    time.sleep(2)  # 等待首页加载完成
    page.goto("https://alphapai-web.rabyte.cn/reading/home/stock?id=002475.SZ&name=%E7%AB%8B%E8%AE%AF%E7%B2%BE%E5%AF%86", wait_until="networkidle")
    time.sleep(5)  # 延长等待时间，确保内容渲染
    
    # 6. 调试信息：打印Cookie和页面状态
    print("当前页面Cookie：", context.cookies())
    print("页面标题：", page.title())
    print("页面URL：", page.url)
    
    # 7. 截图并保存HTML（分析页面状态）
    page.screenshot(path="final_page.png", full_page=True)
    with open("page_source.html", "w", encoding="utf-8") as f:
        f.write(page.content())
    
    browser.close()