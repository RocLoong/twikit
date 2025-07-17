#!/usr/bin/env python3
"""
浏览器授权Twitter抓取工具
专门为浏览器cookies登录设计的简化版本
"""

import asyncio
import json
import os
import sys
from datetime import datetime
import logging
from cookies_manager import CookiesManager

# 处理代理设置
def get_proxy_config():
    """获取代理配置 - 自动检测常用代理"""
    # 首先检查环境变量
    proxy_vars = ['http_proxy', 'https_proxy', 'HTTP_PROXY', 'HTTPS_PROXY', 'all_proxy', 'ALL_PROXY']

    for var in proxy_vars:
        proxy_url = os.environ.get(var)
        if proxy_url:
            print(f"🔧 检测到环境变量代理: {var}={proxy_url}")
            # 转换socks代理格式
            if proxy_url.startswith('socks://'):
                proxy_url = proxy_url.replace('socks://', 'socks5://')
                print(f"🔄 转换代理格式: {proxy_url}")
            return proxy_url

    # 如果没有环境变量，自动尝试常用代理
    print("🔍 未检测到代理环境变量，尝试常用代理...")
    common_proxies = [
        'socks5://127.0.0.1:7897',  # 你的代理端口
        'socks5://127.0.0.1:1080',  # 常用socks5端口
        'socks5://127.0.0.1:7890',  # Clash默认端口
        'http://127.0.0.1:8080',    # 常用http代理
    ]

    for proxy in common_proxies:
        print(f"🧪 尝试代理: {proxy}")
        return proxy  # 直接返回第一个（你的7897端口）

    return None

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logging.getLogger("httpx").setLevel(logging.WARNING)  # 屏蔽httpx的INFO日志
logger = logging.getLogger(__name__)

