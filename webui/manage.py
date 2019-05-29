#!/usr/bin/env python
import os
import sys

from json_manager import settings

sys.path.append(settings.CRAWLER_DIR)
sys.path.append(settings.WEIBO_DIR)
import watch

if __name__ == "__main__":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "json_manager.settings")
    try:
        from django.core.management import execute_from_command_line
    except ImportError:
        # The above import may fail for some other reason. Ensure that the
        # issue is really that Django is missing to avoid masking other
        # exceptions on Python 2.
        try:
            import django
        except ImportError:
            raise ImportError(
                "Couldn't import Django. Are you sure it's installed and "
                "available on your PYTHONPATH environment variable? Did you "
                "forget to activate a virtual environment?"
            )
        raise
    # 当web程序被杀死时，监控程序也被杀死了
    try:
        watch.start()
        execute_from_command_line(sys.argv)
    except KeyboardInterrupt:
        # watch.stop_all()
        pass
