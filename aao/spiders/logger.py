import logging

# create logger with 'spam_application'
logger = logging.getLogger('spider')
logger.setLevel(logging.DEBUG)
# create console handler with a higher log level
ch = logging.StreamHandler()
ch.setLevel(logging.WARNING)
# create formatter and add it to the handlers
formatter = logging.Formatter('%(asctime)s-%(name)s-%(levelname)s-%(message)s')
ch.setFormatter(formatter)
# add the handlers to the logger
logger.addHandler(ch)
