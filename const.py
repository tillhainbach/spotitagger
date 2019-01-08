import logzero
import os

_log_format = ("%(color)s%(levelname)s:%(end_color)s %(message)s")
formatter = logzero.LogFormatter(fmt=_log_format)
log_file = os.path.join(os.getcwd(),'spotitagger.txt')

# options
log = logzero.setup_logger(formatter=formatter)

args = None
