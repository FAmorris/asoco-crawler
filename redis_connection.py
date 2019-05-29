from config import REDIS_HOST,REDIS_PASSWORD,REDIS_PORT
import redis


client = redis.StrictRedis(host=REDIS_HOST,password=REDIS_PASSWORD,port=REDIS_PORT)