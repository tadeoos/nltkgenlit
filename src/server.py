# Import your application as:
# from app import application
# Example:

from app import app
from paste.translogger import TransLogger


# Import CherryPy
import cherrypy

if __name__ == '__main__':

    app_logged = TransLogger(app)

    cherrypy.config.update({
        'engine.autoreload_on': True,
        'log.screen': True
       })
    # Mount the application
    cherrypy.tree.graft(app_logged, "/")

    # Unsubscribe the default server
    cherrypy.server.unsubscribe()

    # Instantiate a new server object
    server = cherrypy._cpserver.Server()

    # Configure the server object
    server.socket_host = "0.0.0.0"
    server.socket_port = 80
    server.thread_pool = 30

    # For SSL Support
    # server.ssl_module            = 'pyopenssl'
    # server.ssl_certificate       = 'ssl/certificate.crt'
    # server.ssl_private_key       = 'ssl/private.key'
    # server.ssl_certificate_chain = 'ssl/bundle.crt'

    # Subscribe this server
    server.subscribe()

    # Start the server engine (Option 1 *and* 2)

    cherrypy.engine.start()
    cherrypy.engine.block()
