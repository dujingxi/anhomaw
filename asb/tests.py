from django.test import TestCase

from tornado.httpserver import HTTPServer
from tornado.httpclient import HTTPClient

# Create your tests here.
import datetime
from django.middleware import security

n = datetime.datetime.now()
print ("now is %s"%n)