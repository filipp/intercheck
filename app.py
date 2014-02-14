import os
import re
import sys
import logging
import sqlite3
import subprocess
import tornado.ioloop
import tornado.web
from tornado import template


def initialize(self):
    logging.debug('INITIALIZING')
    conn = sqlite3.connect(":memory:")
    cursor = conn.cursor()
    cursor.execute('CREATE TABLE notes (kw text value text)')


class MainHandler(tornado.web.RequestHandler):
    def initialize(self):
        self.loader = template.Loader(os.path.dirname(__file__))

    def get(self):
        self.write(self.loader.load("index.html").generate())
        

class ScanHandler(tornado.web.RequestHandler):
        
    def get(self):
        commands = ('nmap', 'help', '?', '!',)

        out = {'results': list()}
        cmd = self.get_argument('cmd', 'help')

        if cmd == 'help' or cmd not in commands:
            out['results'].append({'raw': 'Available commands:'})
            out['results'].append({'raw': '* nmap - scan your IP'})
            out['results'].append({'raw': '* ?<keyword> - query keyword'})
            out['results'].append({'raw': '* !<keyword> definition - learn <keyword>'})
            out['results'].append({'raw': '* !!<keyword> - forget <keyword>'})
            out['results'].append({'raw': '* help - shows this help message'})

        if cmd == 'nmap':
            host = self.request.headers.get('X-Real-IP', self.request.remote_ip)
            logging.debug('SCANNING %s' % host)
            result = subprocess.check_output(['nmap', host])
            for r in re.finditer(r'(\d+/[a-z]{3})\s([a-z]+)\s+(.+)', result):
                t = r.groups()
                out['results'].append({
                    'port': t[0],
                    'state': t[1],
                    'service': t[2],
                    'raw': "    ".join(r.groups(0))
                })

        self.write(out)


application = tornado.web.Application([
    (r'/', MainHandler),
    (r'/scan/', ScanHandler),
])

if __name__ == '__main__':
    if 'init' in sys.argv:
        initialize()

    application.listen(8888)
    logging.basicConfig(level=logging.DEBUG)
    logging.debug('intercheck ready for action...')
    tornado.ioloop.IOLoop.instance().start()
