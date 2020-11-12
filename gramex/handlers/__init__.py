'''
Handlers
'''

from .basehandler import BaseHandler, BaseWebSocketHandler, SetupFailedHandler
from .functionhandler import FunctionHandler
from .websockethandler import WebSocketHandler
from .filehandler import FileHandler
from .authhandler import GoogleAuth, SimpleAuth, LogoutHandler
from .processhandler import ProcessHandler
from .jsonhandler import JSONHandler
from .socialhandler import TwitterRESTHandler, FacebookGraphHandler
from .uploadhandler import UploadHandler
from .capturehandler import CaptureHandler, Capture
from .formhandler import FormHandler
from .pptxhandler import PPTXHandler
from .proxyhandler import ProxyHandler
from .modelhandler import ModelHandler
from .mlhandler import MLHandler
from .filterhandler import FilterHandler
from .drivehandler import DriveHandler

DirectoryHandler = FileHandler

__all__ = [
    'BaseHandler',
    'BaseWebSocketHandler',
    'Capture',
    'CaptureHandler',
    'DirectoryHandler',
    'DriveHandler',
    'FacebookGraphHandler',
    'FileHandler',
    'FilterHandler',
    'FormHandler',
    'FunctionHandler',
    'GoogleAuth',
    'JSONHandler',
    'LogoutHandler',
    'ModelHandler',
    'MLHandler',
    'PPTXHandler',
    'ProcessHandler',
    'ProxyHandler',
    'SetupFailedHandler',
    'SimpleAuth',
    'TwitterRESTHandler',
    'UploadHandler',
    'WebSocketHandler',
]

try:
    # If Gramex enterprise is available, import all handlers
    import gramexenterprise.handlers
    if hasattr(gramexenterprise, 'handlers'):
        from gramexenterprise.handlers import *             # noqa
        __all__ += gramexenterprise.handlers.__all__
except ImportError:
    pass
