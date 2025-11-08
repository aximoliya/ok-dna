from src.tasks.MyBaseTask import MyBaseTask


class OpenWalnutTask(MyBaseTask):
    """开核桃任务 - 自动处理密函报酬选择和密函选择流程"""
    
    # 常量定义
    DEFAULT_ACTION_DELAY = 1.0  # 默认操作延迟（秒）
    DEFAULT_CHECK_INTERVAL = 1.0  # 默认检测间隔（秒）
    DEFAULT_WAIT_TIMEOUT = 30  # 默认等待超时时间（秒）
    
    # 角色特征映射
    ROLE_FEATURE_MAP = {
        "莉兹贝尔": "lizibeier",
    }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.name = "开核桃"
        self.description = "自动处理密函报酬选择界面，支持自动继续挑战或撤离"
        
        # 初始化默认配置
        self.default_config.update({
            "角色密函选择": "莉兹贝尔",
            "轮次": 0,  # 0表示无限循环，>0表示执行指定次数后退出
            "检测间隔(秒)": self.DEFAULT_CHECK_INTERVAL,
            "操作延迟(秒)": self.DEFAULT_ACTION_DELAY,
        })
        
        # 配置描述
        self.config_description.update({
            "角色密函选择": "选择要使用的角色密函",
            "轮次": "执行轮次的次数，0表示无限轮次直到手动停止",
            "检测间隔(秒)": "每次检测界面之间的间隔时间",
            "操作延迟(秒)": "每次点击操作后的等待时间",
        })
        
        # 配置UI类型
        self.config_type["角色密函选择"] = {
            "type": "drop_down",
            "options": ["莉兹贝尔"],
        }
        
        # 初始化循环计数器
        self.loop_count = 0

    def run(self):
        """主运行方法 - 循环检测并处理密函报酬选择界面"""
        self.log_info("开核桃任务开始运行!", notify=True)
        
        # 获取配置
        role_walnut_selection = self.config.get("角色密函选择", "莉兹贝尔")
        max_rounds = self.config.get("轮次", 0)
        check_interval = self.config.get("检测间隔(秒)", self.DEFAULT_CHECK_INTERVAL)
        action_delay = self.config.get("操作延迟(秒)", self.DEFAULT_ACTION_DELAY)
        
        # 验证角色选择
        if role_walnut_selection not in self.ROLE_FEATURE_MAP:
            self.log_info(f"❌ 不支持的角色: {role_walnut_selection}", notify=True)
            return
        
        self.log_info(
            f"配置: 角色密函={role_walnut_selection}, "
            f"轮次={'无限' if max_rounds == 0 else max_rounds}, "
            f"检测间隔={check_interval}秒, 操作延迟={action_delay}秒",
            notify=False
        )
        
        try:
            # 主循环
            while True:
                # 检查是否达到最大轮次
                if max_rounds > 0 and self.loop_count >= max_rounds:
                    self.log_info(f"已达到最大轮次 {max_rounds}，退出循环", notify=True)
                    break
                
                # 检测"密函报酬选择"界面
                if self._check_and_handle_reward_selection(action_delay):
                    self.loop_count += 1
                    self.log_info(f"成功处理第 {self.loop_count} 次密函报酬选择", notify=False)
                    
                    # 处理后续流程（始终自动继续挑战，除非达到最大轮次）
                    auto_continue = max_rounds == 0 or self.loop_count < max_rounds
                    result = self._handle_challenge_choice(
                        auto_continue, action_delay, role_walnut_selection
                    )
                    
                    if result is False:
                        # 处理失败，退出循环
                        self.log_info("处理挑战选择失败，退出循环", notify=True)
                        break
                    elif result is None:
                        # 选择撤离，退出任务
                        self.log_info("已选择撤离，退出任务", notify=True)
                        break
                    # result is True 表示成功处理，继续循环
                else:
                    # 未找到"密函报酬选择"界面，等待后继续检测
                    self.sleep(check_interval)
                    
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
        
        import time
        start_time = time.time()
        while time.time() - start_time < 130:
            # 循环体可以在需要时填充内容
            reward_text = self.ocr(match="密函报酬选择", log=False)
            if reward_text:
                break 
            self.sleep(5)
        
        
        if not reward_text:
            return False
        
        self.log_info("找到密函报酬选择界面!", notify=False)
        
        try:
            # 等待并点击"确认选择"按钮
            if not self.wait_click_ocr(
                match="确认选择",
                log=True,
                time_out=self.DEFAULT_WAIT_TIMEOUT
            ):
                self.log_info("未找到确认选择按钮", notify=False)
                return False
            
            self.sleep(delay)
            return True
            
        except Exception as e:
            self.log_info(f"点击确认选择按钮时出错: {str(e)}", notify=False)
            return False

    def _handle_challenge_choice(self, auto_continue, delay, role_walnut_selection):
        """处理挑战选择界面（撤离/继续挑战）
        
        Args:
            auto_continue: 是否自动继续挑战
            delay: 操作延迟时间(秒)
            role_walnut_selection: 角色密函选择
            
        Returns:
            bool: 成功处理并继续循环
            None: 选择撤离，需要退出任务
            False: 处理失败
        """
        self.log_info("等待挑战选择界面...", notify=False)
        self.sleep(delay)
        
        try:
            # 检测"撤离"和"继续挑战"按钮
            exit_button = self.wait_ocr(
                match="撤离",
                log=True,
                time_out=self.DEFAULT_WAIT_TIMEOUT
            )
            continue_button = self.wait_ocr(
                match=["继续挑战", "○继续挑战"],
                log=True,
                time_out=self.DEFAULT_WAIT_TIMEOUT
            )
            
            if not exit_button and not continue_button:
                self.log_info("未找到撤离或继续挑战按钮，可能界面还未加载", notify=False)
                return False
            
            if auto_continue:
                # 点击"继续挑战"
                if continue_button:
                    self.log_info("点击继续挑战按钮", notify=False)
                    self.click_box(continue_button[0])
                    self.sleep(delay)
                    
                    # 进入"选择密函"界面，选择密函并确认
                    return self._handle_walnut_selection(role_walnut_selection, delay)
                else:
                    self.log_info("未找到继续挑战按钮", notify=False)
                    return False
            else:
                # 点击"撤离"，退出任务
                if exit_button:
                    self.log_info("点击撤离按钮，退出关卡", notify=True)
                    self.click_box(exit_button[0])
                    self.sleep(delay)
                    return None  # 返回None表示选择撤离，需要退出任务
                else:
                    self.log_info("未找到撤离按钮", notify=False)
                    return False
                    
        except Exception as e:
            self.log_info(f"处理挑战选择界面时出错: {str(e)}", notify=False)
            return False

    def _handle_walnut_selection(self, role_walnut_selection, delay):
        """处理密函选择界面
        
        Args:
            role_walnut_selection: 角色密函选择
            delay: 操作延迟时间(秒)
            
        Returns:
            bool: 是否成功处理
        """
        self.log_info("等待选择密函界面...", notify=False)
        self.sleep(delay)
        
        try:
            # 检测"选择密函"界面（可选，用于确认界面已加载）
            selection_text = self.wait_ocr(
                match="选择密函",
                log=True,
                time_out=self.DEFAULT_WAIT_TIMEOUT
            )
            if not selection_text:
                self.log_info("未找到选择密函界面文字，尝试直接点击密函特征", notify=False)
            
            # 根据角色选择对应的密函特征
            feature_name = self.ROLE_FEATURE_MAP.get(role_walnut_selection)
            if not feature_name:
                self.log_info(f"❌ 不支持的角色: {role_walnut_selection}", notify=True)
                return False
            
            self.log_info(f"点击角色密函特征: {feature_name}", notify=False)
            if not self.wait_click_feature(
                feature_name,
                horizontal_variance=9999,
                vertical_variance=9999,
                time_out=self.DEFAULT_WAIT_TIMEOUT,
            ):
                self.log_info(f"未找到角色密函特征: {feature_name}", notify=False)
                return False
            
            self.sleep(delay)
            
            # 查找并点击"确认选择"按钮
            if not self.wait_click_ocr(
                match="确认选择",
                log=True,
                time_out=self.DEFAULT_WAIT_TIMEOUT
            ):
                self.log_info("未找到确认选择按钮", notify=False)
                return False
            
            self.sleep(delay)
            return True
            
        except Exception as e:
            self.log_info(f"处理密函选择界面时出错: {str(e)}", notify=False)
            return False
