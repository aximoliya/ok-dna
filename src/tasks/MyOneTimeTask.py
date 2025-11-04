import re
import random

from ok import BaseTask

from src.tasks.MyBaseTask import MyBaseTask


class MyOneTimeTask(MyBaseTask):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.name = "驱离挂机测试"
        self.description = "用户点击时调用run方法"
        self.default_config.update(
            {
                "下拉菜单选项": "mod开核桃驱离挂机测试(没写完选什么都没用)",
                "是否选项默认支持": False,
                "执行几次": 1,
                "文字框选项": "默认文字",
                "长文字框选项": "默认文字默认文字默认文字默认文字默认文字默认文字默认文字默认文字默认文字默认文字默认文字默认文字默认文字默认文字默认文字默认文字默认文字默认文字默认文字",
                "list选项": ["第一", "第二", "第3"],
            }
        )
        self.config_type["下拉菜单选项"] = {
            "type": "drop_down",
            "options": ["mod驱离挂机测试", "开核桃驱离挂机测试(未写)"],
        }

    def run(self):
        """运行驱离挂机测试任务，支持循环执行
        
        实现正确的循环流程：
        1. 点击"再次进行"按钮
        2. 然后点击"开始挑战"按钮
        3. 等待进图
        4. 重复执行指定次数
        """
        # 获取配置中的执行次数，默认为1
        execution_count = self.config.get("执行几次", 1)
        
        try:
            # 执行指定次数的驱离挂机测试
            for i in range(execution_count):
                self.log_info(f"开始第{i+1}/{execution_count}次驱离挂机测试", notify=True)
                
                # 第一次运行完整流程（包含确认选择）
                if i == 0:
                    if not self._run_initial_dismiss_bot_test():
                        self.log_info(f"第{i+1}次测试失败，提前结束循环", notify=True)
                        break
                # 后续循环
                else:
                    self.log_info(f"开始第{i+1}次循环", notify=False)
                    
                    # 循环衔接第3步：查找并点击"开始挑战"按钮
                    if not self._find_and_click_button("开始挑战", None, "开始挑战按钮"):
                        self.log_info(f"无法找到开始挑战按钮，提前结束循环", notify=True)
                        break
                    self.sleep(1)
                    
                    # 等待地图加载
                    if not self._wait_for_map_loading():
                        self.log_info(f"地图加载失败，提前结束循环", notify=True)
                        break
                    
                    # 执行螺旋飞跃和移动操作
                    self._execute_spiral_movement(3, 2, 2, 1)
                    
                    # 尝试查找并点击"再次进行"按钮（第6步）
                    retry_attempts = 0
                    max_retry = 3  # 最多尝试3次退出后再查找
                    while retry_attempts < max_retry:
                        if self._handle_retry_and_continue(1):
                            # 找到再次进行按钮，跳出重试循环
                            break
                        else:
                            # 未找到再次进行按钮，执行退出逻辑
                            self.log_info(f"无法继续循环，执行退出逻辑，尝试第{retry_attempts+1}/{max_retry}次", notify=True)
                            self._exit_instance_procedure(1)
                            retry_attempts += 1
                            # 执行完退出逻辑后，再次尝试查找"再次进行"按钮（衔接第6步）
                            continue
                    
                    # 如果达到最大重试次数仍未成功，结束循环
                    if retry_attempts >= max_retry:
                        self.log_info(f"达到最大重试次数，无法继续循环", notify=True)
                        break
        except Exception as e:
            self.log_info(f"运行过程中出错: {str(e)}")
            self.log_info(f"错误类型: {type(e).__name__}")
        finally:
            self.log_info(f"驱离挂机测试全部运行完成!", notify=False)
    
    def _run_initial_dismiss_bot_test(self):
        """执行初始驱离挂机测试的完整流程（包含确认选择）
        
        流程包括:
        1. 等待准备时间
        2. 查找并点击"确认选择"按钮
        3. 查找并点击"开始挑战"按钮
        4. 等待地图加载并确认"驱离"文字出现
        5. 执行螺旋飞跃和移动操作
        6. 查找并点击"再次进行"按钮
            此时有两种情况：
            a. 找到"再次进行"按钮，继续循环
                循环衔接的是第3步
            b. 未找到"再次进行"按钮，执行退出逻辑
                执行完退出逻辑后循环应该衔接第6步
        
        Returns:
            bool: 测试是否成功完成
        """
        # 常量定义
        PREPARE_TIME = 3
        ACTION_DELAY = 1
        BACKWARD_TIME = 2
        SPIRAL_FORWARD_COUNT = 3
        SPIRAL_BACKWARD_COUNT = 2
        
        # 1. 等待准备时间
        self.sleep(PREPARE_TIME)
        self.log_info("驱离挂机测试开始运行!", notify=False)
        
        # 2. 查找并点击"确认选择"按钮
        if not self._find_and_click_button("确认选择", "bottom_right", "确认选择按钮"):
            self.log_info("未找到确认选择按钮，尝试直接查找开始挑战按钮", notify=False)
        else:
            self.sleep(ACTION_DELAY)
            self.log_info("等待1秒后继续运行!", notify=False)
        
        # 3. 查找并点击"开始挑战"按钮
        if not self._find_and_click_button("开始挑战", None, "开始挑战按钮"):
            return False
        self.sleep(ACTION_DELAY)
        self.log_info("等待1秒后继续运行!", notify=False)
        
        # 4. 等待地图加载并确认"驱离"文字出现
        if not self._wait_for_map_loading():
            return False
        
        # 5. 执行螺旋飞跃和移动操作
        self._execute_spiral_movement(SPIRAL_FORWARD_COUNT, BACKWARD_TIME, SPIRAL_BACKWARD_COUNT, ACTION_DELAY)
        
        # 6. 查找并点击"再次进行"按钮
        retry_attempts = 0
        max_retry = 3  # 最多尝试3次退出后再查找
        while retry_attempts < max_retry:
            if self._handle_retry_and_continue(ACTION_DELAY):
                # 找到再次进行按钮，返回成功
                return True
            else:
                # 未找到再次进行按钮，执行退出逻辑
                self.log_info(f"未找到再次进行按钮，执行退出逻辑，尝试第{retry_attempts+1}/{max_retry}次", notify=True)
                self._exit_instance_procedure(ACTION_DELAY)
                retry_attempts += 1
                # 执行完退出逻辑后，再次尝试查找"再次进行"按钮（衔接第6步）
                continue
        
        # 如果达到最大重试次数仍未成功，返回失败
        return False
    
    def _find_and_click_button(self, text, box=None, button_name="按钮"):
        """通用的查找并点击按钮方法
        
        Args:
            text: 要查找的文本
            box: OCR搜索区域，默认为None(全屏幕)
            button_name: 按钮的描述名称，用于日志
            
        Returns:
            bool: 是否成功点击按钮
        """
        self.log_info(f"开始查找{button_name}...", notify=False)
        pos = self.ocr(box=box, match=text, log=True)
        if not pos:
            self.log_info(f"未找到{button_name}")
            return False
        
        self.click_box(pos[0])
        self.log_info(f"点击{button_name}成功!", notify=False)
        return True
    
    def _wait_for_map_loading(self):
        """等待地图加载并确认"驱离"文字出现
        
        Returns:
            bool: 地图是否加载成功
        """
        self.log_info("开始等待地图加载...", notify=False)
        if not self.wait_ocr(box="top_right", match="驱离", log=True):
            self.log_info("未检测到驱离文字，地图可能未加载成功")
            return False
        
        self.log_info("检测到右上角\"驱离\"文字，地图加载成功!", notify=False)
        self.sleep(3)  # 额外的准备时间
        return True
    
    def _execute_spiral_movement(self, forward_count, backward_time, backward_count, delay):
        """执行螺旋飞跃和移动操作
        
        Args:
            forward_count: 向前螺旋飞跃次数
            backward_time: 后退持续时间(秒)
            backward_count: 后退后向前螺旋飞跃次数
            delay: 每次操作之间的延迟时间(秒)
        """
        # 向前螺旋飞跃
        self._send_key_multiple_times('4', forward_count, "向前", delay)

        self.sleep(1)

        self._execute_random_wasd_movement()
    
    def _execute_random_wasd_movement(self, duration=10, min_move_time=0.5, max_move_time=1.5, move_interval=0.2):
        """执行随机WASD移动操作
        
        Args:
            duration: 总移动持续时间(秒)
            min_move_time: 每次移动的最短时间(秒)
            max_move_time: 每次移动的最长时间(秒)
            move_interval: 两次移动之间的间隔时间(秒)
        """
        import time
        self.log_info(f"开始随机WASD移动，持续时间: {duration}秒", notify=False)
        
        # 定义方向键列表
        direction_keys = ['w', 'a', 's', 'd']
        direction_names = {'w': '前进', 'a': '向左', 's': '后退', 'd': '向右'}
        
        start_time = time.time()
        move_count = 0
        
        try:
            while time.time() - start_time < duration:
                # 随机选择一个方向键
                key = random.choice(direction_keys)
                # 随机生成按下时间
                down_time = random.uniform(min_move_time, max_move_time)
                
                # 发送按键
                direction = direction_names.get(key, key)
                self.log_info(f"随机移动: {direction}，持续时间: {down_time:.2f}秒", notify=False)
                self.send_key(key, down_time=down_time)
                
                move_count += 1
                
                # 等待间隔时间
                remaining_time = duration - (time.time() - start_time)
                if remaining_time > move_interval:
                    self.sleep(move_interval)
                else:
                    break
        except Exception as e:
            self.log_info(f"随机WASD移动过程中出错: {str(e)}", notify=False)
        finally:
            self.log_info(f"随机WASD移动完成，共执行{move_count}次移动", notify=False)
        
    
    def _send_key_multiple_times(self, key, count, direction, delay):
        """多次发送指定按键
        
        Args:
            key: 要发送的按键
            count: 发送次数
            direction: 方向描述，用于日志
            delay: 每次发送之间的延迟时间(秒)
        """
        self.log_info(f"开始{direction}{count}次螺旋飞跃", notify=False)
        for i in range(count):
            self.send_key(key)
            self.log_info(f"{direction}第{i+1}次发送按键{key}", notify=False)
            self.sleep(delay)
    
    def _handle_retry_and_continue(self, delay):
        """处理再次尝试并继续挑战的逻辑
        1. 点击"再次进行"按钮
        成功后循环会在run方法中衔接第3步
        
        Args:
            delay: 操作延迟时间(秒)
            
        Returns:
            bool: 是否成功点击"再次进行"按钮
        """
        self.log_info("开始查找再次进行按钮...", notify=False)
        try:
            # 只实现点击"再次进行"按钮的逻辑
            # 成功后，run方法会继续处理衔接第3步
            if self.wait_click_ocr(box="bottom_right", match="再次进行", log=True, 
                                 time_out=120, recheck_time=2, raise_if_not_found=True):
                self.log_info("点击再次进行成功!", notify=False)
                self.sleep(delay)  # 等待界面切换
                return True
        except Exception as e:
            self.log_info(f"未找到再次进行按钮或点击失败: {str(e)}", notify=False)
            return False
        return False
    
    def _exit_instance_procedure(self, delay):
        """执行退出副本的完整流程
        
        Args:
            delay: 操作延迟时间(秒)
        """
        self.log_info("未找到再次进行按钮，执行退出逻辑", notify=False)
        self.sleep(2)
        
        # 发送ESC键
        self.send_key('esc')
        self.log_info("已发送 ESC 键，尝试退出副本", notify=False)
        self.sleep(2)
        
        # 点击放弃挑战
        if self.wait_click_ocr(match="放弃挑战", log=True, 
                                 time_out=30,raise_if_not_found=True):
            self.sleep(delay)
            # 点击确认按钮
            self.wait_click_ocr(match="确定", log=True, 
                                 time_out=30,raise_if_not_found=True)



    def find_some_text_on_bottom_right(self):
        return self.ocr(box="bottom_right",match="商城", log=True) #指定box以提高ocr速度

    def find_some_text_with_relative_box(self):
        return self.ocr(0.5, 0.5, 1, 1, match=re.compile("招"), log=True) #指定box以提高ocr速度

    def test_find_one_feature(self):
        return self.find_one('box_battle_1')

    def test_find_feature_list(self):
        return self.find_feature('box_battle_1')

    def run_for_5(self):
        self.operate(lambda: self.do_run_for_5())

    def do_run_for_5(self):
        self.do_send_key_down('w')
        self.sleep(0.1)
        self.do_mouse_down(key='right')
        self.sleep(0.1)
        self.do_mouse_up(key='right')
        self.sleep(5)
        self.do_send_key_up('w')




