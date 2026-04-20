import redis 

redis_client = redis.Redis(host='localhost', port=6379, decode_responses=True)

# redis_client.set("name", "Kiran")
# print(redis_client.get("name"))

# redis_client.hset("user-session:123", mapping={
#     "user_id": 1,
#     "username": "Ashura",
#     "email": "ashura@example.com"
# })
print(redis_client.hgetall("user-session:123"))