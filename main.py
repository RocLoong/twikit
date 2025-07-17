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
    
    async def scrape_user_tweets(self, username: str, max_tweets: int = 100) -> list:
        """抓取用户推文"""
        if not self.is_logged_in:
            print("❌ 请先登录")
            return []
        
        try:
            print(f"📋 开始抓取 @{username} 的推文...")
            
            # 获取用户信息
            try:
                user = await self.client.get_user_by_screen_name(username)
            except:
                user = await self.client.get_user_by_id(username)
            
            # 获取推文
            tweets = await self.client.get_user_tweets(user.id, 'Tweets', count=20)
            tweets_data = []
            
            count = 0
            while tweets and count < max_tweets:
                for tweet in tweets:
                    if count >= max_tweets:
                        break
                    
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
                
                # 获取下一页
                if count < max_tweets:
                    try:
                        await asyncio.sleep(2)  # 安全延迟
                        tweets = await tweets.next()
                    except:
                        break
            
            print(f"✅ 抓取完成，共获取 {len(tweets_data)} 条推文")
            return tweets_data
            
        except Exception as e:
            print(f"❌ 抓取失败: {e}")
            return []
    
    def save_tweets(self, tweets_data: list, username: str, format_type: str = 'json'):
        """保存推文数据"""
        if not tweets_data:
            print("⚠️ 没有数据可保存")
            return
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        if format_type == 'json':
            filename = f"{username}_{timestamp}.json"
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(tweets_data, f, ensure_ascii=False, indent=2, default=str)
            print(f"💾 已保存到: {filename}")
        
        elif format_type == 'txt':
            filename = f"{username}_{timestamp}.txt"
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

    # 直接使用 cookies.json 文件
    cookies_file = "cookies.json"

    if not os.path.exists(cookies_file):
        print(f"\n❌ 找不到 {cookies_file} 文件")
        print("📖 请先创建cookies.json文件，运行以下命令查看指南:")
        print("   python cookie_helper.py guide")
        print("   python cookie_helper.py sample")
        return
    
    # 创建抓取器并登录
    scraper = BrowserAuthScraper(cookies_file)
    
    print(f"\n🔐 正在登录...")
    if not await scraper.login_with_cookies():
        return
    
    # 显示用户信息
    user_info = scraper.user_info
    # print(f"\n👤 当前用户信息:")
    # print(f"   用户名: @{user_info['screen_name']}")
    # print(f"   显示名: {user_info['name']}")
    # print(f"   粉丝数: {user_info['followers_count']:,}")
    # print(f"   关注数: {user_info['friends_count']:,}")
    
    # 获取抓取参数
    print(f"\n📝 请输入抓取参数:")
    target_user = input("目标用户名: ").strip()
    if not target_user:
        print("❌ 用户名不能为空")
        return
    
    try:
        max_tweets = int(input("最大推文数量 [100]: ").strip() or "100")
    except ValueError:
        max_tweets = 100
    
    format_type = input("输出格式 (json/txt) [json]: ").strip() or "json"
    
    # 开始抓取
    print(f"\n🚀 开始抓取 @{target_user} 的推文...")
    tweets = await scraper.scrape_user_tweets(target_user, max_tweets)
    
    if tweets:
        scraper.save_tweets(tweets, target_user, format_type)
        print(f"\n✅ 抓取完成！")
    else:
        print(f"\n⚠️ 没有获取到推文")

async def command_mode():
    """命令行模式"""
    if len(sys.argv) < 3:
        print("用法: python browser_auth_scraper.py <用户名> <推文数量>")
        print("示例: python browser_auth_scraper.py elonmusk 100")
        print("注意: 请确保当前目录有 cookies.json 文件")
        return

    username = sys.argv[1]
    max_tweets = int(sys.argv[2])
    cookies_file = "cookies.json"  # 固定使用 cookies.json
    
    scraper = BrowserAuthScraper(cookies_file)
    
    if await scraper.login_with_cookies():
        tweets = await scraper.scrape_user_tweets(username, max_tweets)
        if tweets:
            scraper.save_tweets(tweets, username)

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
