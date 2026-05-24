import redis 

#Connect to Redis server
redis_client = redis.Redis(host='localhost', port=6380, decode_responses=True)

try:
    print(redis_client.ping())
    print("Connected to Redis!")
except redis.ConnectionError:
    print("Redis is not running")
    print(redis_client)
    exit()

# #Simple String Operations    
# redis_client.set("name", "Kiran")
# print(redis_client.get("name"))

# #Hash Operations
# redis_client.hset("user-session:123", mapping={
#     "user_id": 1,
#     "username": "Ashura",
#     "email": "ashura@example.com"
# })
# print(redis_client.hgetall("user-session:123"))
# redis_client.close()
# print(redis_client.hgetall("user-session:123"))

# #List Operations
# redis_client.rpush("recent-activities", "Logged In")
# redis_client.rpush("recent-activities", "Viewed Post 1")
# print(redis_client.lrange("recent-activities", 0, -1))

# #Set Operations
# redis_client.sadd("active-users", "user1")
# redis_client.sadd("active-users", "user2")
# print(redis_client.smembers("active-users"))

#Cache Example
# redis_client.setex("cached-data", 60, "This is cached data with a TTL of 60 seconds")
if redis_client.exists("cached-data"):
    print("Cached data exists:", redis_client.get("cached-data"))
else:
    print("Cached data does not exist")




# from redis.cluster import RedisCluster
# # Connect to Redis Cluster
# try: 
#     redis_cluster_client = RedisCluster(host='localhost', port=16379, decode_responses=True)
#     print(redis_cluster_client)
#     redis_cluster_client.set("cluseter-key", "Hello Redis Cluster!")
#     print(redis_cluster_client.get("cluseter-key"))
# except Exception as e:
#     print("Error connecting to Redis Cluster:", e)