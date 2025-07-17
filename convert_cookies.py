#!/usr/bin/env python3
"""
Cookies转换工具
将浏览器扩展导出的cookies数组转换为我们需要的JSON格式
"""

import json
from cookies_manager import CookiesManager

def convert_browser_cookies_from_text():
    """从文本输入转换cookies"""
    print("🍪 浏览器Cookies转换工具")
    print("=" * 40)
    print("请粘贴浏览器扩展导出的cookies数组:")
    print("(粘贴完成后按回车，然后输入 'END' 并按回车)")
    
    lines = []
    while True:
        line = input()
        if line.strip() == 'END':
            break
        lines.append(line)
    
    cookies_text = '\n'.join(lines)
    
    try:
        # 解析JSON数组
        browser_cookies = json.loads(cookies_text)
        
        if not isinstance(browser_cookies, list):
            print("❌ 输入的不是有效的cookies数组格式")
            return False
        
        # 转换并保存
        success = CookiesManager.save_browser_cookies_to_file(browser_cookies)
        
        if success:
            print("\n🎉 转换成功!")
            print("现在可以运行: python main.py")
        
        return success
        
    except json.JSONDecodeError as e:
        print(f"❌ JSON格式错误: {e}")
        return False
    except Exception as e:
        print(f"❌ 转换失败: {e}")
        return False

def convert_from_file(input_file: str):
    """从文件转换cookies"""
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            browser_cookies = json.load(f)
        
        if not isinstance(browser_cookies, list):
            print("❌ 文件中的不是有效的cookies数组格式")
            return False
        
        success = CookiesManager.save_browser_cookies_to_file(browser_cookies)
        return success
        
    except Exception as e:
        print(f"❌ 从文件转换失败: {e}")
        return False

def main():
    print("🍪 Cookies转换工具")
    print("=" * 30)
    print("选择转换方式:")
    print("1. 从文本输入转换")
    print("2. 从文件转换")
    print("3. 使用示例数据测试")
    
    choice = input("请选择 (1/2/3): ").strip()
    
    if choice == '1':
        convert_browser_cookies_from_text()
    elif choice == '2':
        file_path = input("请输入cookies文件路径: ").strip()
        convert_from_file(file_path)
    elif choice == '3':
        # 使用你提供的示例数据
        example_cookies = [
            {"domain":".x.com","name":"guest_id_marketing","value":"v1%3A175270935747248566"},
            {"domain":".x.com","name":"guest_id_ads","value":"v1%3A175270935747248566"},
            {"domain":".x.com","name":"guest_id","value":"v1%3A175270935747248566"},
            {"domain":".x.com","name":"personalization_id","value":"\"v1_CiGbDylHPHqHcQ8sVptVxA==\""},
            {"domain":".x.com","name":"gt","value":"1945630250127560728"},
            {"domain":"x.com","name":"g_state","value":"{\"i_l\":0}"},
            {"domain":".x.com","name":"kdt","value":"BY1svCIm2kD2DYeH4AQZteNcvS9orEhBHVQdAtS5"},
            {"domain":".x.com","name":"auth_token","value":"c5b8edfbb6390894a5e0a59141b10190cc753ecd"},
            {"domain":".x.com","name":"ct0","value":"6b374de771b1ee842654c894e3691dae8d2ad539b6b719cb7c7110c02a7cc2ba7750b9d7242e8a86ad686c2947bc4c0be54fddeefaf3d204bc1e872e50e7c147375817756b248ee836485bb98e9e0d0d"},
            {"domain":".x.com","name":"att","value":"1-jfC4QuY3mrZvVq1fJ42muAVp8BDqklYogBY6xo2Y"},
            {"domain":"x.com","name":"lang","value":"zh-cn"},
            {"domain":".x.com","name":"twid","value":"u%3D1214500080188682241"},
            {"domain":".x.com","name":"__cf_bm","value":"tS_F0CnR9kVjR69yBUWq2R9W8PiHtBrB4CU3nrLUYKQ-1752712480-1.0.1.1-XtfMhtaVTla39jeqms7CBvX5Ld3M8YWPXOqpQZ1QcgbfAlOknMGT6ZWjGkHvD9LPTlGI_.jlMOSD3wbzTMDhwLhO0evC9eo1MUchx1LrC1k"}
        ]
        
        print("🧪 使用示例数据转换...")
        success = CookiesManager.save_browser_cookies_to_file(example_cookies)
        if success:
            print("🎉 示例转换成功!")
    else:
        print("❌ 无效选择")

if __name__ == "__main__":
    main()
