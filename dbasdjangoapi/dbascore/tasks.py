import requests
from django.conf import settings

# your tasks here

def request_action(method, json, urls=settings.SCHEDULER_URL):

    action = getattr(requests, method)
    print(json)

    for prefix in urls:
        try:
            url = prefix + 'core/jobs/'
            action(url=url, json=json)
            print("%sed to: %s" % (method, url))
        except Exception as e:
            print ('failed to %s to: %s' % (method, url))
