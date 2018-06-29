from apscheduler.schedulers.background import BackgroundScheduler
import logging, datetime
import logging.handlers
import signal


class TaskScheduler():
    def __init__(self):
        self.data = {}
        logger = logging.getLogger('apscheduler')
        logger.setLevel(logging.INFO)
        fmt = "%(asctime)s - %(name)s - %(filename)s[line:%(lineno)d] - %(levelname)s - %(message)s"
        log_format = logging.Formatter(fmt)
        loghandler = logging.handlers.RotatingFileHandler('./schedule.log', maxBytes=1024 * 1024 * 3, backupCount=3)
        loghandler.setFormatter(log_format)
        logger.addHandler(loghandler)

    def get_scheduler(self, title):
        if title in self.data:
            return self.data[title]
        return None

    def add(self, title, scheduler):
        if title not in self.data:
            self.data[title] = scheduler
            scheduler.start()

    def remove(self, title):
        if title in self.data:
            self.data[title].shutdown(wait=False)
            del self.data[title]

    def pause(self, title):
        if title in self.data:
            self.data[title].pause()
            return 0
        else:
            return -1

    def resume(self, title):
        if title in self.data:
            self.data[title].resume()
            return 0
        else:
            return -1

GLOBAL_TASK = TaskScheduler()

def interval_task():
    print('I am interval ... ' + datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))

def date_task():
    print('I am date ... ' + datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))

def cron_task():
    print('I am icon ... ' + datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))

flag = 0
def modify_task(signum, stack):
    global flag
    if flag:
        GLOBAL_TASK.pause('interval_task')
        GLOBAL_TASK.resume('cron_task')
        flag = 0
    else:
        GLOBAL_TASK.resume('interval_task')
        GLOBAL_TASK.pause('cron_task')
        flag = 1
        

if __name__ == "__main__":
    signal.signal(signal.SIGUSR1, modify_task)

    sched = BackgroundScheduler()
    sched.add_job(interval_task, 'interval', seconds=10)
    GLOBAL_TASK.add('interval_task', sched)

    sched = BackgroundScheduler()
    sched.add_job(date_task, 'date', next_run_time=datetime.datetime.now() + datetime.timedelta(seconds=3))
    GLOBAL_TASK.add('date_task', sched)

    sched = BackgroundScheduler()
    sched.add_job(cron_task, 'cron', second=10)
    GLOBAL_TASK.add('cron_task', sched)

    while(1):
        pass
