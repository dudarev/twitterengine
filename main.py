#!/usr/bin/env python
import wsgiref.handlers
import logging
from google.appengine.ext import webapp, db
from google.appengine.ext.webapp import template
import twitter, os, random
import re, htmlentitydefs
import yaml
import sys

import users
from twitter_oauth_handler import OAuthClient,OAuthHandler

# Datamodel
class Tweet(db.Model):
  id = db.IntegerProperty()
  text = db.StringProperty(required=True, multiline=True)
  created_at = db.StringProperty(required=True)
  from_user = db.StringProperty(required=True)
  from_user_id = db.IntegerProperty(required=True)
  to_user = db.StringProperty()
  to_user_id = db.IntegerProperty()
  source = db.StringProperty()
  profile_image_url = db.StringProperty()
  term = db.StringProperty(required=True)
  votes_count = db.IntegerProperty()
  users_voted = db.StringListProperty()

def unescape(text):
    def fixup(m):
        text = m.group(0)
        if text[:2] == "&#":
            # character reference
            try:
                if text[:3] == "&#x":
                    return unichr(int(text[3:-1], 16))
                else:
                    return unichr(int(text[2:-1]))
            except ValueError:
                pass
        else:
            # named entity
            try:
                text = unichr(htmlentitydefs.name2codepoint[text[1:-1]])
            except KeyError:
                pass
        return text # leave as is
    return re.sub("&#?\w+;", fixup, text)

def get_config():
  # Get config from config.yaml
  f = open('config.yaml')
  c = yaml.load(f)
  f.close()
  return c


class IndexHandler(webapp.RequestHandler):
  sort_order = "-id"
  show_votes = False
  def get(self):
    config = get_config()

    # Tweets
    count = Tweet.all().count(1000)
    page = int(self.request.get('page', 1))
    prev_page = page-1
    next_page = page+1
    show_prev_page = (page>1)
    show_next_page = (page*20<count)
    tweets = []
    for tweet in Tweet.all().order(self.sort_order).order("-id").fetch(20, (page-1)*20):
      tweet.status = twitter.Status(id=tweet.id, created_at=tweet.created_at)
      tweet.text = unescape(tweet.text)
      tweet.source = unescape(tweet.source)
      tweets.append(tweet)

    # User cloud
    cloud_tweets = Tweet.all().order('-id').fetch(300)
    cloud_items = {}
    cloud = []
    max = 0
    for tw in cloud_tweets:
      cloud_items[tw.from_user] = 0
    for tw in cloud_tweets:
      cloud_items[tw.from_user] = cloud_items[tw.from_user]+1
      if cloud_items[tw.from_user]>max: max = cloud_items[tw.from_user]
    for k in cloud_items:
      cloud.append({'name':k, 'lower_name':k.lower(), 'count':cloud_items[k], 'html':'<a href="http://twitter.com/%s" style="font-size:%spx">%s</a>' % (k, (9 + 16*(1.0*cloud_items[k]/max)), k)})

    user = users.get_current_user(self)
    if user:
      login_logout_link = "<strong>%s</strong> | <a href=\"%s\">Logout</a>" % (user,users.create_logout_url(self,"/"))
    else:
      login_logout_link = "<a href=\"%s\">Login</a>" % users.create_login_url(self,"/")
    nav_link = login_logout_link
      
    path = os.path.join(os.path.dirname(__file__), 'index.html')
    self.response.out.write(template.render(path, locals()))
    logging.debug('Start guestbook signing request')

class TopHandler(IndexHandler):
  sort_order = "-votes_count"
  show_votes = True


class RssHandler(webapp.RequestHandler):
  def get(self):
    config = get_config()
    path = os.path.join(os.path.dirname(__file__), 'rss.html')
    self.response.headers['Content-Type'] = 'application/xml+rss'
    self.response.out.write(template.render(path, {'config':config, 'tweets':Tweet.all().order('-id').fetch(20)}))


class ImportHandler(webapp.RequestHandler):
  def get(self):
    config = get_config()

    # Array of all queries
    t = []
    for u in config["users"]:
      t.append('@'+str(u))
      t.append('from:'+str(u))
    for h in config["hashes"]:
      t.append('#'+str(h))

    # We want to limit number of queries to twitter api, but max query length is 140 chars
    terms = []
    new_term = []
    for item in t:
      new_term.append(item)
      if len(" OR ".join(new_term))>140:
        new_term.pop()
        terms.append(" OR ".join(new_term))
        new_term = [item]
    if len(new_term)>0: terms.append(" OR ".join(new_term))

    # Connect to API
    api = twitter.Api(username=config["twitter_username"], password=config["twitter_password"])

    # Do searches and save results
    for term in terms:
      since_id = 0
      for x in Tweet.all().filter('term = ', term).order('-id').fetch(1):
        since_id=x.id

      statuses = api.Search(terms=term, since_id=since_id)

      for status in statuses:
        tw = Tweet.get_or_insert("id%s" % status.id, 
                                 id=status.id, 
                                 text=status.text, 
                                 created_at=status.created_at, 
                                 to_user=status.to_user, 
                                 to_user_id=status.to_user_id, 
                                 from_user=status.from_user, 
                                 from_user_id=status.from_user_id, 
                                 source=status.source, 
                                 profile_image_url=status.profile_image_url, 
                                 term=term);
        # (this tweet might have been a match for a different query than before, update datastore)
        tw.term = term
        tw.put()
    self.response.out.write('success')

class VoteHandler(webapp.RequestHandler):
  def get(self):
    config = get_config()
    vtweet = self.request.get('tweetid')
    vuser = str(users.get_current_user(self))
    if vuser:
      # Проверим не голосовал ли юзер за этот твит
      try:
        query = db.GqlQuery("SELECT * FROM Tweet WHERE id=:1", int(vtweet))
        if query:
          tweet = query[0]
        else:
          self.response.out.write('error_tweet_not_found')
          return
      except:
        self.response.out.write('error_query_exception %s' % vtweet)
        return
      if vuser in tweet.users_voted:
        self.response.out.write('already')
      else:
        # Добавляем данные о голосовании
        tweet.users_voted.append(vuser)
        if tweet.votes_count:
          tweet.votes_count += 1
        else:
          tweet.votes_count = 1
        try:
          tweet.put()
          self.response.out.write('success')
        except:
          self.response.out.write(str(tweet.users_voted))
    else:
      self.response.out.write('no login')

def main():
  logging.getLogger().setLevel(logging.DEBUG)
  application = webapp.WSGIApplication([
      ('/', IndexHandler), 
      ('/top', TopHandler),
      ('/rss', RssHandler), 
      ('/import', ImportHandler),
      ('/vote', VoteHandler),
      ('/oauth/(.*)/(.*)', OAuthHandler),
      ], debug=True)
  wsgiref.handlers.CGIHandler().run(application)

if __name__ == '__main__': main()

