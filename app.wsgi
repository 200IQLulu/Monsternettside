import sys
import site
import os

site.addsitedir('/var/www/html/env/lib/python3.13/site-packages')

sys.path.insert(0, '/var/www/html')

os.chdir('/var/www/html')

os.environ['VIRTUAL_ENV'] = '/var/www/html/env'
os.environ['PATH'] = '/var/www/html/env/bin:' + os.environ['PATH']

from app import app as application
