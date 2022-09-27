from datetime import date, datetime
from apscheduler.triggers.interval import IntervalTrigger
from apscheduler.triggers.cron import CronTrigger

data = {
    # "trigger" : "cron",
    "seconds" : 10,
    "minutes" : 1
}

# def get_time_delta(data):
#     slots = ["seconds" , "minutes", "hours", "week", "days", "start_date", "end_date"]
#     res = {}
#     for key in slots:
#         if key in data:
#             res[key] = data[key]
#     return datetime.timedelta(**res)

# time_delta = get_time_delta(data=data)

# # print(time_delta == datetime.timedelta(minutes=1, seconds=10))
# dlt = datetime.timedelta(minutes=1, start_date='2022-09-10')
# print(dlt)

cron1 = IntervalTrigger(**data)
cron2 = IntervalTrigger(**data)

print(datetime.now().date().strftime('%Y-%m-%d') == '2022-09-07')
