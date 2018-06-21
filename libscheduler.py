from apscheduler.schedulers.background import BackgroundScheduler
import logging, datetime
import logging.handlers


class TaskScheduler():
    def __init__(self):
        self.data = {}
        logger = logging.getLogger('apscheduler')
        logging.basicConfig(filename='./schedule.log', level=logging.INFO)
        loghandler = logging.handlers.RotatingFileHandler('./schedule.log', maxBytes=1024, backupCount=3)
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
    print('I am interval ... ' + datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))

def cron_task():
    print('I am icon ... ' + datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))

if __name__ == "__main__":
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
