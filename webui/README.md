运行django程序时，默认会开启进程检测文件变化，这样会给日志文件
加锁导致日志无法写入。可以使用命令`python manage.py runserver --noreload`
来禁用自动加载。

py.test haha/tests.py