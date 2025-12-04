import requests
import json
import re
from urllib.parse import quote
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import os

class JiuYanGongSheSpider:
    def __init__(self, cookie):
        # Setup Chrome options
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument("--headless=new")  # Use new headless mode for Chrome 109+
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36")
        chrome_options.add_argument("--disable-web-security")
        chrome_options.add_argument("--disable-features=VizDisplayCompositor")
        chrome_options.add_argument("--disable-extensions")
        chrome_options.add_argument("--disable-background-timer-throttling")
        chrome_options.add_argument("--disable-backgrounding-occluded-windows")
        chrome_options.add_argument("--disable-renderer-backgrounding")
        chrome_options.add_argument("--disable-background-networking")
        chrome_options.add_argument("--no-first-run")
        chrome_options.add_argument("--no-default-browser-check")
        chrome_options.add_argument("--disable-logging")
        chrome_options.add_argument("--disable-site-isolation-trials")
        chrome_options.add_argument("--disable-impl-side-painting")
        chrome_options.add_argument("--disable-seccomp-filter-sandbox")
        chrome_options.add_argument("--disable-ipc-flooding-protection")
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)

        try:
            # Initialize the driver with explicit timeout for driver creation
            import subprocess
            try:
                # Try to find the chromedriver path
                result = subprocess.run(["which", "chromedriver"], capture_output=True, text=True, timeout=5)
                if result.returncode == 0 and result.stdout.strip():
                    chromedriver_path = result.stdout.strip()
                    service = Service(chromedriver_path)
                else:
                    # Use webdriver_manager as fallback
                    service = Service(ChromeDriverManager(cache_valid_range=7).install())  # Cache for 7 days to avoid repeated downloads
            except:
                # Use webdriver_manager as fallback if subprocess fails
                service = Service(ChromeDriverManager(cache_valid_range=7).install())

            self.driver = webdriver.Chrome(service=service, options=chrome_options)

        except Exception as e:
            # If the initial attempt failed, try with webdriver manager that has more timeout settings
            try:
                # Use the already imported ChromeDriverManager
                service = Service(ChromeDriverManager(cache_valid_range=7).install())
                self.driver = webdriver.Chrome(service=service, options=chrome_options)
            except Exception as e2:
                raise Exception(f"Failed to initialize ChromeDriver: {e}. Alternative method also failed: {e2}")

        # Set page load timeout
        self.driver.set_page_load_timeout(30)  # 30 seconds timeout
        self.driver.implicitly_wait(10)  # 10 seconds implicit wait

        # Execute script to remove webdriver property to avoid detection
        self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

        # Store the cookie
        self.cookie = cookie
        self.base_url = 'https://www.jiuyangongshe.com/search/new?k='  # Base URL for all searches

    def verify_login(self):
        """验证是否登录成功"""
        try:
            # Wait for page to load and check for login indicators
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            page_source = self.driver.page_source

            # 登录成功的特征：页面包含"退出登录"或"我的主页"
            if '退出登录' in page_source or '我的主页' in page_source or '发布' in page_source:
                print("✅ 登录验证成功！")
                return True
            else:
                print("❌ 登录验证失败！页面为未登录状态")
                print("未登录页面预览（前500字符）：")
                print(page_source[:500])
                return False
        except Exception as e:
            print(f"登录验证出错: {e}")
            return False

    def extract_post_data(self):
        """提取帖子数据（从已加载的页面中）"""
        try:
            # Wait for the page to fully load
            try:
                WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.TAG_NAME, "body"))
                )
            except:
                print("页面body元素加载超时，继续尝试提取数据...")

            # Wait a bit more to ensure all JavaScript has executed
            time.sleep(3)

            # For JavaScript-heavy sites like this, we need to wait for dynamic content to load
            # Look for elements that indicate articles/posts are present
            try:
                # Wait for article elements to be present (adjust selector as needed)
                # Using explicit waits for each selector separately
                wait = WebDriverWait(self.driver, 5)  # Reduced wait time
                selectors = [
                    (By.CLASS_NAME, "article-item"),
                    (By.CSS_SELECTOR, "[data-v-6060adf8]"),
                    (By.CLASS_NAME, "article-list")
                ]

                for by, selector in selectors:
                    try:
                        wait.until(EC.presence_of_element_located((by, selector)))
                        break  # Exit if any selector is found
                    except:
                        continue  # Try next selector
            except:
                # If specific selectors don't work, just continue
                pass

            # Try to extract posts by executing JavaScript to access the nuxt store directly
            try:
                # Execute JavaScript to extract the nuxt state
                nuxt_data = self.driver.execute_script("""
                    if (window.__NUXT__) {
                        // Try to get the actual data, but this is complex due to obfuscation
                        // For now, return the stringified version
                        return JSON.stringify(window.__NUXT__);
                    } else {
                        return null;
                    }
                """)

                if nuxt_data and nuxt_data != 'null' and nuxt_data != 'NUXT not found':
                    print("获取到 nuxt 数据")
                    # Parse the JSON to get the actual data
                    try:
                        nuxt_obj = json.loads(nuxt_data)
                        # Navigate to where the actual article data might be

                        # Check if there's data in the expected location
                        if 'data' in nuxt_obj and len(nuxt_obj['data']) > 0:
                            first_data_item = nuxt_obj['data'][0] if isinstance(nuxt_obj['data'], list) else nuxt_obj['data']

                            # Extract from both 'list' and 'productList' which might contain articles
                            combined_list = []

                            if 'list' in first_data_item:
                                post_list = first_data_item['list']
                                print(f"从 nuxt list 中提取到 {len(post_list)} 个项目")
                                combined_list.extend(post_list)

                            if 'productList' in first_data_item:
                                product_list = first_data_item['productList']
                                print(f"从 nuxt productList 中提取到 {len(product_list)} 个项目")
                                # Convert product items to a similar format as posts for consistency
                                for item in product_list:
                                    # Add a flag to distinguish products from articles
                                    item['is_product'] = True
                                combined_list.extend(product_list)

                            if combined_list:
                                print(f"总共提取到 {len(combined_list)} 个项目")
                                return combined_list
                            else:
                                print("nuxt 数据中未找到任何项目")

                    except json.JSONDecodeError as e:
                        print(f"无法解析 nuxt 数据为 JSON: {e}")

            except Exception as js_error:
                print(f"执行 JavaScript 获取 nuxt 数据时出错: {js_error}")
                import traceback
                traceback.print_exc()

            # As a fallback, try to extract posts by looking for article elements in the DOM
            # This assumes the articles are rendered as HTML elements we can identify
            try:
                # Look for article containers in the page
                article_elements = self.driver.find_elements(By.CSS_SELECTOR, ".article-item, .article-list-item, .post-item, [class*='article'], [class*='post']")

                posts = []
                for element in article_elements:
                    try:
                        # Extract information from each article element
                        # This will vary based on the site's HTML structure
                        title_element = element.find_elements(By.TAG_NAME, 'a') or element.find_elements(By.CLASS_NAME, 'title')
                        title = title_element[0].text if title_element else '无标题'

                        # Placeholder - add more extraction logic based on site's DOM structure
                        post_info = {
                            'title': title,
                            'content': '',  # Would need to extract from DOM
                            'create_time': '',  # Would need to extract from DOM
                            'view_count': 0,  # Would need to extract from DOM
                            'stock_list': [],  # Would need to extract from DOM
                            'is_dom_extracted': True
                        }
                        posts.append(post_info)
                    except Exception as e:
                        continue  # Skip if we can't extract from this element

                if posts:
                    print(f"从页面DOM中提取到 {len(posts)} 个帖子")
                    return posts

            except Exception as dom_error:
                print(f"从DOM提取帖子时出错: {dom_error}")

            # If all methods fail, return empty list
            return []

        except Exception as e:
            print(f"提取帖子数据失败: {e}")
            import traceback
            traceback.print_exc()
            return []

    def crawl_stock_posts(self, stock_name):
        print(f"开始爬取 {stock_name} 的相关帖子...\n")

        try:
            # Navigate to the domain first to set cookies properly
            self.driver.get("https://www.jiuyangongshe.com")

            # Add the cookies to the driver
            cookie_pairs = self.cookie.split(';')
            for pair in cookie_pairs:
                if '=' in pair:
                    name, value = pair.split('=', 1)
                    name = name.strip()
                    value = value.strip()
                    if name and value:
                        # Add cookie, handling URL encoded values
                        import urllib.parse
                        decoded_value = urllib.parse.unquote(value)

                        # Set cookies with proper domain and path
                        try:
                            # Try adding the cookie with the main domain first
                            self.driver.add_cookie({
                                'name': name,
                                'value': decoded_value,
                                'domain': '.jiuyangongshe.com',
                                'path': '/',
                                'secure': False
                            })
                        except:
                            # If that fails, try with the www subdomain
                            try:
                                self.driver.add_cookie({
                                    'name': name,
                                    'value': decoded_value,
                                    'domain': 'www.jiuyangongshe.com',
                                    'path': '/',
                                    'secure': False
                                })
                            except:
                                # If both fail, add without domain specification
                                self.driver.execute_script(f"document.cookie = '{name}={decoded_value}; domain=.jiuyangongshe.com; path=/';")

            # Navigate to the search page with the query (for all posts first)
            encoded_name = quote(stock_name)
            url = f'{self.base_url}{encoded_name}'
            self.driver.get(url)

            # Wait for page to load
            time.sleep(5)  # Give time for JavaScript to execute

            print("检查页面加载状态...")

            # Verify login status
            if not self.verify_login():
                return "【登录失败】请重新获取有效Cookie！\n原因：Cookie无效/过期/未登录，导致页面无帖子数据"

            # After loading the search results, click on the "标题标签" tab to filter
            try:
                # Wait for the filter tabs to be available
                filter_tab = WebDriverWait(self.driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, "//span[contains(text(), '标题标签') or contains(text(), 'title tags') or contains(@class, 'tag')]"))
                )
                # Click on the "标题标签" (title tags) tab
                self.driver.execute_script("arguments[0].click();", filter_tab)
                print("已点击标题标签筛选")

                # Wait for the content to reload after filtering
                time.sleep(3)
            except:
                # If the specific tab isn't found, try to find elements by common class names for tags
                try:
                    # Try to find tag filter using common selectors
                    tag_filters = self.driver.find_elements(By.CSS_SELECTOR, "div[role='tab'], .tab-item, .filter-item")
                    for tab in tag_filters:
                        if '标题标签' in tab.text or 'title' in tab.text.lower() or 'tag' in tab.text.lower():
                            self.driver.execute_script("arguments[0].click();", tab)
                            print("已点击标题标签筛选")
                            time.sleep(3)
                            break
                except:
                    print("未找到标题标签筛选项，使用默认搜索结果")

            # 4. 尝试最多3次提取帖子数据
            post_list = []
            max_retries = 3
            retry_count = 0

            while retry_count < max_retries:
                print(f"尝试提取帖子数据... (第{retry_count + 1}次)")

                # Extract data after JavaScript has loaded the content
                post_list = self.extract_post_data()

                if post_list:
                    print(f"成功提取到 {len(post_list)} 个帖子")
                    break
                else:
                    print(f"第{retry_count + 1}次尝试未提取到帖子，等待重试...")
                    retry_count += 1
                    if retry_count < max_retries:
                        # 等待一段时间再重试
                        time.sleep(3)

            if not post_list:
                return f"【{stock_name}】登录成功，但搜索结果中无相关帖子"

            # 5. 筛选目标股票帖子
            target_posts = []
            stock_name_lower = stock_name.lower()
            for post in post_list:
                post_title = post.get('title', '').lower()
                post_content = post.get('content', '').lower()
                related_stocks = post.get('stock_list', []) if isinstance(post.get('stock_list'), list) else []
                related_stock_names = [s.get('name', '').lower() for s in related_stocks if isinstance(s, dict)]

                if (stock_name_lower in post_title or
                    stock_name_lower in post_content or
                    stock_name_lower in [name.lower() for name in related_stock_names]):
                    target_posts.append(post)
                    if len(target_posts) >= 5:
                        break

            if not target_posts:
                return f"【{stock_name}】登录成功，但搜索结果中无相关帖子"

            # 5. 整理输出
            final_output = f"【{stock_name} - 韭研公社相关帖子汇总】\n\n"
            for i, post in enumerate(target_posts, 1):
                post_id = post.get('article_id', '') or post.get('id', '')
                title = post.get('title', '无标题')
                author_info = post.get('user', {}) if isinstance(post.get('user'), dict) else {}
                author = author_info.get('nickname', post.get('author', '未知作者'))
                publish_time = post.get('create_time', post.get('publish_time', '未知时间'))
                view_count = post.get('view_count', post.get('views', 0))
                post_url = f"https://www.jiuyangongshe.com/a/{post_id}" if post_id else ''  # Updated URL format

                # Get the full content from the article page if URL is available
                if post_url:
                    print(f"正在获取第{i}篇文章的完整内容: {title}")
                    full_content = self.get_full_article_content(post_url, post)
                else:
                    # Fallback to the preview content if no URL
                    full_content = self.clean_content(post.get('content', ''))

                final_output += f"=== 第{i}篇 ===\n"
                final_output += f"标题: {title}\n"
                final_output += f"链接: {post_url}\n"
                final_output += f"作者: {author}\n"
                final_output += f"发布时间: {publish_time}\n"
                final_output += f"阅读量: {view_count}\n"
                final_output += f"内容:\n{full_content}\n\n"
                final_output += "-" * 80 + "\n\n"

            return final_output

        except Exception as e:
            return f"【爬取异常】{type(e).__name__}: {str(e)}"
        finally:
            # Make sure to close the driver when done
            try:
                self.driver.quit()
            except:
                pass

    def clean_content(self, content_html):
        """清理帖子内容"""
        if not content_html:
            return "无有效内容"
        content = re.sub(r'<[^>]+>', '', content_html)
        content = re.sub(r'\s+', '\n', content).strip()
        return content[:5000]

    def get_full_article_content(self, article_url, article_obj=None):
        """获取文章完整内容"""
        try:
            # Check if we have content in the original article object first
            if article_obj and article_obj.get('content'):
                preview_content = self.clean_content(article_obj.get('content', ''))
                if len(preview_content) > 20:  # If there's some content in the preview
                    print("使用原始数据中的内容预览")
            else:
                preview_content = "无预览内容"

            # Try navigating to the correct article URL format
            print(f"尝试访问文章页面: {article_url}")

            # Navigate directly to the article page using the correct format (a/{id})
            try:
                self.driver.get(article_url)
            except:
                print("访问文章页面超时")
                return preview_content

            # Wait for the page to load
            try:
                WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.TAG_NAME, "body"))
                )
            except:
                print("文章页面加载超时")
                return preview_content

            # Wait more for dynamic content to potentially load
            time.sleep(3)

            print(f"页面加载完成，当前URL: {self.driver.current_url}")
            print(f"页面标题: {self.driver.title}")

            # Check if we were redirected or if the content loaded
            current_url = self.driver.current_url
            if "login" in current_url or "signin" in current_url or self.driver.title == "登录" or "注册" in self.driver.title:
                print("检测到重定向到登录页面，返回预览内容")
                return preview_content if 'preview_content' in locals() else "无法提取完整内容，需要登录"

            # More specific approach to extract main content avoiding comment sections
            main_content_selectors = [
                '.jc-home',  # Based on analysis, this class contains main content
                '.article-main',  # Alternative main content area
                '[class*="article-body"]',  # Article body containers
                '[class*="article-content"]',  # Article content containers
                '.main-content',  # Main content area
                '[id*="content"]',  # Content by ID
                'article',  # Article tag, if present
            ]

            full_content = ""

            # First, try to find content that's NOT in comment sections
            for selector in main_content_selectors:
                try:
                    elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    for element in elements:
                        element_text = element.text.strip()
                        # Check if this content is NOT primarily comment-like
                        comment_ratio = self._calculate_comment_ratio(element_text)
                        if element_text and comment_ratio < 0.5:  # Less than 50% comments
                            if len(element_text) > len(full_content):
                                full_content = element_text
                    if full_content:
                        break
                except:
                    continue

            # If we still don't have good content, try a different approach
            if not full_content or len(full_content) < 100:
                try:
                    # Find all divs but exclude those that are clearly comment sections
                    all_divs = self.driver.find_elements(By.TAG_NAME, 'div')
                    for div in all_divs:
                        div_text = div.text.strip()
                        div_class = div.get_attribute('class') or ''

                        # Skip comment sections based on class names or text patterns
                        if (not any(skip in div_class.lower() for skip in ['comment', 'reply', 'response', 'user']) and
                            not any(skip in div_text[:200].lower() for skip in ['只看ta', '打赏', '回复', '投诉', '感谢分享']) and
                            len(div_text) > 150):  # Only consider substantial content

                            comment_ratio = self._calculate_comment_ratio(div_text)
                            if comment_ratio < 0.3:  # Less than 30% comments
                                if len(div_text) > len(full_content):
                                    full_content = div_text
                except:
                    pass

            # If still no good content, try to extract content by filtering comments from large text blocks
            if not full_content or len(full_content) < 100:
                try:
                    # Try to get the main body text and filter out comment portions
                    body_element = self.driver.find_element(By.TAG_NAME, 'body')
                    all_text = body_element.text

                    if all_text:
                        # Split by common comment elements and take the substantial non-comment portion
                        potential_content_parts = all_text.split('\n\n')
                        for part in potential_content_parts:
                            if (len(part.strip()) > 100 and
                                '只看TA' not in part and
                                '打赏' not in part and
                                '回复' not in part and
                                '感谢分享' not in part):
                                if len(part) > len(full_content):
                                    full_content = part
                except:
                    pass

            # Clean up the content
            if full_content:
                # Remove excessive whitespace
                full_content = re.sub(r'\n\s*\n', '\n\n', full_content)
                full_content = full_content.strip()

                # If we got more content than the preview, return it
                if len(full_content) > len(preview_content if 'preview_content' in locals() else ""):
                    print("成功获取更完整的文章内容")
                    return full_content
                else:
                    print("未能获取比预览更完整的内容")
                    return preview_content if 'preview_content' in locals() else full_content
            else:
                print("未能从文章页面提取内容，返回预览内容")
                return preview_content if 'preview_content' in locals() else "无法提取完整内容"

        except Exception as e:
            print(f"获取文章完整内容失败 {article_url}: {e}")
            import traceback
            traceback.print_exc()
            # If anything fails, return the preview content we already have
            return preview_content if 'preview_content' in locals() else "无法提取完整内容"

    def _calculate_comment_ratio(self, text):
        """计算文本中评论相关词汇的比例"""
        if not text:
            return 1.0

        lines = text.split('\n')
        comment_lines = 0

        for line in lines:
            line_lower = line.lower()
            if any(keyword in line_lower for keyword in ['只看ta', '打赏', '回复', '投诉', '感谢分享', '谢谢']):
                comment_lines += 1
            elif '今天' in line and ('北京' in line or '上海' in line or '广东' in line or '浙江' in line or '四川' in line or '广西' in line or '安徽' in line or '河南' in line or '湖南' in line or '江苏' in line or '山东' in line):
                # Pattern: "今天 XX时间 XX地点" is often for comments
                comment_lines += 1

        return comment_lines / len(lines) if lines else 0

