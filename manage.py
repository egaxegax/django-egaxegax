#!/usr/bin/env python
import os, sys

sys.path.insert(0, '.')
sys.path.insert(1, 'vendor')

if __name__ == "__main__":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings")

    from django.core.management import execute_from_command_line

    execute_from_command_line(sys.argv)