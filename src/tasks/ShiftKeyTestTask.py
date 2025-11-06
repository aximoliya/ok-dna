#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Shift键测试任务 - 前台pynput解决方案
专门针对需要窗口在前台的游戏优化
"""

import time
import win32gui
from src.tasks.MyBaseTask import MyBaseTask

class ShiftKeyTestTask(MyBaseTask):
    """Shift键测试任务 - 前台pynput解决方案"""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.name = "Shift键测试任务（前台模式）"
        self.description = "使用前台pynput方法测试shift键，确保游戏窗口在前台"
        self.game_hwnd = None
        # 初始化配置，确保_log方法正常工作
        if not hasattr(self, 'config') or self.config is None:
            self.config = {"启用日志": True}
        # 初始化pynput键盘控制器
        try:
            from pynput.keyboard import Controller
            self.keyboard = Controller()
        except ImportError:
            self.log_info("⚠ pynput库未安装，将使用标准方法")
            self.keyboard = None
    
    def run(self):
        """运行任务"""
        self.log_info("开始Shift键测试任务（前台模式）")
        
        # 确保游戏窗口在前台
        if not self.ensure_game_foreground():
            self.log_info("❌ 无法确保游戏窗口在前台，任务终止")
            return
        
        # 测试shift键
        self.test_shift_key()
        
        # 测试组合键
        self.test_combination_keys()
        
        self.log_info("✅ Shift键测试任务完成")
    
    def ensure_game_foreground(self):
        """确保游戏窗口在前台"""
        self.log_info("检查游戏窗口状态...")
        
        # 查找游戏窗口
        windows = []
        def enum_windows_proc(hwnd, _):
            if win32gui.IsWindowVisible(hwnd):
                title = win32gui.GetWindowText(hwnd)
                if title and ('二重螺旋' in title or '游戏' in title or 'Game' in title):
                    windows.append((hwnd, title))
            return True
        
        win32gui.EnumWindows(enum_windows_proc, None)
        
        if not windows:
            self.log_info("❌ 未找到游戏窗口")
            return False
        
        self.game_hwnd, title = windows[0]
        self.log_info(f"找到游戏窗口: {title} (句柄: {self.game_hwnd})")
        
        # 检查窗口是否在前台
        foreground_hwnd = win32gui.GetForegroundWindow()
        if foreground_hwnd == self.game_hwnd:
            self.log_info("✓ 游戏窗口已在前台")
            return True
        else:
            self.log_info("⚠ 游戏窗口不在前台，尝试激活...")
            
            # 尝试激活窗口
            win32gui.SetForegroundWindow(self.game_hwnd)
            time.sleep(1)
            
            # 再次检查
            foreground_hwnd = win32gui.GetForegroundWindow()
            if foreground_hwnd == self.game_hwnd:
                self.log_info("✓ 游戏窗口已激活到前台")
                return True
            else:
                self.log_info("❌ 无法激活游戏窗口到前台")
                self.log_info(f"当前前台窗口: {win32gui.GetWindowText(foreground_hwnd)}")
                return False
    
    def test_shift_key(self):
        """测试shift键 - 使用标准方法"""
        self.log_info("测试shift键...")
        
        # 确保窗口在前台
        if not self.check_foreground():
            return
        
        # 方法1: 使用标准方法发送shift键
        self.log_info("方法1: 使用标准方法发送shift键")
        self.do_send_key_shift()
        time.sleep(1)
        
        # 方法2: 使用便捷方法
        self.log_info("方法2: 使用便捷方法发送shift键")
        self.send_shift()
        time.sleep(1)
        
        # 方法3: 测试组合键
        self.log_info("方法3: 测试shift+W组合键")
        self.send_w_with_shift()
        time.sleep(1)
    
    def test_combination_keys(self):
        """测试组合键 - 使用标准方法"""
        self.log_info("测试组合键...")
        
        # 确保窗口在前台
        if not self.check_foreground():
            return
        
        # 测试所有shift组合键
        combinations = [
            ("W", self.send_w_with_shift),
            ("A", self.send_a_with_shift),
            ("S", self.send_s_with_shift),
            ("D", self.send_d_with_shift),
        ]
        
        for key_name, method in combinations:
            self.log_info(f"测试shift+{key_name}组合键")
            if method():
                self.log_info(f"✓ shift+{key_name}组合键测试成功")
            else:
                self.log_info(f"❌ shift+{key_name}组合键测试失败")
            time.sleep(1)
    
    def check_foreground(self):
        """检查窗口是否在前台"""
        if self.game_hwnd is None:
            return False
        
        foreground_hwnd = win32gui.GetForegroundWindow()
        if foreground_hwnd != self.game_hwnd:
            self.log_info("⚠ 警告：游戏窗口不在前台，按键可能无效")
            return False
        
        return True
    
    # ========== 便捷方法 ==========
    
    def send_shift(self):
        """发送shift键（按下并抬起）"""
        if self.check_foreground():
            # 使用pynput直接发送shift键（更可靠）
            self.log_info("使用pynput直接发送shift键...")
            try:
                from pynput.keyboard import Key
                self.keyboard.press(Key.shift)
                time.sleep(0.2)  # 增加按下时间
                self.keyboard.release(Key.shift)
                self.log_info("✓ pynput直接发送shift键成功")
                return True
            except Exception as e:
                self.log_info(f"⚠ pynput发送失败: {str(e)}")
                # 失败时回退到标准方法
                self.log_info("回退到标准方法...")
                self.do_send_key_shift(down_time=0.2)  # 增加按下时间
                return True
        return False
    
    def send_shift_down(self):
        """按下shift键"""
        if self.check_foreground():
            try:
                from pynput.keyboard import Key
                self.keyboard.press(Key.shift)
                self.log_info("✓ pynput shift键按下")
                return True
            except Exception:
                # 回退到标准方法
                self.do_send_key_down('SHIFT')
                return True
        return False
    
    def send_shift_up(self):
        """抬起shift键"""
        if self.check_foreground():
            try:
                from pynput.keyboard import Key
                self.keyboard.release(Key.shift)
                self.log_info("✓ pynput shift键释放")
                return True
            except Exception:
                # 回退到标准方法
                self.do_send_key_up('SHIFT')
                return True
        return False
    
    def send_key_with_shift(self, key):
        """发送shift+指定键的组合键"""
        if self.check_foreground():
            self.log_info(f"发送shift+{key}组合键...")
            try:
                from pynput.keyboard import Key
                # 使用pynput的上下文管理器发送组合键
                with self.keyboard.pressed(Key.shift):
                    self.keyboard.press(key)
                    time.sleep(0.1)
                    self.keyboard.release(key)
                    time.sleep(0.1)
                self.log_info(f"✓ shift+{key}组合键发送成功")
                return True
            except Exception as e:
                self.log_info(f"⚠ pynput组合键失败: {str(e)}")
                # 回退到分步方法
                self.send_shift_down()
                self.send_key(key)
                self.send_shift_up()
                return True
        return False
    
    def send_w_with_shift(self):
        """发送shift+W组合键"""
        return self.send_key_with_shift('w')
    
    def send_a_with_shift(self):
        """发送shift+A组合键"""
        return self.send_key_with_shift('a')
    
    def send_s_with_shift(self):
        """发送shift+S组合键"""
        return self.send_key_with_shift('s')
    
    def send_d_with_shift(self):
        """发送shift+D组合键"""
        return self.send_key_with_shift('d')
    
    def send_key(self, key):
        """发送单个键 - 使用标准方法"""
        if self.check_foreground():
            # 对于普通按键，使用标准方法
            if len(key) == 1 and key.isalpha():
                self.do_send_key_down(key.upper())
                self.sleep(0.1)  # 短暂的按键时间
                self.do_send_key_up(key.upper())
            else:
                # 对于特殊按键，使用MyBaseTask的标准方法
                self.do_send_key_down(key)
                self.sleep(0.1)
                self.do_send_key_up(key)
            return True
        return False
    
    def ensure_game_active(self):
        """确保游戏窗口激活（便捷方法）"""
        return self.ensure_game_foreground()

if __name__ == "__main__":
    task = ShiftKeyTestTask()
    task.run()