def get_valid_cookie():
    """直接返回预设的 cookie"""
    cookie = "Hm_lvt_2d6d056d37910563cdaa290ee2981080=1763398928,1763477226,1763992215,1764069813; HMACCOUNT=524E2D3BADE2C206; Hm_lvt_58aa18061df7855800f2a1b32d6da7f4=1763398928,1763477226,1763992215,1764069813; admin=%7B%22user_id%22%3A%223a34b21668e143dcb828393491875444%22%2C%22country_code%22%3A%22%2B86%22%2C%22phone%22%3A%2215652307727%22%2C%22nickname%22%3A%22%E6%97%A0%E5%90%8D%E5%B0%8F%E9%9F%AD77270227%22%2C%22avatar%22%3A%22https%3A%2F%2Fjiucaigongshe.oss-cn-beijing.aliyuncs.com%2Favatar_default.png%22%2C%22gender%22%3A0%2C%22profile%22%3A%22%E8%BF%99%E4%B8%AA%E4%BA%BA%E5%BE%88%E6%87%92%EF%BC%8C%E4%BB%80%E4%B9%88%E9%83%BD%E6%B2%A1%E6%9C%89%E7%95%99%E4%B8%8B%22%2C%22open_id%22%3Anull%2C%22pc_open_id%22%3Anull%2C%22union_id%22%3Anull%2C%22city%22%3Anull%2C%22area%22%3Anull%2C%22follow_count%22%3A6%2C%22fans_count%22%3A0%2C%22like_count%22%3A0%2C%22posts%22%3A0%2C%22energy%22%3A100%2C%22integral%22%3A0%2C%22integral_grade%22%3A10%2C%22balance%22%3A0%2C%22interaction%22%3A0%2C%22verify%22%3A0%2C%22msg_vibrate%22%3A0%2C%22faction%22%3A0%2C%22faction_id%22%3A%22%22%2C%22investment_style%22%3A%22%22%2C%22investment_style_id%22%3A%22%22%2C%22status%22%3A0%2C%22reward_read_day%22%3A6%2C%22reward_read_time%22%3A%222025-08-15%2023%3A59%3A59%22%2C%22no_read_limit_time%22%3Anull%2C%22change_nickname_limit_time%22%3Anull%2C%22change_info_limit_time%22%3Anull%2C%22medal_count%22%3A0%2C%22withdraw_review%22%3A0%2C%22newest_article_tool_time%22%3Anull%2C%22create_time%22%3A%222024-02-27%2017%3A48%3A19%22%2C%22low_quality%22%3A0%2C%22style_str%22%3Anull%2C%22has_pwd%22%3A1%2C%22newest_article_tool%22%3A0%2C%22user_no%22%3A%223a34b21668e143dcb828393491875444%22%2C%22sessionToken%22%3A%22YmJmYzk3ZWEtZTcyYS00NjkwLWJhNWEtOWYxZjE1MTRlNGFj%22%7D; SESSION=YmJmYzk3ZWEtZTcyYS00NjkwLWJhNWEtOWYxZjE1MTRlNGFj; Hm_lpvt_2d6d056d37910563cdaa290ee2981080=1764072090; Hm_lpvt_58aa18061df7855800f2a1b32d6da7f4=1764072090"
    return cookie

def main():
    # 1. 获取有效Cookie
    cookie = get_valid_cookie()
    
    # 2. 安装依赖提示
    print("\n注意：若未安装requests，请先运行：pip install requests\n")
    time.sleep(1)
    
    # 3. 创建爬虫实例（传入Cookie）
    spider = JiuYanGongSheSpider(cookie)
    
    # 4. 爬取欧陆通（固定目标，避免输入错误）
    stock_name = "沪电股份"
    print(f"\n正在爬取 {stock_name} ...")
    
    # 5. 执行爬取
    result = spider.crawl_stock_posts(stock_name)
    
    # 6. 输出结果
    print("\n" + "="*100)
    print(result)
    
    # 7. 保存到文件
    with open(f'{stock_name}_韭研公社帖子.txt', 'w', encoding='utf-8') as f:
        f.write(result)
    print(f"\n结果已保存到文件: {stock_name}_韭研公社帖子.txt")

if __name__ == "__main__":
    main()