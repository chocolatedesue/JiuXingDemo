import threading

# QUERY_INTERVIEWER = "query_interviewer"
# FINiSH_INTERVIEW = "finish_interview"

COMMIT_SIGNAL = "commit_signal"


class SemaphoreManager:
    # def __init__(self):
    #     self.semaphores = {}
    semaphores = {}

    @classmethod
    def  acquire_semaphore(cls, key):
        if key in cls.semaphores:
            cls.semaphores[key].acquire()
        else:
            cls.semaphores[key] = threading.Semaphore(1)
            cls.semaphores[key].acquire()

    @classmethod
    def release_semaphore(cls, key):
        if key in cls.semaphores:
            cls.semaphores[key].release()

    @classmethod
    def acquire_semaphore(cls, key):
        if key in cls.semaphores:
            cls.semaphores[key].acquire()
        else:
            cls.semaphores[key] = threading.Semaphore(1)
            cls.semaphores[key].acquire()

    @classmethod
    def has_semaphore(cls, key):
        return key in cls.semaphores

    # def acquire_semaphore(self, key):
    #     if key in self.semaphores:
    #         self.semaphores[key].acquire()
    #     else:
    #         self.semaphores[key] = threading.Semaphore(1)
    #         self.semaphores[key].acquire()

    # def has_semaphore(self, key):
    #     return key in self.semaphores