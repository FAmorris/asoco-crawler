cd /d %~dp0
cd ./redis
redis-server --service-install redis.windows.conf
@pause