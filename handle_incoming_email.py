# -*- coding: utf-8 -*-

import logging
import email
import datetime

from google.appengine.ext.webapp.mail_handlers import InboundMailHandler
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext import webapp, db

# Datamodel
class Email(db.Model):
    subject = db.StringProperty()
    sender = db.EmailProperty()
    body = db.TextProperty()

class MailHandler(InboundMailHandler):
    def receive(self, message):
        e = Email()
        e.sender = message.sender
        e.subject = message.subject
        bodies = message.bodies(content_type='text/plain')
        e.body = ''
        for body in bodies:
            e.body = e.body + body[1].decode()
        e.put()

application = webapp.WSGIApplication([ MailHandler.mapping() ], debug=True)

def main():
    run_wsgi_app(application)

if __name__ == "__main__":
    main()
