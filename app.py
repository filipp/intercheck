import re
import logging
import subprocess
import tornado.ioloop
import tornado.web
from tornado import template

class MainHandler(tornado.web.RequestHandler):
    def initialize(self):
        self.loader = template.Loader('/Users/filipp/Projects/intercheck')

    def get(self):
        self.write(self.loader.load("index.html").generate())
        

class ScanHandler(tornado.web.RequestHandler):
    def get(self):
        logging.debug('SCANNING!')
        result = subprocess.check_output(['nmap', self.request.remote_ip])
        for r in re.finditer(r'(\d+/[a-z]{3})\s([a-z]+)\s+(.+)', result):
            t = r.groups()
            self.write({'port': t[0], 'state': t[1], 'service': t[2]})


application = tornado.web.Application([
    (r'/', MainHandler),
    (r'/scan/', ScanHandler),
])

if __name__ == '__main__':
    application.listen(8888)
    logging.basicConfig(level=logging.DEBUG)
    logging.debug('intercheck ready for action...')
    tornado.ioloop.IOLoop.instance().start()