class BrowserAuthScraper:
    """基于浏览器授权的Twitter抓取器"""
    
    def __init__(self, cookies_file: str = "cookies.json"):
        self.cookies_file = cookies_file
        self.client = None
        self.user_info = None
        self.is_logged_in = False
    
    async def login_with_cookies(self) -> bool:
        """使用cookies登录"""
        from twikit import Client

        if not os.path.exists(self.cookies_file):
            print(f"❌ Cookies文件不存在: {self.cookies_file}")
            print("请先运行: python cookie_helper.py guide")
            return False

        try:
            print(f"🍪 加载cookies文件: {self.cookies_file}")

            # 使用cookies管理器
            cookies_manager = CookiesManager(self.cookies_file)
            if not cookies_manager.load_cookies():
                return False

            cookies = cookies_manager.get_cookies()

            # 创建客户端 - 使用系统代理
            proxy_config = get_proxy_config()
            if proxy_config:
                print(f"🔧 创建客户端 (使用代理: {proxy_config})...")
                self.client = Client('en-US', proxy=proxy_config)
            else:
                print("🔧 创建客户端 (无代理)...")
                self.client = Client('en-US')
            self.client.set_cookies(cookies)

            # 设置CSRF头
            if 'ct0' in cookies:
                self.client.http.headers['x-csrf-token'] = cookies['ct0']
                print(f"🛡️ 设置CSRF令牌: {cookies['ct0'][:20]}...")
            
            # 验证登录状态 - 直接尝试搜索推文
            print("🔍 验证登录状态...")

            # 添加调试信息
            print(f"🔍 DEBUG: cookies字段: {list(cookies.keys())}")
            print(f"🔍 DEBUG: auth_token长度: {len(cookies.get('auth_token', ''))}")
            print(f"🔍 DEBUG: 代理设置: {proxy_config}")

            # 先测试网络连接
            try:
                print("🌐 测试基础网络连接...")
                import httpx
                async with httpx.AsyncClient(proxy=proxy_config, timeout=10) as test_client:
                    resp = await test_client.get("https://httpbin.org/ip")
                    print(f"✅ 网络连接正常: {resp.json()}")
            except Exception as net_e:
                print(f"❌ 网络连接失败: {net_e}")
                print(f"🔍 错误类型: {type(net_e).__name__}")
                print("🚨 这是网络/代理问题，不是cookies问题!")
                return False

            try:
                print("🧪 测试推文搜索...")
                tweets = await self.client.search_tweet('hello', 'Latest', count=1)

                print(f"🔍 DEBUG: 搜索结果类型: {type(tweets)}")
                print(f"🔍 DEBUG: 搜索结果长度: {len(tweets) if tweets else 'None'}")

                if tweets and len(tweets) > 0:
                    print("✅ Cookies验证成功! 可以正常访问Twitter")
                    print("🎉 这说明cookies是有效的!")
                    print(f"📝 找到 {len(tweets)} 条推文")

                    # 显示第一条推文信息
                    first_tweet = tweets[0]
                    print(f"   示例: {first_tweet.text[:50]}...")

                    self.user_info = {
                        'id': 'verified',
                        'screen_name': 'verified_user',
                        'name': 'Verified User',
                        'followers_count': 0,
                        'friends_count': 0
                    }
                    self.is_logged_in = True

                    # 保存更新后的cookies
                    self.client.save_cookies(self.cookies_file)
                    return True
                else:
                    print("❌ 搜索推文无结果")
                    print("🔍 尝试其他搜索词...")

                    # 尝试搜索更常见的词
                    for search_term in ['twitter', 'news', 'python']:
                        print(f"� 尝试搜索: {search_term}")
                        try:
                            test_tweets = await self.client.search_tweet(search_term, 'Latest', count=1)
                            if test_tweets and len(test_tweets) > 0:
                                print(f"✅ 搜索 '{search_term}' 成功! 找到 {len(test_tweets)} 条推文")
                                print("🎉 Cookies是有效的!")
                                self.is_logged_in = True
                                return True
                        except Exception as e:
                            print(f"❌ 搜索 '{search_term}' 失败: {e}")

                    print("🤔 所有搜索都无结果，可能是Twitter限制或cookies问题")
                    return False

            except Exception as e:
                print(f"❌ 推文搜索失败: {e}")
                print(f"� 错误类型: {type(e).__name__}")

                if 'timeout' in str(e).lower() or 'ConnectTimeout' in str(e):
                    print("🚨 这是网络连接问题!")
                elif '401' in str(e) or '403' in str(e) or 'unauthorized' in str(e).lower():
                    print("🚨 这是cookies认证问题!")
                else:
                    print("🤔 其他问题，可能是cookies或API限制")

                return False
                
        except Exception as e:
            print(f"❌ 登录失败: {e}")
            return False
    

    
    async def _get_user_info(self) -> dict:
        """获取用户信息 - 简化版本"""
        # 现在这个方法主要用于向后兼容
        return self.user_info if hasattr(self, 'user_info') and self.user_info else None
    
    async def scrape_user_tweets(self, username: str, max_tweets: int = 100, start_date: str = None, end_date: str = None, continue_from_checkpoint: bool = False) -> list:
        """抓取用户推文，支持时间范围和检查点"""
        if not self.is_logged_in:
            print("❌ 请先登录")
            return []

        # 检查点文件处理
        checkpoint_dir = "checkpoints"
        os.makedirs(checkpoint_dir, exist_ok=True)
        checkpoint_file = os.path.join(checkpoint_dir, f"{username}_cursor.txt")
        
        initial_cursor = None
        if continue_from_checkpoint and os.path.exists(checkpoint_file):
            with open(checkpoint_file, 'r') as f:
                initial_cursor = f.read().strip()
            print(f"ℹ️ 从检查点加载 cursor: {initial_cursor[:20]}...")

        try:
            s_date = datetime.strptime(start_date, '%Y-%m-%d') if start_date else None
            e_date = datetime.strptime(end_date, '%Y-%m-%d') if end_date else None

            print(f"📋 开始抓取 @{username} 的推文...")
            if s_date or e_date:
                print(f"   时间范围: {start_date or '...'} -> {end_date or '...'}")

            user = await self.client.get_user_by_screen_name(username)
            # 使用 initial_cursor 开始抓取
            tweets = await self.client.get_user_tweets(user.id, 'Tweets', count=40, cursor=initial_cursor)
            tweets_data = []
            
            count = 0
            stop_scraping = False
            while tweets and count < max_tweets and not stop_scraping:
                # 在每次循环开始时，保存当前的cursor作为检查点
                if tweets.next_cursor:
                    with open(checkpoint_file, 'w') as f:
                        f.write(tweets.next_cursor)

                for tweet in tweets:
                    if count >= max_tweets:
                        break

                    tweet_time = tweet.created_at
                    if isinstance(tweet_time, str):
                        try:
                            tweet_time = datetime.strptime(tweet_time, '%a %b %d %H:%M:%S %z %Y')
                        except ValueError:
                            tweet_time = datetime.fromisoformat(tweet_time.replace('Z', '+00:00'))
                    
                    if s_date and tweet_time.date() < s_date.date():
                        print(f"ℹ️ 推文 ({tweet.created_at.date()}) 早于开始日期 ({start_date})，停止抓取。")
                        stop_scraping = True
                        break

                    if (not s_date or tweet_time.date() >= s_date.date()) and \
                       (not e_date or tweet_time.date() <= e_date.date()):
                        
                        tweet_data = {
                            'id': tweet.id,
                            'text': tweet.text,
                            'created_at': tweet.created_at,
                            'user_name': user.name,
                            'user_screen_name': user.screen_name,
                            'retweet_count': getattr(tweet, 'retweet_count', 0),
                            'favorite_count': getattr(tweet, 'favorite_count', 0),
                            'url': f"https://twitter.com/{user.screen_name}/status/{tweet.id}"
                        }
                        tweets_data.append(tweet_data)
                        count += 1

                if stop_scraping:
                    break

                if count < max_tweets:
                    retries = 3
                    for attempt in range(retries):
                        try:
                            print(f"    ...已获取 {count} 条有效推文，等待 1.5 秒后继续翻页...")
                            await asyncio.sleep(1.5)
                            tweets = await tweets.next()
                            break
                        except Exception as page_e:
                            if "429" in str(page_e) or "rate limit" in str(page_e).lower():
                                wait_time = 60 * (attempt + 1)
                                print(f"️️️⚠️ 触发速率限制！第 {attempt + 1}/{retries} 次重试，将暂停 {wait_time} 秒...")
                                await asyncio.sleep(wait_time)
                            else:
                                print(f"❌ 无法获取下一页，错误类型: {type(page_e).__name__}, 详情: {page_e}")
                                print("⚠️ 可能是已到达推文末尾或遇到非速率限制的API错误。")
                                tweets = None
                                break
                    
                    if tweets is None:
                        break
            
            if s_date or e_date:
                final_message = f"✅ 抓取完成，共获取 {len(tweets_data)} 条在指定时间范围内的推文"
            else:
                final_message = f"✅ 抓取完成，共获取 {len(tweets_data)} 条推文"
                if len(tweets_data) < max_tweets:
                    final_message += f" (目标 {max_tweets} 条，可能已到达用户推文末尾或触发API限制)"
            
            print(final_message)
            # 任务成功完成后，删除检查点文件
            if os.path.exists(checkpoint_file):
                os.remove(checkpoint_file)
                print("ℹ️ 任务完成，已删除检查点文件。")

            return tweets_data
            
        except Exception as e:
            print(f"❌ 抓取失败: {e}")
            return []
    
    def save_tweets(self, tweets_data: list, username: str, format_type: str = 'json'):
        """保存推文数据到指定文件夹"""
        if not tweets_data:
            print("⚠️ 没有数据可保存")
            return

        # 1. 定义并创建主输出目录和用户子目录
        output_dir = "downloaded_tweets"
        user_dir = os.path.join(output_dir, username)
        os.makedirs(user_dir, exist_ok=True)  # exist_ok=True 避免在文件夹已存在时报错

        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        base_filename = f"{username}_{timestamp}"

        if format_type == 'json':
            filename = os.path.join(user_dir, f"{base_filename}.json")
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(tweets_data, f, ensure_ascii=False, indent=2, default=str)
            print(f"💾 已保存到: {filename}")

        elif format_type == 'txt':
            filename = os.path.join(user_dir, f"{base_filename}.txt")
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(f"@{username} 的推文合集\n")
                f.write(f"抓取时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"总计: {len(tweets_data)} 条推文\n")
                f.write("=" * 50 + "\n\n")

                for i, tweet in enumerate(tweets_data, 1):
                    f.write(f"推文 {i}:\n")
                    f.write(f"时间: {tweet['created_at']}\n")
                    f.write(f"内容: {tweet['text']}\n")
                    f.write(f"链接: {tweet['url']}\n")
                    f.write("-" * 30 + "\n\n")

            print(f"💾 已保存到: {filename}")

async def interactive_mode():
    """交互式模式"""
    print("🍪 浏览器授权Twitter抓取工具")
    print("=" * 50)

    cookies_file = "cookies.json"
    if not os.path.exists(cookies_file):
        print(f"\n❌ 找不到 {cookies_file} 文件")
        print("📖 请先运行: python cookie_helper.py guide")
        return
    
    scraper = BrowserAuthScraper(cookies_file)
    print(f"\n🔐 正在登录...")
    if not await scraper.login_with_cookies():
        return
    
    print(f"\n📝 请输入抓取参数:")
    target_user = input("目标用户名: ").strip()
    if not target_user:
        print("❌ 用户名不能为空")
        return

    # 检查是否存在检查点，并询问用户是否继续
    continue_from_checkpoint = False
    checkpoint_file = f"checkpoints/{target_user}_cursor.txt"
    if os.path.exists(checkpoint_file):
        continue_choice = input(f"发现 @{target_user} 的检查点，是否继续？(y/N): ").strip().lower()
        if continue_choice == 'y':
            continue_from_checkpoint = True
    
    try:
        max_tweets = int(input("最大推文数量 (默认1000): ").strip() or "1000")
    except ValueError:
        max_tweets = 1000

    start_date = input("开始日期 (YYYY-MM-DD, 可选): ").strip()
    end_date = input("结束日期 (YYYY-MM-DD, 可选): ").strip()
    
    # 使用数字选择文件格式
    print("请选择输出格式:")
    print("  1: TXT")
    print("  2: JSON (默认)")
    format_choice = input("输入选项 [2]: ").strip()

    if format_choice == '1':
        format_type = 'txt'
    else:
        format_type = 'json'
    
    print(f"\n🚀 开始抓取 @{target_user} 的推文...")
    tweets = await scraper.scrape_user_tweets(target_user, max_tweets, start_date, end_date, continue_from_checkpoint)
    
    if tweets:
        scraper.save_tweets(tweets, target_user, format_type)
        print(f"\n✅ 抓取完成！")
    else:
        print(f"\n⚠️ 没有获取到符合条件的推文")

async def command_mode():
    """命令行模式"""
    # 用法: python main.py <用户名> <推文数量> [开始日期] [结束日期]
    # 示例: python main.py elonmusk 1000 2023-01-01 2023-12-31
    if len(sys.argv) < 3:
        print("用法: python main.py <用户名> <推文数量> [开始日期] [结束日期]")
        print("示例: python main.py elonmusk 1000 2023-01-01 2023-12-31")
        print("注意: 请确保当前目录有 cookies.json 文件")
        return

    username = sys.argv[1]
    max_tweets = int(sys.argv[2])
    start_date = sys.argv[3] if len(sys.argv) > 3 else None
    end_date = sys.argv[4] if len(sys.argv) > 4 else None
    cookies_file = "cookies.json"
    
    scraper = BrowserAuthScraper(cookies_file)
    
    if await scraper.login_with_cookies():
        tweets = await scraper.scrape_user_tweets(username, max_tweets, start_date, end_date)
        if tweets:
            # 命令行模式默认保存为json
            scraper.save_tweets(tweets, username, 'json')

async def main():
    try:
        if len(sys.argv) == 1:
            # 交互式模式
            await interactive_mode()
        else:
            # 命令行模式
            await command_mode()
    except KeyboardInterrupt:
        print("\n👋 用户取消操作")
    except Exception as e:
        print(f"❌ 程序错误: {e}")

if __name__ == "__main__":
    asyncio.run(main())
