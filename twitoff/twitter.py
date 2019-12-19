import basilica
import tweepy
from decouple import config
from .models import DB, Tweets, User

TWITTER_USERS = ['elonmusk', 'nasa', 'neiltyson', 'pattonoswalt']

AUTH = tweepy.OAuthHandler(config('TWITTER_CONSUMER_API_KEY'),
                           config('TWITTER_CONSUMER_API_SECRET'))
AUTH.set_access_token(config('TWITTER_ACCESS_TOKEN'),
                      config('TWITTER_ACCESS_TOKEN_SECRET'))
TWITTER = tweepy.API(AUTH)
BASILICA = basilica.Connection(config('BASILICA_KEY'))

def add_or_update_user(username):
    '''Add user & their tweets to db'''
    try:
        # Get user info
        twitter_user = TWITTER.get_user(username)

        # Add user info to User table in db
        db_user = User(id=twitter_user.id,
                       username=twitter_user.screen_name,
                       followers=twitter_user.followers_count,
                       newest_tweet_id=newest_tweet_id)
        DB.session.add(db_user)

        # Add as many recent non-retweet/reply tweets as possible
        # 200 is a Twitter API limit for a single request
        tweets = twitter_user.timeline(count=200,
                                       exclude_replies=True,
                                       include_rts=False,
                                       tweet_mode='extended',
                                       since_id=db_user.newest_tweet_id)

        # import pdb; pdb.set_trace()
        if tweets:
            db_user.newest_tweet_id = tweets[0].id

        # Loop over each tweet
        for tweet in tweets:

            # Get Basilica embedding for each tweet
            embedding = BASILICA.embed_sentence(tweet.full_text,
                                                model='twitter')
            
            # Add tweet info to Twets table in db
            db_tweet = Tweets(id=tweet.id,
                              text=tweet.full_text[:300],
                              embedding=embedding)
            db_user.tweets.append(db_tweet)
            DB.session.add(db_tweet)
    except Exception as e:
        print(f'Error processing {username}: {e}')
        raise e
    else:
        DB.session.commit()

def add_default_users(users=TWITTER_USERS):
    '''
    Add/update a list of default users to populate the db on start
    '''
    for user in users:
        add_or_update_user(user)

def update_all_users():
    for user in User.query.all():
        add_or_update_user(user.name)