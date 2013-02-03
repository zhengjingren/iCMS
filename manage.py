from flask.ext.script import Manager, prompt, prompt_pass
from iCMS.app import app, db
import iCMS.views
from iCMS.models import User


manager = Manager(app)
app.config.from_pyfile('_config/dev.py', silent=True)


@manager.command
def create_all(pro=False):
    if pro:
        app.config.from_pyfile('_config/pro.py', silent=True)
    db.create_all()


@manager.command
def add_user(pro=False):
    if pro:
        app.config.from_pyfile('_config/pro.py', silent=True)
    username = prompt('Username')
    password = prompt_pass('Password')
    user = User(username, password)
    db.session.add(user)
    db.session.commit()


@manager.command
def run_with_tornado(port=8888):
    """
    Don't run this in dev env.
    """
    app.config.from_pyfile('_config/pro.py', silent=True)
    from tornado.wsgi import WSGIContainer
    from tornado.httpserver import HTTPServer
    from tornado.ioloop import IOLoop

    # Enable pretty logging.
    import sys
    import time
    import logging

    try:
        import curses
    except ImportError:
        curses = None

    def enable_pretty_logging(level='info'):
        """Turns on formatted logging output as configured.

        This is called automatically by `WeRoBot.run()`.
        """
        root_logger = logging.getLogger()
        root_logger.setLevel(getattr(logging, level.upper()))

        if not root_logger.handlers:
            # Set up color if we are in a tty and curses is installed
            color = False
            if curses and sys.stderr.isatty():
                try:
                    curses.setupterm()
                    if curses.tigetnum("colors") > 0:
                        color = True
                except Exception:
                    pass
            channel = logging.StreamHandler()
            channel.setFormatter(_LogFormatter(color=color))
            root_logger.addHandler(channel)


    class _LogFormatter(logging.Formatter):
        def __init__(self, color, *args, **kwargs):
            logging.Formatter.__init__(self, *args, **kwargs)
            self._color = color
            if color:
                # The curses module has some str/bytes confusion in
                # python3.  Until version 3.2.3, most methods return
                # bytes, but only accept strings.  In addition, we want to
                # output these strings with the logging module, which
                # works with unicode strings.  The explicit calls to
                # unicode() below are harmless in python2 but will do the
                # right conversion in python 3.
                fg_color = (curses.tigetstr("setaf") or
                            curses.tigetstr("setf") or "")
                if (3, 0) < sys.version_info < (3, 2, 3):
                    fg_color = unicode(fg_color, "ascii")
                self._colors = {
                    logging.DEBUG: unicode(curses.tparm(fg_color, 4),  # Blue
                        "ascii"),
                    logging.INFO: unicode(curses.tparm(fg_color, 2),  # Green
                        "ascii"),
                    logging.WARNING: unicode(curses.tparm(fg_color, 3),  # Yellow
                        "ascii"),
                    logging.ERROR: unicode(curses.tparm(fg_color, 1),  # Red
                        "ascii"),
                    }
                self._normal = unicode(curses.tigetstr("sgr0"), "ascii")

        def format(self, record):
            try:
                record.message = record.getMessage()
            except Exception as e:
                record.message = "Bad message (%r): %r" % (e, record.__dict__)
            record.asctime = time.strftime(
                "%y%m%d %H:%M:%S", self.converter(record.created))
            prefix = '[%(levelname)1.1s %(asctime)s %(module)s:%(lineno)d]' %\
                     record.__dict__
            if self._color:
                prefix = (self._colors.get(record.levelno, self._normal) +
                          prefix + self._normal)
            formatted = prefix + " " + record.message
            if record.exc_info:
                if not record.exc_text:
                    record.exc_text = self.formatException(record.exc_info)
            if record.exc_text:
                formatted = formatted.rstrip() + "\n" + record.exc_text
            return formatted.replace("\n", "\n    ")

    enable_pretty_logging()


    http_server = HTTPServer(WSGIContainer(app))
    http_server.listen(port)
    IOLoop.instance().start()


if __name__ == '__main__':
    manager.run()