import threading

class TaskRunner:
    def __init__(self, tab):
        self.tab = tab
        self.tasks = []
        self.condition = threading.Condition()

    def scheduele_task(self, task):
        self.condition.acquire(blocking=True)
        self.tasks.append(task)
        self.condition.notify_all()
        self.condition.release()

    def run(self):
        task = None
        self.condition.acquire(blocking=True)
        if len(self.tasks) > 0:
            task = self.tasks.pop(0)
        self.condition.release()

        if task:
            task.run()
        
        # TODO: This caused the browser to hang poorly
        # self.condition.acquire(blocking=True)
        # if len(self.tasks) == 0:
        #     self.condition.wait()
        # self.condition.release()
         