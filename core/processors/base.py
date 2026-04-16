class BaseProcessor:
    def __init__(self, engine):
        self.engine = engine  # 注入你现有的 engine

    def process(self, image_path, **kwargs):
        raise NotImplementedError("每个专家模块必须实现 process 方法")