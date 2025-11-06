import re
import random
import time
import win32gui
import win32api

from src.tasks.MyBaseTask import MyBaseTask
from src.tasks.ShiftKeyTestTask import ShiftKeyTestTask



class MyTestTask(ShiftKeyTestTask):
    """
    专门用于测试的任务类
    提供各种测试功能，包括OCR测试、按键测试、鼠标测试、延迟测试等
    """

    def __init__(self, executor=None, *args, **kwargs):
        # 调用父类构造函数，传递所有参数
        super().__init__(executor=executor, *args, **kwargs)
        self.name = "测试任务"
        self.description = "提供多种测试功能的综合测试任务"
        # 默认配置参数
        self.default_config.update(
            {
                "测试类型": "综合测试",
                "OCR测试文本": "测试",
                "OCR测试区域": "全屏",
                "按键测试键位": "w,a,s,d",
                "鼠标点击次数": 3,
                "延迟测试时间(秒)": 2,
                "循环测试次数": 2,
                "随机测试": True,
                "启用日志": True,
            }
        )
        # 配置类型定义
        self.config_type["测试类型"] = {
            "type": "drop_down",
            "options": ["综合测试", "OCR测试", "按键测试", "鼠标测试", "延迟测试"],
        }
        self.config_type["OCR测试区域"] = {
            "type": "drop_down",
            "options": ["全屏", "左上角", "右上角", "左下角", "右下角"],
        }

    def run(self, test_mode="auto"):
        """
        运行测试
        
        Args:
            test_mode: 测试模式，可选值:
                - "auto": 自动选择测试模式
                - "quick": 快速测试
                - "comprehensive": 全面测试
                - "shift_only": 仅测试shift键
                - "window_only": 仅测试窗口状态
        """
        # 首先检查配置中的测试类型
        test_type = self.config.get("测试类型", "综合测试")
        self._log(f"开始运行测试 (模式: {test_mode}, 类型: {test_type})", notify=True)
        
        # 根据配置的测试类型选择测试方法
        if test_type == "按键测试":
            success = self._run_keyboard_test()
        elif test_type == "鼠标测试":
            success = self._run_mouse_test()
        elif test_type == "OCR测试":
            success = self._run_ocr_test()
        elif test_type == "延迟测试":
            success = self._run_delay_test()
        elif test_type == "综合测试":
            # 综合测试时再根据test_mode选择
            if test_mode == "quick":
                success = self._run_quick_test()
            elif test_mode == "shift_only":
                # shift测试需要检查窗口前台状态
                success = self._run_shift_only_test()
            elif test_mode == "window_only":
                success = self._run_window_only_test()
            elif test_mode == "auto":
                # 自动模式：直接运行快速测试，不需要检查窗口状态
                # 只有shift相关测试会在内部检查窗口状态
                success = self._run_quick_test()
            else:  # comprehensive
                success = self._run_comprehensive_test()
        else:
            self._log(f"❌ 未知的测试类型: {test_type}，默认执行综合测试", notify=True)
            success = self._run_comprehensive_test()
        
        if success:
            self._log("✅ 测试完成", notify=True)
        else:
            self._log("❌ 测试失败", notify=True)
        
        return success
    
    def _run_quick_test(self):
        """快速测试"""
        self._log("执行快速测试", notify=True)
        
        # 快速shift测试（内部会检查窗口前台状态）
        if not self.quick_shift_test():
            self._log("❌ 快速shift测试失败", notify=True)
        
        # 基本OCR测试（可以后台执行）
        self._run_ocr_test()
        
        # 基本鼠标测试（可以后台执行）
        self._run_mouse_test()
        
        # 窗口状态检查不影响整体结果，只记录信息
        if not self.test_game_window_status():
            self._log("⚠ 游戏窗口不在前台，但不影响后台测试", notify=True)
        
        self._log("✅ 快速测试完成", notify=True)
        return True
    
    def _run_shift_only_test(self):
        """仅测试shift键"""
        self._log("执行shift键专项测试", notify=True)
        
        # 确保游戏窗口在前台
        if not self.ensure_game_active():
            self._log("❌ 无法确保游戏窗口在前台", notify=True)
            return False
        
        # 测试所有shift组合键
        if not self.test_all_shift_combinations():
            self._log("❌ shift组合键测试失败", notify=True)
            return False
        
        # 测试shift键保持
        if not self.test_shift_hold():
            self._log("❌ shift键保持测试失败", notify=True)
            return False
        
        self._log("✅ shift键专项测试完成", notify=True)
        return True
    
    def _run_window_only_test(self):
        """仅测试窗口状态"""
        self._log("执行窗口状态专项测试", notify=True)
        
        # 测试窗口状态
        if not self.test_game_window_status():
            self._log("❌ 窗口状态测试失败", notify=True)
            return False
        
        # 尝试激活窗口
        if not self.ensure_game_active():
            self._log("❌ 窗口激活失败", notify=True)
            return False
        
        # 再次检查窗口状态
        if not self.test_game_window_status():
            self._log("❌ 激活后窗口状态检查失败", notify=True)
            return False
        
        self._log("✅ 窗口状态专项测试完成", notify=True)
        return True
    
    def start_test(self, test_mode="auto", delay=3):
        """
        启动测试的便捷方法
        
        Args:
            test_mode: 测试模式
            delay: 启动前延迟（秒）
        """
        self._log(f"🚀 准备启动测试，{delay}秒后开始...", notify=True)
        self.sleep(delay)
        
        return self.run(test_mode)
    
    def interactive_test(self):
        """交互式测试模式"""
        self._log("🎮 进入交互式测试模式", notify=True)
        
        while True:
            self._log("\n=== 交互式测试菜单 ===", notify=True)
            self._log("1. 快速测试", notify=True)
            self._log("2. shift键专项测试", notify=True)
            self._log("3. 窗口状态测试", notify=True)
            self._log("4. 全面测试", notify=True)
            self._log("5. 退出", notify=True)
            
            choice = input("请选择测试模式 (1-5): ").strip()
            
            if choice == "1":
                self.start_test("quick")
            elif choice == "2":
                self.start_test("shift_only")
            elif choice == "3":
                self.start_test("window_only")
            elif choice == "4":
                self.start_test("comprehensive")
            elif choice == "5":
                self._log("👋 退出交互式测试模式", notify=True)
                break
            else:
                self._log("❌ 无效选择，请重新输入", notify=True)
            
            self.sleep(1)
    
    def _log(self, message, notify=False):
        """
        根据配置决定是否记录日志
        """
        if self.config.get("启用日志", True):
            self.log_info(message, notify=notify)

    def _run_comprehensive_test(self):
        """
        运行综合测试
        依次执行所有测试类型
        
        Returns:
            bool: 测试是否成功
        """
        self._log("执行综合测试...", notify=True)
        
        # 初始化成功标志
        success = True
        
        try:
            # 测试顺序可以根据需要调整
            self._run_delay_test()
            
            # 对于键盘测试，排除shift以允许在后台执行
            self._run_keyboard_test(exclude_shift=True)
            
            self._run_mouse_test()
            # OCR测试有返回值，用于判断成功与否
            ocr_success = self._run_ocr_test()
            if not ocr_success:
                success = False
            
            # 如果启用随机测试，添加一些随机操作
            if self.config.get("随机测试", True):
                self._run_random_operations()
                
        except Exception as e:
            self._log(f"❌ 综合测试过程中发生错误: {str(e)}", notify=True)
            success = False
            
        self._log(f"{'✅' if success else '❌'} 综合测试完成", notify=True)
        return success

    def _run_ocr_test(self):
        """
        运行OCR测试
        在指定区域查找指定文本
        """
        self._log("执行OCR测试...", notify=False)
        self._log("⚠ OCR测试将在后台执行", notify=True)
        
        # 获取OCR测试配置
        text = self.config.get("OCR测试文本", "测试")
        area = self.config.get("OCR测试区域", "全屏")
        
        # 转换区域为box参数
        box_map = {
            "全屏": None,
            "左上角": "top_left",
            "右上角": "top_right",
            "左下角": "bottom_left",
            "右下角": "bottom_right"
        }
        box = box_map.get(area, None)
        
        self._log(f"在{area}查找文本: '{text}'", notify=False)
        
        # 执行OCR识别
        start_time = time.time()
        result = self.ocr(box=box, match=text, log=True)
        end_time = time.time()
        
        if result:
            self._log(f"OCR测试成功! 找到文本，耗时: {(end_time - start_time):.2f}秒", notify=False)
            self._log(f"找到的位置: {result}", notify=False)
        else:
            self._log(f"OCR测试完成，但未找到指定文本，耗时: {(end_time - start_time):.2f}秒", notify=False)
        
        return bool(result)

    def _run_keyboard_test(self, exclude_shift=False):
        """
        运行按键测试
        测试指定的按键，使用便捷方法
        
        Args:
            exclude_shift: 是否排除shift键测试
            
        Returns:
            bool: 测试是否成功
        """
        self._log("执行按键测试...", notify=False)
        
        # 初始化成功标志
        success = True
        
        # 除了shift，其他按键测试可以在后台执行
        if not exclude_shift:
            if not self.ensure_game_active():
                self._log("❌ 无法确保游戏窗口在前台，包含shift的键盘测试失败", notify=False)
                return False
        
        # 获取按键配置
        keys_str = self.config.get("按键测试键位", "w,a,s,d")
        keys = [key.strip() for key in keys_str.split(",")]
        
        # 如果排除shift，则过滤掉shift键
        if exclude_shift:
            keys = [key for key in keys if key.lower() != 'shift']
            self._log(f"测试按键(排除shift): {', '.join(keys)}", notify=False)
        else:
            self._log(f"测试按键: {', '.join(keys)}", notify=False)
        
        # 测试每个按键
        for key in keys:
            self._log(f"测试按键: {key}", notify=False)
            
            try:
                # 如果是shift键，使用便捷方法
                if key.lower() == 'shift':
                    self._log("=== 开始测试shift键（使用便捷方法） ===", notify=False)
                    
                    # 测试1: 发送shift键
                    self._log("测试1: 发送shift键", notify=False)
                    if self.send_shift():
                        self._log("✓ shift键发送成功", notify=False)
                    else:
                        self._log("❌ shift键发送失败", notify=False)
                        success = False
                    self.sleep(1)
                    
                    # 测试2: 按下shift键保持
                    self._log("测试2: 按下shift键保持2秒", notify=False)
                    if self.send_shift_down():
                        self._log("✓ shift键按下成功", notify=False)
                        self.sleep(2)
                        if self.send_shift_up():
                            self._log("✓ shift键抬起成功", notify=False)
                        else:
                            self._log("❌ shift键抬起失败", notify=False)
                            success = False
                    else:
                        self._log("❌ shift键按下失败", notify=False)
                        success = False
                    self.sleep(1)
                    
                    # 测试3: 发送shift+W组合键
                    self._log("测试3: 发送shift+W组合键", notify=False)
                    if self.send_w_with_shift():
                        self._log("✓ shift+W组合键发送成功", notify=False)
                    else:
                        self._log("❌ shift+W组合键发送失败", notify=False)
                        success = False
                    self.sleep(1)
                    
                    # 测试4: 发送shift+A组合键
                    self._log("测试4: 发送shift+A组合键", notify=False)
                    if self.send_a_with_shift():
                        self._log("✓ shift+A组合键发送成功", notify=False)
                    else:
                        self._log("❌ shift+A组合键发送失败", notify=False)
                        success = False
                    self.sleep(1)
                    
                    # 测试5: 发送shift+S组合键
                    self._log("测试5: 发送shift+S组合键", notify=False)
                    if self.send_s_with_shift():
                        self._log("✓ shift+S组合键发送成功", notify=False)
                    else:
                        self._log("❌ shift+S组合键发送失败", notify=False)
                        success = False
                    self.sleep(1)
                    
                    # 测试6: 发送shift+D组合键
                    self._log("测试6: 发送shift+D组合键", notify=False)
                    if self.send_d_with_shift():
                        self._log("✓ shift+D组合键发送成功", notify=False)
                    else:
                        self._log("❌ shift+D组合键发送失败", notify=False)
                        success = False
                    self.sleep(1)
                    
                    self._log("=== shift键测试完成 ===", notify=False)
                else:
                    # 对于其他按键，使用便捷方法
                    self._log(f"测试按键: {key}", notify=False)
                    if self.send_key(key):
                        self._log(f"✓ {key}键发送成功", notify=False)
                    else:
                        self._log(f"❌ {key}键发送失败", notify=False)
                        success = False
                    self.sleep(1)
            except Exception as e:
                self._log(f"❌ 测试按键 {key} 时发生错误: {str(e)}", notify=False)
                success = False
        
        self._log(f"{'✅' if success else '❌'} 按键测试完成", notify=False)
        return success

    def _run_mouse_test(self):
        """
        运行鼠标测试
        测试鼠标点击功能
        """
        self._log("执行鼠标测试...", notify=False)
        self._log("⚠ 鼠标测试将在后台执行", notify=True)
        
        # 获取点击次数配置
        click_count = self.config.get("鼠标点击次数", 3)
        
        self._log(f"测试鼠标点击，共点击{click_count}次", notify=False)
        
        # 执行鼠标点击测试
        for i in range(click_count):
            
            # 使用win32api获取屏幕大小
            screen_width = win32api.GetSystemMetrics(0)
            screen_height = win32api.GetSystemMetrics(1)
            center_x, center_y = screen_width // 2, screen_height // 2
            
            # 轻微随机化点击位置
            offset_x = random.randint(-50, 50)
            offset_y = random.randint(-50, 50)
            click_x = center_x + offset_x
            click_y = center_y + offset_y
            
            self._log(f"第{i+1}次鼠标点击，位置: ({click_x}, {click_y})", notify=False)
            
            # 左键点击
            self.click(click_x, click_y)
            self.sleep(0.5)
            
            # 右键点击
            self.click(click_x, click_y, key='right')
            self.sleep(0.5)
        
        self._log("鼠标测试完成", notify=False)

    def _run_delay_test(self):
        """
        运行延迟测试
        测试延迟功能的准确性
        """
        self._log("执行延迟测试...", notify=False)
        
        # 获取延迟时间配置
        delay_time = self.config.get("延迟测试时间(秒)", 2)
        
        self._log(f"测试延迟: {delay_time}秒", notify=False)
        
        # 测量实际延迟时间
        start_time = time.time()
        self.sleep(delay_time)
        actual_delay = time.time() - start_time
        
        error_percent = abs(actual_delay - delay_time) / delay_time * 100
        self._log(f"预期延迟: {delay_time}秒，实际延迟: {actual_delay:.3f}秒，误差: {error_percent:.2f}%", notify=False)
        
        self._log("延迟测试完成", notify=False)

    def _run_random_operations(self):
        """
        执行随机操作测试
        随机执行各种操作，测试系统的稳定性
        """
        self._log("执行随机操作测试...", notify=False)
        
        # 定义可用的操作类型
        operations = [
            self._random_ocr,
            self._random_keyboard,
            self._random_mouse,
            self._random_delay
        ]
        
        # 随机执行5-10次操作
        operation_count = random.randint(5, 10)
        self._log(f"随机执行{operation_count}次操作", notify=False)
        
        for i in range(operation_count):
            # 随机选择一个操作
            operation = random.choice(operations)
            operation()
        
        self._log("随机操作测试完成", notify=False)

    def _random_ocr(self):
        """
        随机OCR测试
        """
        random_texts = ["确定", "取消", "开始", "结束", "保存", "退出"]
        text = random.choice(random_texts)
        areas = [None, "top_left", "top_right", "bottom_left", "bottom_right"]
        area = random.choice(areas)
        
        self._log(f"随机OCR测试: 在{area or '全屏'}查找文本 '{text}'", notify=False)
        self.ocr(box=area, match=text, log=False)

    def _random_keyboard(self):
        """
        随机键盘测试，使用便捷方法
        """
        all_keys = "abcdefghijklmnopqrstuvwxyz0123456789"
        special_keys = ["enter", "esc", "space", "shift", "ctrl", "alt"]
        
        # 90%概率测试普通键，10%概率测试特殊键
        if random.random() < 0.9:
            key = random.choice(all_keys)
            self._log(f"随机键盘测试: 按键 '{key}'", notify=False)
            if self.send_key(key):
                self._log(f"✓ {key}键发送成功", notify=False)
            else:
                self._log(f"❌ {key}键发送失败", notify=False)
        else:
            key = random.choice(special_keys)
            self._log(f"随机键盘测试: 特殊键 '{key}'", notify=False)
            
            # 如果是shift键，使用便捷方法
            if key == 'shift':
                if self.send_shift():
                    self._log("✓ shift键发送成功", notify=False)
                else:
                    self._log("❌ shift键发送失败", notify=False)
            else:
                # 其他特殊键使用原始方法
                down_time = random.uniform(0.1, 0.5)
                self.send_key(key, down_time=down_time)
                self._log(f"特殊键 '{key}' 发送完成", notify=False)

    def _random_mouse(self):
        """
        随机鼠标测试
        """
        # 使用win32api获取屏幕大小
        screen_width = win32api.GetSystemMetrics(0)
        screen_height = win32api.GetSystemMetrics(1)
        x = random.randint(100, screen_width - 100)
        y = random.randint(100, screen_height - 100)
        keys = ['left', 'right']
        key = random.choice(keys)
        
        self._log(f"随机鼠标测试: 在位置 ({x}, {y}) {key}键点击", notify=False)
        self.click(x, y, key=key)

    def _random_delay(self):
        """
        随机延迟测试
        """
        delay = random.uniform(0.5, 3.0)
        self._log(f"随机延迟测试: 延迟 {delay:.2f}秒", notify=False)
        self.sleep(delay)

    # 以下是一些额外的实用测试方法
    
    def test_find_feature(self, feature_name):
        """
        测试查找特定的特征点
        
        Args:
            feature_name: 特征点名称
            
        Returns:
            bool: 是否找到特征点
        """
        self._log(f"测试查找特征点: {feature_name}", notify=False)
        result = self.find_one(feature_name)
        if result:
            self._log(f"找到特征点 {feature_name}，位置: {result}", notify=False)
            return True
        else:
            self._log(f"未找到特征点 {feature_name}", notify=False)
            return False
    
    def test_ocr_with_regex(self, pattern, box=None):
        """
        测试使用正则表达式进行OCR识别
        
        Args:
            pattern: 正则表达式模式
            box: OCR区域
            
        Returns:
            list: 识别结果列表
        """
        self._log(f"测试正则表达式OCR: 模式 '{pattern}'", notify=False)
        result = self.ocr(box=box, match=re.compile(pattern), log=True)
        return result
    
    def test_screen_capture(self):
        """
        测试屏幕截图功能
        
        Returns:
            bool: 截图是否成功
        """
        self._log("测试屏幕截图功能", notify=False)
        try:
            screenshot = self.screenshot()
            if screenshot is not None:
                self._log(f"屏幕截图成功，大小: {screenshot.shape[:2]}", notify=False)
                return True
            else:
                self._log("屏幕截图失败", notify=False)
                return False
        except Exception as e:
            self._log(f"屏幕截图过程中出错: {str(e)}", notify=False)
            return False
    
    # ========== 新增便捷方法 ==========
    
    def quick_shift_test(self):
        """快速shift键测试"""
        self._log("执行快速shift键测试", notify=True)
        
        # 确保游戏窗口在前台（shift测试必须在前台）
        if not self.ensure_game_active():
            self._log("❌ 无法确保游戏窗口在前台，shift键测试失败", notify=True)
            return False
        
        # 测试shift键
        if self.send_shift():
            self._log("✓ shift键测试成功", notify=True)
        else:
            self._log("❌ shift键测试失败", notify=True)
            return False
        
        self.sleep(1)
        
        # 测试shift+W组合键
        if self.send_w_with_shift():
            self._log("✓ shift+W组合键测试成功", notify=True)
        else:
            self._log("❌ shift+W组合键测试失败", notify=True)
            return False
        
        self._log("✅ 快速shift键测试完成", notify=True)
        return True
    
    def test_all_shift_combinations(self):
        """测试所有shift组合键"""
        self._log("测试所有shift组合键", notify=True)
        
        if not self.ensure_game_active():
            self._log("❌ 无法确保游戏窗口在前台，测试跳过", notify=True)
            return False
        
        combinations = [
            ("W", self.send_w_with_shift),
            ("A", self.send_a_with_shift),
            ("S", self.send_s_with_shift),
            ("D", self.send_d_with_shift),
        ]
        
        success_count = 0
        for key_name, method in combinations:
            self._log(f"测试shift+{key_name}组合键", notify=False)
            if method():
                self._log(f"✓ shift+{key_name}组合键测试成功", notify=False)
                success_count += 1
            else:
                self._log(f"❌ shift+{key_name}组合键测试失败", notify=False)
            self.sleep(0.5)
        
        self._log(f"✅ shift组合键测试完成: {success_count}/{len(combinations)} 成功", notify=True)
        return success_count == len(combinations)
    
    def test_shift_hold(self, hold_time=3):
        """测试shift键保持功能
        
        Args:
            hold_time: 保持时间（秒）
        """
        self._log(f"测试shift键保持功能（{hold_time}秒）", notify=True)
        
        if not self.ensure_game_active():
            self._log("❌ 无法确保游戏窗口在前台，测试跳过", notify=True)
            return False
        
        # 按下shift键
        if self.send_shift_down():
            self._log("✓ shift键按下成功", notify=True)
        else:
            self._log("❌ shift键按下失败", notify=True)
            return False
        
        # 保持指定时间
        self._log(f"⏳ shift键保持{hold_time}秒...", notify=True)
        self.sleep(hold_time)
        
        # 抬起shift键
        if self.send_shift_up():
            self._log("✓ shift键抬起成功", notify=True)
        else:
            self._log("❌ shift键抬起失败", notify=True)
            return False
        
        self._log("✅ shift键保持测试完成", notify=True)
        return True
    
    def test_game_window_status(self):
        """测试游戏窗口状态"""
        self._log("测试游戏窗口状态", notify=True)
        
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
            self._log("❌ 未找到游戏窗口", notify=True)
            return False
        
        self.game_hwnd, title = windows[0]
        self._log(f"找到游戏窗口: {title} (句柄: {self.game_hwnd})", notify=True)
        
        # 检查窗口状态
        foreground_hwnd = win32gui.GetForegroundWindow()
        if foreground_hwnd == self.game_hwnd:
            self._log("✓ 游戏窗口在前台", notify=True)
            return True
        else:
            self._log("⚠ 游戏窗口不在前台", notify=True)
            self._log(f"当前前台窗口: {win32gui.GetWindowText(foreground_hwnd)}", notify=True)
            return False