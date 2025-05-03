class Task:
    def __init__(self, task_code, *args):
        self.args = args
        self._task_code = task_code
    
    def run(self):
        self._task_code(*self.args)
        self._task_code = None
        self.args = None

    
