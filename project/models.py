from google.appengine.ext import db

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

