import re
import win32gui
import win32con

from ok import BaseTask

class MyBaseTask(BaseTask):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def _log(self, message, notify=False):
        """
        根据配置决定是否记录日志
        """
        config = getattr(self, 'config', {})
        if config is None:
            config = {}
        if config.get("启用日志", True):
            self.log_info(message, notify=notify)

    def operate(self, func):
        self.executor.interaction.operate(func, block=True)

    def do_mouse_down(self, key):
        self.executor.interaction.do_mouse_down(key=key)

    def do_mouse_up(self, key):
        self.executor.interaction.do_mouse_up(key=key)

    def do_send_key_down(self, key):
        self.executor.interaction.do_send_key_down(key)

    def do_send_key_up(self, key):
        self.executor.interaction.do_send_key_up(key)

    def do_send_key_shift(self,down_time=0.1):
        """
        专门发送shift键的方法
        既然WASD键都能正常工作，说明ok库的键盘系统有效
        这里直接使用ok库的标准方法
        """
        self._log(f"使用标准方法发送shift键，按下时间: {down_time}秒", notify=False)
        
        # 根据ok源码分析，只支持'SHIFT'（大写）作为shift键名称
        self.do_send_key_down('SHIFT')
        self.sleep(down_time)
        self.do_send_key_up('SHIFT')
        
        self._log("标准方法发送shift键完成", notify=False)



