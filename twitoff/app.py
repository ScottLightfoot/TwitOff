from decouple import config
from flask import Flask, render_template, request

from .models import DB, User
from .twitter import add_or_update_user, update_all_users, add_default_users
from .predict import predict_user

from dotenv import load_dotenv
load_dotenv()

def create_app():
    '''Create & config instance of Flask'''
    app = Flask(__name__)

    # config db
    app.config['SQLALCHEMY_DATABASE_URI'] = config('DATABASE_URL')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # connect to our app
    DB.init_app(app)

    @app.route('/')
    def root():
        users = User.query.all()
        return render_template('base.html', title='TwitOff!', users=users)

    @app.route('/user', methods=['POST'])
    @app.route('/user/<name>', methods=['GET'])
    def  user(name=None, message=''):
        name = name or request.values['user_name']
        try:
            if request.method == 'POST':
                add_or_update_user(name)
                message = 'User {} successfully added!'.format(name)
            tweets = User.query.filter(User.username == name).one().tweets
        except Exception as e:
                message = 'Error adding {}: {}'.format(name, e)
                tweets = []
        return render_template('user.html', title=name, tweets=tweets, message=message)
    
    @app.route('/compare', methods=['POST'])
    def compare(message=''):
        user1, user2 = sorted([request.values['user1'],
                               request.values['user2']])
        if user1 == user2:
            message = 'Cannot compare a user to themselves!'
        else:
            prediction = predict_user(user1, user2, request.values['tweet_text'])
            message = '"{}" is more likely to be said by {} than {}'.format(
                request.values['tweet_text'], user1 if prediction else user2,
                user2 if prediction else user1)
        return render_template('prediction.html', title='Prediction', message=message)
    
    @app.route('/update')
    def update():
        update_all_users()
        return render_template('base.html', users=User.query.all(), title='All Tweets updated!!!')

    @app.route('/reset')
    def reset():
        DB.drop_all()
        DB.create_all()
        return render_template('base.html', title = 'Panic Button!', users=[])
    
    @app.route('/add_default')
    def add_default():
        add_default_users()
        return render_template('base.html', users=User.query.all(), title='Added default users!')
    
    return app
