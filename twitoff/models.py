'''SQLAlchemy Models for TwitOff'''
from flask_sqlalchemy import SQLAlchemy

DB = SQLAlchemy()

class User(DB.Model):
    '''Twitter users that we query and store historical tweets for'''
    id = DB.Column(DB.BigInteger, primary_key=True)
    username = DB.Column(DB.String(15), nullable=False)
    followers = DB.Column(DB.BigInteger, nullable=False)
    
    # Tweets IDs are ordinal ints
    newest_tweet_id = DB.Column(DB.BigInteger, nullable=False)
    
    def __repr__(self):
        return '<User {}>'.format(self.name)
    
class Tweets(DB.Model):
    '''Stores Tweets'''
    id = DB.Column(DB.BigInteger, primary_key=True)
    text = DB.Column(DB.Unicode(300))
    user_id = DB.Column(DB.BigInteger, DB.ForeignKey('user.id'), nullable=False)
    user = DB.relationship('User', backref=DB.backref('tweets', lazy=True))

    embedding = DB.Column(DB.PickleType, nullable=False)

    def __repr__(self):
        return '<Tweet {}>'.format(self.text)

class Comparison(DB.Model):
    """Comparison between twitter users and a user generated tweet, and prediction/
    probabilities for which user is more likely to have tweeted the tweet"""
    id = DB.Column(DB.Integer, primary_key=True, autoincrement=True)
    text = DB.Column(DB.Unicode(300))
    predicted_user = DB.Column(DB.String(15), nullable=False)
    user1_name = DB.Column(DB.String(15), nullable=False)
    user2_name = DB.Column(DB.String(15), nullable=False)
    user1_prob = DB.Column(DB.Float, nullable=False)
    user2_prob = DB.Column(DB.Float, nullable=False)