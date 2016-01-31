async_mode = 'gevent'

if async_mode == 'gevent':
    from gevent import monkey
    monkey.patch_all()

else:
    raise RuntimeError('Invalid "async_mode"')

from flask import Flask, render_template, g, url_for, request, redirect, session, copy_current_request_context
import flask
from flask_socketio import SocketIO, emit
from flask_login import LoginManager, login_required, login_user, current_user
from mongoengine import connect as connect_mongo

from db.user import User
from db import MongoSessionInterface
from forms.login_form import LoginForm
from twitter import *

from utils.log_helpers import logging, get_ws_log_queue
from utils.work_helpers import Worker

import json, time, random, string

from gevent import joinall


logger = logging.getLogger(__name__)

# Flask from-object configuration; all caps are acknowledged
DATABASE = 'test'
DEBUG = True
SECRET_KEY = 'thisisnosecret'
SESSION_COOKIE_NAME = 'tacklr'

app = Flask(__name__)
app.config.from_object(__name__)
app.session_interface = MongoSessionInterface(db=getattr(app.config, 'database', DATABASE))

# Flask session-based authorization
login_manager = LoginManager()
login_manager.init_app(app)

# Flask Websocket implementation
socketio = SocketIO(app, async_mode=async_mode, logger=False)

tweet_stream = stream_iterator(get_stream())

workers = []


def connect_db():
    logger.debug('connect db ' + app.config['DATABASE'])
    return connect_mongo(app.config['DATABASE'])


@login_manager.user_loader
def load_user(email):
    print 'trying to load', email
    try:
        u = User(email=email)
        return u
    except Exception as e:
        logger.exception(e)
        return None


@app.before_request
def setup_request():
    g.db = connect_db()


@app.teardown_request
def teardown_request(exception):
    db = getattr(g, 'db', None)
    if db is not None:
        db.close()


@app.route('/', methods=['GET', 'POST'])
def index():
    return render_template('index.html', form=LoginForm(email='test@email.com', password='abcdefgh'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm(request.form)
    if form.validate():
        user = User.objects.get(email=request.form['email'])
        password = request.form['password']
        if isinstance(password, list):
            password = ''.join([str(i) for i in password])

        logger.debug('user: {0} password (actual): {1} password (attempted): {2} length diff: {3}'.format(user.email, user.hashed_password, password, len(user.hashed_password) - len(password)))

        #logger.debug('logging in {0} with pw {1}'.format(user.email, password))

        if user.try_login(request.form['password']):
            logger.debug('logging in user: {0}'.format(user.email))
            print 'login_user', login_user(user)

            flask.flash('Logged in successfully.')

            # user is now logged in so a redirect will suffice
            return redirect('home')
        else:
            logger.debug('invalid user creds for {0}'.format(user.email))
    else:
        logger.error('invalid form')
    return render_template('index.html', form=form)


@app.route('/home', methods=['GET', 'POST'])
@login_required
def home():
    return render_template('home.html')


@socketio.on('log')
def start_log_worker(req):

    @copy_current_request_context
    def emit_(l):
            print 'emitting!!', l
            emit('log message', l)

    q = get_ws_log_queue()

    worker = Worker(emit_, q)
    worker.start()

    workers.append(worker)


@socketio.on('page_request')
def get_new_page(req):
    print 'DDDDDD______', request.namespace
    print 'new_page request', json.dumps(req, indent=1)
    print ''.join([str(i) for i in req['auth']['password']['words']])
    page_html = render_template((lambda x: x if x.endswith('.html') else x + '.html')(req['req']['page']))
    print page_html
    emit('page_response', {'data': page_html})


@socketio.on('connect')
def connect_log():
    print 'connected'


def extract_one(stream):
    tweet = None
    while tweet is None:
        print 'iterating'
        try:
            #tweet = stream.next()
            tweet = dict( id=random.randint(1, 100000)
                        , text=''.join(random.sample(string.letters, 40))
                        , timestamp=time.time()
                        , user=''.join(random.sample('abcde', 1)).lower())
        except Exception as e:
            print 'exception', e
            #print stream.status_code
            time.sleep(2)
            tweet = None
        else:
            return tweet


# def extract_on_abrv(stream):
#     match_set = set(abreviations.keys())
#     tweet, key_match = None, None
#     while not key_match:
#         tweet = extract_one(stream)
#         print tweet['text']
#         key_match = match_set.intersection(set(getattr(tweet, 'text', '').lower().split()))
#     return key_match, abreviations[key_match]

def emit_tweet(event_name="tweet", func=None, **kwargs):
    tweet = extract_one(tweet_stream)
    tweet = func(tweet, **kwargs) if func else tweet

    print json.dumps(tweet, indent=1)
    print 'emitting tweet id#', tweet['id']

    emit(event_name, tweet)


def emit_tweets():
    while True:
        emit_tweet("push_tweet")
        time.sleep(1)


@app.route('/js/<doc>', methods=['GET', 'POST'])
def get_js():
    logger.debug('.js file request for: {0}'.format(doc))
    return app.send_static_file('js', doc)


global count
count = 0


@socketio.on('get tweet')
def get_tweet(msg):
    global count
    print 'beginning emit callback sequence #%d' % count
    count += 1
    emit_tweet()


def uniqueness(tweet):
    data = []
    words = tweet['text'].lower()
    for word in words:
        if word:
            data.append({'name': word, 'y': (100*float(words.count(word))/float(len(words)))})
    tweet['highcharts_data'] = data
    return tweet


@socketio.on('get tweet complete')
def client_confirmation(msg):
    print 'client confirmation of get tweet complete'


@app.route('/ajax/<subscription>', methods=['GET'])
def ajax_driven_subscription():
    logger.debug('Ajax request for subscription to {0}'.format(subscription))


@app.route('/react', methods=['GET'])
def react():
    return render_template('react.html')


if __name__ == '__main__':
    try:
        socketio.run(app, debug=True)
    except KeyboardInterrupt:
        pass

    for w in workers:
        w.stop()
    joinall(workers)
