from src.tasks.MyBaseTask import MyBaseTask
import time


class OpenWalnutTask(MyBaseTask):
    """开核桃任务 - 自动处理密函报酬选择和密函选择流程"""
    
    # 常量定义
    DEFAULT_ACTION_DELAY = 1.0  # 默认操作延迟（秒）
    DEFAULT_CHECK_INTERVAL = 1.0  # 默认检测间隔（秒）
    DEFAULT_WAIT_TIMEOUT = 30  # 默认等待超时时间（秒）
    MAX_REWARD_TIMEOUT = 130  # 最大密函报酬选择等待时间（秒）
    
    # 角色特征映射
    ROLE_FEATURE_MAP = {
        "莉兹贝尔": "lizibeier",
    }
    
    # 手册特征映射
    MANUAL_FEATURE_MAP = {
        "无": "bsysc",
        "一": "sc1",
        "二": "sc2",
        "三": "sc3",
        "四": "sc4",
    }
    
    def __init__(self, *args, **kwargs):
        """初始化开核桃任务
        
        Args:
            *args: 可变位置参数
            **kwargs: 可变关键字参数
        """
        super().__init__(*args, **kwargs)
        
        # 设置任务基本信息
        self.name = "自动下一轮"
        self.description = "在有轮次的关卡中自动选择奖励并且进入下一轮，可选择是否开核桃"
        
        # 初始化默认配置
        self.default_config.update({
            "角色密函选择": "莉兹贝尔",
            "轮次": 0,  # 0表示无限循环，>0表示执行指定次数后退出
            "检测间隔(秒)": self.DEFAULT_CHECK_INTERVAL,
            "操作延迟(秒)": self.DEFAULT_ACTION_DELAY,
            "是否开核桃": False,
            "是否使用手册": "无",
        })
        
        # 配置描述
        self.config_description.update({
            "角色密函选择": "选择要使用的角色密函",
            "轮次": "执行轮次的次数，0表示无限轮次直到手动停止",
            "检测间隔(秒)": "每次检测界面之间的间隔时间",
            "操作延迟(秒)": "每次点击操作后的等待时间",
            "是否开核桃": "是否在每轮结束后开核桃",
            "是否使用手册": "选择要使用的委托手册等级",
        })
        
        # 配置UI类型
        self.config_type.update({
            "角色密函选择": {
                "type": "drop_down",
                "options": list(self.ROLE_FEATURE_MAP.keys()),
            },
            "是否使用手册": {
                "type": "drop_down",
                "options": list(self.MANUAL_FEATURE_MAP.keys()),
            }
        })
        
        # 初始化循环计数器
        self.loop_count = 0

    def run(self):
        """主运行方法 - 循环检测并处理密函报酬选择界面
        
        Returns:
            None
        """
        self.log_info("开核桃任务开始运行!", notify=True)
        
        # 获取配置
        config = getattr(self, 'config', {}) or {}
        role_walnut_selection = config.get("角色密函选择", "莉兹贝尔")
        max_rounds = config.get("轮次", 0)
        check_interval = config.get("检测间隔(秒)", self.DEFAULT_CHECK_INTERVAL)
        action_delay = config.get("操作延迟(秒)", self.DEFAULT_ACTION_DELAY)
        open_walnut = config.get("是否开核桃", False)
        
        # 验证角色选择
        if role_walnut_selection not in self.ROLE_FEATURE_MAP:
            self.log_info(f"❌ 不支持的角色: {role_walnut_selection}", notify=True)
            return
        
        # 输出配置信息
        self.log_info(
            f"配置: 角色密函={role_walnut_selection}, "
            f"轮次={'无限' if max_rounds == 0 else max_rounds}, "
            f"检测间隔={check_interval}秒, 操作延迟={action_delay}秒, "
            f"是否开核桃={open_walnut}",
            notify=False
        )
        
        self.log_info(f"{'开核桃模式' if open_walnut else '普通循环模式'}已启动", notify=False)
        
        try:
            # 主循环
            while True:
                # 检查是否达到最大轮次
                if max_rounds > 0 and self.loop_count >= max_rounds:
                    self.log_info(f"已达到最大轮次 {max_rounds}，退出循环", notify=True)
                    break
                
                # 开核桃流程
                if open_walnut:
                    # 检测"密函报酬选择"界面
                    if self._check_and_handle_reward_selection(action_delay):
                        self.loop_count += 1
                        self.log_info(f"成功处理第 {self.loop_count} 次密函报酬选择", notify=False)
                        
                        # 处理后续流程
                        auto_continue = max_rounds == 0 or self.loop_count < max_rounds
                        result = self._handle_challenge_choice(
                            auto_continue, action_delay, role_walnut_selection, open_walnut
                        )
                        
                        # 处理结果逻辑
                        if result is False:
                            self.log_info("处理挑战选择失败，退出循环", notify=True)
                            break
                        elif result is None:
                            self.log_info("已选择撤离，退出任务", notify=True)
                            break
                        # result is True 表示成功处理，继续循环
                    else:
                        # 未找到界面，等待后继续检测
                        self.sleep(check_interval)
                else:
                    # 不开核桃流程
                    self.loop_count += 1
                    auto_continue = max_rounds == 0 or self.loop_count < max_rounds
                    if auto_continue:
                        self._handle_challenge_choice(
                            True, action_delay, role_walnut_selection, open_walnut
                        )

        except KeyboardInterrupt:
            self.log_info("用户中断任务", notify=True)
        except Exception as e:
            self.log_info(f"运行过程中出错: {str(e)}", notify=True)
            self.log_info(f"错误类型: {type(e).__name__}", notify=False)
        finally:
            self.log_info(f"开核桃任务运行完成! 共处理 {self.loop_count} 轮", notify=True)

    def _check_and_handle_reward_selection(self, delay):
        """检测并处理"密函报酬选择"界面
        
        Args:
            delay: 操作延迟时间(秒)
            
        Returns:
            bool: 是否成功处理
        """
        self.log_info("开始检测密函报酬选择界面...", notify=False)
        
        # 等待并检测密函报酬选择界面
        start_time = time.time()
        reward_text = None
        check_count = 0
        
        while time.time() - start_time < self.MAX_REWARD_TIMEOUT:
            check_count += 1
            reward_text = self.ocr(match="密函报酬选择", log=False)
            if reward_text:
                break
            
            # 每10次检查输出一次日志
            if check_count % 10 == 0:
                elapsed_time = int(time.time() - start_time)
                self.log_info(f"已等待{elapsed_time}秒，继续检测密函报酬选择界面...", notify=False)
                
            self.sleep(5)  # 间隔检测
        
        if not reward_text:
            self.log_info(f"超时：未在{self.MAX_REWARD_TIMEOUT}秒内找到密函报酬选择界面", notify=False)
            return False
        
        self.log_info("找到密函报酬选择界面!", notify=False)
        
        try:
            # 等待并点击"确认选择"按钮
            click_result = self.wait_click_ocr(
                match="确认选择",
                log=True,
                time_out=self.DEFAULT_WAIT_TIMEOUT
            )
            
            if not click_result:
                self.log_info("未找到确认选择按钮", notify=False)
                return False
            
            self.sleep(delay)
            return True
            
        except Exception as e:
            self.log_info(f"点击确认选择按钮时出错: {str(e)}", notify=False)
            return False

    def _handle_challenge_choice(self, auto_continue, delay, role_walnut_selection, open_walnut):
        """处理挑战选择界面（撤离/继续挑战）
        
        Args:
            auto_continue: 是否自动继续挑战
            delay: 操作延迟时间(秒)
            role_walnut_selection: 角色密函选择
            open_walnut: 是否开核桃
            
        Returns:
            bool: 成功处理并继续循环
            None: 选择撤离，需要退出任务
            False: 处理失败
        """
        self.log_info("等待挑战选择界面...", notify=False)
        self.sleep(delay)
        
        try:
            # 检测"撤离"和"继续挑战"按钮
            exit_button = None
            continue_button = None
            
            # 等待界面加载完成
            start_time = time.time()
            while (exit_button is None or continue_button is None) and time.time() - start_time < self.MAX_REWARD_TIMEOUT:
                exit_button = self.ocr(match="撤离", log=True)
                continue_button = self.ocr(match=["继续挑战", "○继续挑战"], log=True)
                
                if not exit_button and not continue_button:
                    sleep_time = 1 if open_walnut else 5
                    self.sleep(sleep_time)
            
            # 验证按钮是否存在
            if not exit_button and not continue_button:
                self.log_info("未找到撤离或继续挑战按钮，可能界面还未加载", notify=False)
                return False
            
            # 记录找到的按钮
            found_buttons = []
            if exit_button:
                found_buttons.append("撤离")
            if continue_button:
                found_buttons.append("继续挑战")
            
            if found_buttons:
                self.log_info(f"找到按钮: {', '.join(found_buttons)}", notify=False)
            
            # 处理自动继续挑战
            if auto_continue:
                return self._handle_continue_challenge(continue_button, delay, role_walnut_selection, open_walnut)
            else:
                # 处理撤离
                return self._handle_exit_challenge(exit_button, delay)
                    
        except Exception as e:
            self.log_info(f"处理挑战选择界面时出错: {str(e)}", notify=False)
            return False
    
    def _handle_continue_challenge(self, continue_button, delay, role_walnut_selection, open_walnut):
        """处理继续挑战逻辑
        
        Args:
            continue_button: 继续挑战按钮
            delay: 操作延迟时间(秒)
            role_walnut_selection: 角色密函选择
            open_walnut: 是否开核桃
            
        Returns:
            bool: 是否成功处理
        """
        if not continue_button:
            self.log_info("未找到继续挑战按钮", notify=False)
            return False
        
        try:
            # 点击继续挑战
            self.log_info("点击继续挑战按钮", notify=False)
            self.click_box(continue_button[0])
            self.sleep(delay)
            
            # 根据是否开核桃执行不同流程
            if open_walnut:
                # 开核桃流程
                self.log_info("进入密函选择流程", notify=False)
                return self._handle_walnut_selection(role_walnut_selection, delay)
            else:
                # 不开核桃，处理手册选择
                self.log_info("进入手册选择流程", notify=False)
                return self._handle_manual_selection(delay)
        
        except Exception as e:
            self.log_info(f"处理继续挑战时出错: {str(e)}", notify=False)
            return False
    
    def _handle_exit_challenge(self, exit_button, delay):
        """处理撤离逻辑
        
        Args:
            exit_button: 撤离按钮
            delay: 操作延迟时间(秒)
            
        Returns:
            None: 成功撤离
            False: 撤离失败
        """
        if not exit_button:
            self.log_info("未找到撤离按钮", notify=False)
            return False
        
        try:
            # 点击撤离
            self.log_info("点击撤离按钮，退出关卡", notify=True)
            self.click_box(exit_button[0])
            self.sleep(delay)
            return None  # 返回None表示选择撤离
        except Exception as e:
            self.log_info(f"处理撤离时出错: {str(e)}", notify=False)
            return False
    
    def _handle_manual_selection(self, delay):
        """处理手册选择界面
        
        Args:
            delay: 操作延迟时间(秒)
            
        Returns:
            bool: 是否成功处理
        """
        # 获取配置
        config = getattr(self, 'config', {}) or {}
        use_manual = config.get("是否使用手册", "无")
        feature_name = self.MANUAL_FEATURE_MAP.get(use_manual)
        
        if not feature_name:
            self.log_info("未知配置是否使用手册，默认不使用", notify=False)
            return False
        
        self.log_info(f"使用委托手册{use_manual}", notify=False)
        
        try:
            # 查找并点击对应手册特征
            manual_feature = self.find_feature(feature_name, horizontal_variance=9999, vertical_variance=9999)
            if manual_feature:
                self.click_box(manual_feature[0], relative_x=0.1, relative_y=0.1)
                self.sleep(delay)
            
            # 等待并点击开始挑战
            click_result = self.wait_click_ocr(
                match=["开始挑战"],
                log=True,
                time_out=self.DEFAULT_WAIT_TIMEOUT
            )
            
            return click_result is not None
            
        except Exception as e:
            self.log_info(f"处理手册选择时出错: {str(e)}", notify=False)
            return False

    def _handle_walnut_selection(self, role_walnut_selection, delay):
        """处理密函选择界面
        
        Args:
            role_walnut_selection: 角色密函选择
            delay: 操作延迟时间(秒)
            
        Returns:
            bool: 是否成功处理
        """
        self.log_info(f"开始处理角色密函选择: {role_walnut_selection}", notify=False)
        self.sleep(delay)
        
        try:
            # 获取角色对应的密函特征
            feature_name = self.ROLE_FEATURE_MAP.get(role_walnut_selection)
            if not feature_name:
                self.log_info(f"❌ 不支持的角色: {role_walnut_selection}", notify=True)
                return False
            
            # 检测"选择密函"界面（可选，用于确认界面已加载）
            selection_text = self.wait_ocr(
                match="选择密函",
                log=True,
                time_out=self.DEFAULT_WAIT_TIMEOUT
            )
            if not selection_text:
                self.log_info("未找到选择密函界面文字，尝试直接点击密函特征", notify=False)
            else:
                self.log_info("确认找到选择密函界面", notify=False)
            
            # 点击角色密函特征
            self.log_info(f"点击角色密函特征: {feature_name}", notify=False)
            feature_click_result = self.wait_click_feature(
                feature_name,
                horizontal_variance=9999,
                vertical_variance=9999,
                time_out=self.DEFAULT_WAIT_TIMEOUT,
            )
            
            if not feature_click_result:
                self.log_info(f"未找到角色密函特征: {feature_name}", notify=False)
                return False
            
            self.log_info("角色密函选择成功", notify=False)
            self.sleep(delay)
            
            # 点击确认选择按钮
            self.log_info("等待确认选择按钮", notify=False)
            confirm_click_result = self.wait_click_ocr(
                match="确认选择",
                log=True,
                time_out=self.DEFAULT_WAIT_TIMEOUT
            )
            
            if not confirm_click_result:
                self.log_info("未找到确认选择按钮", notify=False)
                return False
            
            self.log_info("确认选择成功，准备进入下一轮", notify=False)
            self.sleep(delay)
            return True
            
        except Exception as e:
            self.log_info(f"处理密函选择界面时出错: {str(e)}", notify=False)
            return False
