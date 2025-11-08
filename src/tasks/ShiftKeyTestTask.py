#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Shift键测试任务 - 前台pynput解决方案
专门针对需要窗口在前台的游戏优化
"""

import time
import win32gui
from src.tasks.MyBaseTask import MyBaseTask

# 尝试导入pynput，如果失败则设为None
try:
    from pynput.keyboard import Controller, Key
    PYNPUT_AVAILABLE = True
except ImportError:
    Controller = None
    Key = None
    PYNPUT_AVAILABLE = False


class ShiftKeyTestTask(MyBaseTask):
    """Shift键测试任务 - 前台pynput解决方案"""
    
    # 常量定义
    DEFAULT_DOWN_TIME = 0.2  # 默认按键按下时间（秒）
    WINDOW_ACTIVATE_DELAY = 1.0  # 窗口激活后等待时间（秒）
    TEST_INTERVAL = 1.0  # 测试间隔时间（秒）
    
    # 游戏窗口标题关键词
    GAME_WINDOW_KEYWORDS = ['二重螺旋', '游戏', 'Game']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.name = "Shift键测试任务（前台模式）"
        self.description = "使用前台pynput方法测试shift键，确保游戏窗口在前台"
        self.game_hwnd = None
        self.keyboard = None
        
        # 初始化pynput键盘控制器
        self._init_keyboard()
    
    def _init_keyboard(self):
        """初始化pynput键盘控制器"""
        if PYNPUT_AVAILABLE:
            try:
                self.keyboard = Controller()
                self.log_info("✓ pynput键盘控制器初始化成功", notify=False)
            except Exception as e:
                self.log_info(f"⚠ pynput键盘控制器初始化失败: {str(e)}", notify=False)
                self.keyboard = None
        else:
            self.log_info("⚠ pynput库未安装，将使用标准方法", notify=False)
            self.keyboard = None
    
    def run(self):
        """运行任务"""
        self.log_info("开始Shift键测试任务（前台模式）", notify=True)
        
        try:
            # 确保游戏窗口在前台
            if not self.ensure_game_foreground():
                self.log_info("❌ 无法确保游戏窗口在前台，任务终止", notify=True)
                return
            
            # 测试shift键
            self.test_shift_key()
            
            self.log_info("✅ Shift键测试任务完成", notify=True)
        except Exception as e:
            self.log_info(f"❌ 任务执行出错: {str(e)}", notify=True)
            raise
    
    def ensure_game_foreground(self):
        """确保游戏窗口在前台
        
        Returns:
            bool: 如果游戏窗口在前台或成功激活，返回True；否则返回False
        """
        self.log_info("检查游戏窗口状态...", notify=False)
        
        # 查找游戏窗口
        game_window = self._find_game_window()
        if not game_window:
            self.log_info("❌ 未找到游戏窗口", notify=False)
            return False
        
        self.game_hwnd, title = game_window
        self.log_info(f"找到游戏窗口: {title} (句柄: {self.game_hwnd})", notify=False)
        
        # 检查窗口是否已在前台
        if self._is_foreground():
            self.log_info("✓ 游戏窗口已在前台", notify=False)
            return True
        
        # 尝试激活窗口
        self.log_info("⚠ 游戏窗口不在前台，尝试激活...", notify=False)
        return self._activate_window()
    
    def _find_game_window(self):
        """查找游戏窗口
        
        Returns:
            tuple: (hwnd, title) 或 None
        """
        windows = []
        
        def enum_windows_proc(hwnd, _):
            if win32gui.IsWindowVisible(hwnd):
                title = win32gui.GetWindowText(hwnd)
                if title and any(keyword in title for keyword in self.GAME_WINDOW_KEYWORDS):
                    windows.append((hwnd, title))
            return True
        
        win32gui.EnumWindows(enum_windows_proc, None)
        return windows[0] if windows else None
    
    def _is_foreground(self):
        """检查游戏窗口是否在前台
        
        Returns:
            bool: 如果游戏窗口在前台，返回True
        """
        if self.game_hwnd is None:
            return False
        return win32gui.GetForegroundWindow() == self.game_hwnd
    
    def _activate_window(self):
        """激活游戏窗口到前台
        
        Returns:
            bool: 如果成功激活，返回True；否则返回False
        """
        try:
            win32gui.SetForegroundWindow(self.game_hwnd)
            time.sleep(self.WINDOW_ACTIVATE_DELAY)
            
            # 再次检查
            if self._is_foreground():
                self.log_info("✓ 游戏窗口已激活到前台", notify=False)
                return True
            else:
                current_title = win32gui.GetWindowText(win32gui.GetForegroundWindow())
                self.log_info(f"❌ 无法激活游戏窗口到前台", notify=False)
                self.log_info(f"当前前台窗口: {current_title}", notify=False)
                return False
        except Exception as e:
            self.log_info(f"❌ 激活窗口时出错: {str(e)}", notify=False)
            return False
    
    def test_shift_key(self):
        """测试shift键 - 使用两种方法测试"""
        self.log_info("开始测试shift键...", notify=False)
        
        # 确保窗口在前台
        if not self.check_foreground():
            self.log_info("⚠ 警告：游戏窗口不在前台，测试可能无效", notify=False)
            return
        
        # 方法1: 使用标准方法发送shift键
        self.log_info("方法1: 使用标准方法发送shift键", notify=False)
        self._send_shift_standard(self.DEFAULT_DOWN_TIME)
        self.sleep(self.TEST_INTERVAL)
        
        # 方法2: 使用便捷方法（pynput）
        self.log_info("方法2: 使用便捷方法发送shift键", notify=False)
        self.send_shift()
        self.sleep(self.TEST_INTERVAL)
        
        self.log_info("✓ shift键测试完成", notify=False)
    
    def check_foreground(self):
        """检查窗口是否在前台
        
        Returns:
            bool: 如果游戏窗口在前台，返回True
        """
        return self._is_foreground()
    
    # ========== 便捷方法 ==========
    
    def send_shift(self, down_time=None):
        """发送shift键（按下并抬起）
        
        Args:
            down_time (float, optional): 按键按下时间（秒），默认使用 DEFAULT_DOWN_TIME
        
        Returns:
            bool: 如果成功发送，返回True；否则返回False
        """
        if down_time is None:
            down_time = self.DEFAULT_DOWN_TIME
        
        if not self.check_foreground():
            self.log_info("⚠ 警告：游戏窗口不在前台，按键可能无效", notify=False)
            return False
        
        # 优先使用pynput发送shift键（更可靠）
        if self._send_shift_with_pynput(down_time):
            return True
        
        # 回退到标准方法
        self.log_info("使用标准方法发送shift键...", notify=False)
        self._send_shift_standard(down_time)
        return True
    
    def _send_shift_standard(self, down_time):
        """使用标准方法发送shift键（通过do_send_key_down/up）
        
        Args:
            down_time (float): 按键按下时间（秒）
        """
        self.do_send_key_down('SHIFT')
        time.sleep(down_time)
        self.do_send_key_up('SHIFT')
    
    def _send_shift_with_pynput(self, down_time):
        """使用pynput发送shift键
        
        Args:
            down_time (float): 按键按下时间（秒）
        
        Returns:
            bool: 如果成功发送，返回True；否则返回False
        """
        if self.keyboard is None or not PYNPUT_AVAILABLE:
            return False
        
        try:
            self.keyboard.press(Key.shift)
            time.sleep(down_time)
            self.keyboard.release(Key.shift)
            self.log_info("✓ pynput发送shift键成功", notify=False)
            return True
        except Exception as e:
            self.log_info(f"⚠ pynput发送失败: {str(e)}", notify=False)
            return False

if __name__ == "__main__":
    task = ShiftKeyTestTask()
    task.run()