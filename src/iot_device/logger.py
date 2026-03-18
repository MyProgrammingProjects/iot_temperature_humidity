class LogLevel:
    TRACE = 4
    INFO = 3
    WARN = 2
    ERROR = 1
    FATAL = 0

# Set the current log level
_logLevel = LogLevel.WARN

def log_trace(msg):
    if(_logLevel>= LogLevel.TRACE):
        print(f"TRACE: {msg}")

def log_info(msg):
    if(_logLevel>= LogLevel.INFO):
        print(f"INFO: {msg}")

def log_warn(msg):
    if(_logLevel>= LogLevel.WARN):
        print(f"WARN: {msg}")

def log_error(msg):
    if(_logLevel>= LogLevel.ERROR):
        print(f"ERROR: {msg}")