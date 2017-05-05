from flask import Flask, g

from .db import RedisClient

__all__ = ['app']

app = Flask(__name__)


def get_conn():
    """
    Opens a new redis connection if there is none yet for the
    current application context.
    """
    if not hasattr(g, 'redis_client'):
        g.redis_client = RedisClient(type='formal')
    return g.redis_client


@app.route('/')
def index():
    return '<h2>Welcome to Proxy Filter System</h2>'


@app.route('/random')
def get_proxy():
    """
    Get a proxy
    """
    conn = get_conn()
    return conn.random()


if __name__ == '__main__':
    app.run()
