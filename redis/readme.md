1) change password in redis.conf
```    
requirepass password (check what password in microservice env)
```

2) `$ docker build --pull --rm -t redisjson .`


3) `$ docker images`  
you should see something like this:
```
redisjson                         latest    2851900d79c3   4 minutes ago   105MB
```

4) `$ docker run -p 6379:6379 --name redisjson redisjson` 
