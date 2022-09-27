import redis_lock
import redis

conn = redis.Redis()
lock = redis_lock.Lock(conn, name='abcdefg', expire=10)

print(lock.locked(), lock._held)
lock.acquire()
print(lock.locked(), lock._held)
lock.release()