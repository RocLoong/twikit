#!/usr/bin/env python3
"""
Cookies管理模块
处理Twitter cookies的加载、验证和管理
"""

import json
import os
from typing import Dict, Optional


class CookiesManager:
    """Cookies管理器"""
    
    def __init__(self, cookies_file: str = "cookies.json"):
        self.cookies_file = cookies_file
        self.cookies_data = {}
        self.is_valid = False
    
    def load_cookies(self) -> bool:
        """加载cookies文件"""
        if not os.path.exists(self.cookies_file):
            print(f"❌ Cookies文件不存在: {self.cookies_file}")
            return False
        
        try:
            with open(self.cookies_file, 'r', encoding='utf-8') as f:
                raw_data = json.load(f)
            
            # 处理不同格式的cookies
            self.cookies_data = self._process_cookies_format(raw_data)
            
            if self.cookies_data:
                print(f"✅ 成功加载cookies: {list(self.cookies_data.keys())}")
                self.is_valid = self._validate_cookies()
                return self.is_valid
            else:
                print("❌ Cookies格式无效")
                return False
                
        except Exception as e:
            print(f"❌ 读取cookies文件失败: {e}")
            return False
    
    def _process_cookies_format(self, raw_data) -> Dict[str, str]:
        """处理不同格式的cookies数据"""
        if isinstance(raw_data, dict):
            # 直接的键值对格式
            return raw_data
        elif isinstance(raw_data, list):
            # 数组格式，转换为键值对
            cookies = {}
            for item in raw_data:
                if isinstance(item, dict) and 'name' in item and 'value' in item:
                    cookies[item['name']] = item['value']
            return cookies
        else:
            print(f"❌ 不支持的cookies格式: {type(raw_data)}")
            return {}
    
    def _validate_cookies(self) -> bool:
        """验证cookies的有效性"""
        if not self.cookies_data:
            return False
        
        # 检查必需字段
        required_fields = ['auth_token']
        optional_fields = ['ct0']
        
        has_auth_token = 'auth_token' in self.cookies_data
        has_ct0 = 'ct0' in self.cookies_data
        
        if not has_auth_token:
            print("❌ 缺少必需字段: auth_token")
            return False
        
        auth_token = self.cookies_data['auth_token']
        if not auth_token or len(auth_token) < 10:
            print("❌ auth_token格式无效")
            return False
        
        print(f"✅ Cookies验证通过:")
        print(f"   - auth_token: {len(auth_token)} 字符")
        if has_ct0:
            print(f"   - ct0: {len(self.cookies_data['ct0'])} 字符")
        
        # 显示额外字段
        extra_fields = [k for k in self.cookies_data.keys() 
                       if k not in required_fields + optional_fields]
        if extra_fields:
            print(f"   - 额外字段: {', '.join(extra_fields)}")
        
        return True
    
    def get_cookies(self) -> Dict[str, str]:
        """获取处理后的cookies"""
        return self.cookies_data.copy() if self.is_valid else {}
    
    def get_auth_token(self) -> Optional[str]:
        """获取auth_token"""
        return self.cookies_data.get('auth_token') if self.is_valid else None
    
    def get_ct0(self) -> Optional[str]:
        """获取ct0令牌"""
        return self.cookies_data.get('ct0') if self.is_valid else None
    
    def has_field(self, field_name: str) -> bool:
        """检查是否包含指定字段"""
        return field_name in self.cookies_data if self.is_valid else False
    
    def get_cookies_info(self) -> Dict:
        """获取cookies信息摘要"""
        if not self.is_valid:
            return {'valid': False, 'error': 'Cookies未加载或无效'}
        
        return {
            'valid': True,
            'total_fields': len(self.cookies_data),
            'fields': list(self.cookies_data.keys()),
            'auth_token_length': len(self.cookies_data.get('auth_token', '')),
            'has_ct0': 'ct0' in self.cookies_data,
            'file_path': self.cookies_file
        }
    
    def save_cookies(self, new_cookies: Dict[str, str]) -> bool:
        """保存更新后的cookies"""
        try:
            # 合并新的cookies
            self.cookies_data.update(new_cookies)
            
            with open(self.cookies_file, 'w', encoding='utf-8') as f:
                json.dump(self.cookies_data, f, ensure_ascii=False, indent=2)
            
            print(f"✅ Cookies已更新保存: {self.cookies_file}")
            return True
            
        except Exception as e:
            print(f"❌ 保存cookies失败: {e}")
            return False
    
    @staticmethod
    def create_sample_cookies(file_path: str = "cookies_sample.json") -> bool:
        """创建示例cookies文件"""
        sample_cookies = {
            "auth_token": "请替换为真实的auth_token值",
            "ct0": "请替换为真实的ct0值"
        }
        
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(sample_cookies, f, ensure_ascii=False, indent=2)
            
            print(f"✅ 示例cookies文件已创建: {file_path}")
            print("📝 请编辑此文件，替换为真实的cookies值")
            return True
            
        except Exception as e:
            print(f"❌ 创建示例文件失败: {e}")
            return False
    
    @staticmethod
    def validate_cookies_file(file_path: str) -> bool:
        """静态方法：验证cookies文件"""
        manager = CookiesManager(file_path)
        return manager.load_cookies()

    @staticmethod
    def convert_browser_cookies(browser_cookies_array: list) -> Dict[str, str]:
        """转换浏览器扩展导出的cookies数组格式"""
        cookies = {}

        for cookie in browser_cookies_array:
            if isinstance(cookie, dict) and 'name' in cookie and 'value' in cookie:
                cookies[cookie['name']] = cookie['value']

        print(f"✅ 转换浏览器cookies: {len(cookies)} 个字段")
        print(f"🔑 包含字段: {list(cookies.keys())}")

        return cookies

    @staticmethod
    def save_browser_cookies_to_file(browser_cookies_array: list, file_path: str = "cookies.json") -> bool:
        """将浏览器cookies数组保存为JSON文件"""
        try:
            cookies = CookiesManager.convert_browser_cookies(browser_cookies_array)

            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(cookies, f, ensure_ascii=False, indent=2)

            print(f"✅ 浏览器cookies已保存到: {file_path}")

            # 验证保存的文件
            if CookiesManager.validate_cookies_file(file_path):
                print("✅ 保存的cookies文件验证通过")
                return True
            else:
                print("❌ 保存的cookies文件验证失败")
                return False

        except Exception as e:
            print(f"❌ 保存浏览器cookies失败: {e}")
            return False


def main():
    """测试cookies管理器"""
    print("🍪 Cookies管理器测试")
    print("=" * 30)
    
    # 测试加载cookies
    manager = CookiesManager()
    
    if manager.load_cookies():
        info = manager.get_cookies_info()
        print(f"\n📊 Cookies信息:")
        for key, value in info.items():
            print(f"   {key}: {value}")
        
        print(f"\n🔑 auth_token: {manager.get_auth_token()[:20]}...")
        if manager.has_field('ct0'):
            print(f"🛡️ ct0: {manager.get_ct0()[:20]}...")
    else:
        print("\n❌ Cookies加载失败")
        print("💡 创建示例文件...")
        CookiesManager.create_sample_cookies()


if __name__ == "__main__":
    main()
