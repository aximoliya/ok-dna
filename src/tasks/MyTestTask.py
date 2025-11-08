from src.tasks.ShiftKeyTestTask import ShiftKeyTestTask


class MyTestTask(ShiftKeyTestTask):
    """测试任务类 - 提供图片特征测试功能"""
    
    # 常量定义
    DEFAULT_FEATURE = "lizibeier"  # 默认图片特征名称
    DEFAULT_THRESHOLD = 0.8  # 默认匹配阈值
    PREPARE_DELAY = 1.0  # 测试前准备延迟（秒）
    
    def __init__(self, executor=None, *args, **kwargs):
        """初始化测试任务
        
        Args:
            executor: 任务执行器
            *args: 可变位置参数
            **kwargs: 可变关键字参数
        """
        super().__init__(executor=executor, *args, **kwargs)
        
        # 设置任务基本信息
        self.name = "测试任务"
        self.description = "提供图片特征测试功能"
        
        # 初始化默认配置
        self.default_config.update({
            "图片测试目标": self.DEFAULT_FEATURE,
            "图片测试阈值": self.DEFAULT_THRESHOLD,
        })

    def run(self):
        """运行测试任务
        
        Returns:
            bool: 测试是否成功
        """
        return self._run_image_test()
    
    def _run_image_test(self):
        """执行图片特征测试
        
        在全屏幕范围内查找指定的图片特征
        
        Returns:
            bool: 如果找到特征返回True，否则返回False
        """
        feature = self.config.get("图片测试目标", self.DEFAULT_FEATURE)
        threshold = self.config.get("图片测试阈值", self.DEFAULT_THRESHOLD)
        
        self.log_info("执行图片测试", notify=True)
        self.log_info(f"图片测试目标: {feature}, 阈值: {threshold}", notify=False)
        
        # 准备延迟
        self.sleep(self.PREPARE_DELAY)
        
        # 在全屏幕范围内查找特征
        # horizontal_variance=9999, vertical_variance=9999 表示不限制偏移范围
        result = self.find_feature(
            feature_name=feature,
            threshold=threshold,
            horizontal_variance=9999,
            vertical_variance=9999
        )
        
        if result:
            self.log_info(f"✅ 图片测试成功，找到特征: {feature}", notify=True)
            return True
        else:
            self.log_info(f"❌ 图片测试失败，未找到特征: {feature}", notify=True)
            return False