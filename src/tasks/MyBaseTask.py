import re
import win32gui
import win32con

from ok import BaseTask


class MyBaseTask(BaseTask):
    """基础任务类，提供通用功能和辅助方法"""

    def __init__(self, *args, **kwargs):
        """初始化基础任务"""
        super().__init__(*args, **kwargs)


    def operate(self, func):
        """执行交互操作，阻塞模式"""
        self.executor.interaction.operate(func, block=True)

    def do_mouse_down(self, key):
        """按下鼠标键"""
        self.executor.interaction.do_mouse_down(key=key)

    def do_mouse_up(self, key):
        """释放鼠标键"""
        self.executor.interaction.do_mouse_up(key=key)

    def do_send_key_down(self, key):
        """按下键盘按键"""
        self.executor.interaction.do_send_key_down(key)

    def do_send_key_up(self, key):
        """释放键盘按键"""
        self.executor.interaction.do_send_key_up(key)




