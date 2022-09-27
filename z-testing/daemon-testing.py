from multiprocessing import Process
from apscheduler.schedulers.background import BackgroundScheduler

from time import sleep

def print_daemon_1():
    while True:
        print('this is daemon 1!')
        sleep(5)

def print_daemon_2():
    sleep(2)
    while True:
        print('this is daemon 2!')
        sleep(5)

def print_scheduler():
    print('this is scheduler!')

process1 = Process(daemon=True, target=print_daemon_1)
process2 = Process(daemon=True, target=print_daemon_2)
# scheduler = BackgroundScheduler()
# scheduler.add_job(
#     id='job-testing',
#     func=print_scheduler,
#     trigger='interval',
#     seconds=5
# )

process1.start()
process2.start()

while True:
    try:
        sleep(5)
    except KeyboardInterrupt:
        process.terminate()
        scheduler.shutdown()