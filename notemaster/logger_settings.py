class LoggerSettings:

    log_location = ''

    def __init__(self, location):
        self.log_location = location

    def get_location(self):
        return self.log_location

    def set_location(self, location):
        self.log_location = location

    def get_logger_settings(self):
        log_settings = {
            'version': 1,
            'disable_existing_loggers': False,
            'formatters': {
                'large': {
                    'format': '%(asctime)s|%(levelname)s|%(process)d|%(name)s:%(funcName)s, line=%(lineno)d|%(message)s'
                },
                'tiny': {
                    # 'format': '%(asctime)s  %(message)s'
                    'format': '%(asctime)s  %(module)s  %(message)s'
                }
            },
            'handlers': {
                'errors_file': {
                    'level': 'ERROR',
                    'class': 'logging.handlers.TimedRotatingFileHandler',
                    'when': 'midnight',
                    'interval': 1,
                    'filename': self.log_location + 'ErrorLoggers.log',
                    'formatter': 'large',
                },
                'info_file': {
                    'level': 'INFO',
                    'class': 'logging.handlers.TimedRotatingFileHandler',
                    'when': 'midnight',
                    'interval': 1,
                    'filename': self.log_location + 'InfoLoggers.log',
                    'formatter': 'large',
                },
                'debug_file': {
                    'level': 'DEBUG',
                    'class': 'logging.handlers.TimedRotatingFileHandler',
                    'when': 'midnight',
                    'interval': 1,
                    'filename': self.log_location + 'DebugLoggers.log',
                    'formatter': 'large',
                },
                'console': {
                    'level': 'DEBUG',
                    'class': 'logging.StreamHandler',
                    'formatter': 'tiny',
                },
            },
            'loggers': {
                # 'hal_portal': {
                '': {
                    'handlers': ['debug_file', 'errors_file', 'info_file', 'console'],
                    # 'handlers': ['debug_file', 'errors_file', 'info_file'],
                    # the logger needs to have a level but it doesn't do anything, the level parameter in
                    # the handler is what determines what logger level gets written in what log.
                    'level': 'DEBUG',
                },
                'hal_portal.info': {
                    'handlers': ['info_file'],
                    'level': 'DEBUG',
                    'propagate': True,  # Propagate is True by default. It's just here as a reminder.
                },
                'hal_portal.error': {
                    'handlers': ['errors_file'],
                    'level': 'DEBUG',
                    'propagate': True,
                },
                'impala': {
                    'handlers': ['console'],
                    'level': 'WARNING',
                    'propagate': False,
                },
                'urllib3': {
                    'handlers': ['debug_file', 'errors_file', 'info_file', 'console'],
                    'level': 'INFO',
                },
            },
        }

        return log_settings
