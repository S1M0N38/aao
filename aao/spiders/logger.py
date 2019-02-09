import logging


def logger(name, console_level='INFO', file_level='DEBUG', **kwargs):
    log = logging.getLogger(name)
    log.setLevel(logging.DEBUG)

    console_handler = logging.StreamHandler()
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(message)s', '%H:%M:%S')
    console_handler.setFormatter(formatter)
    console_handler.setLevel(console_level)
    log.addHandler(console_handler)

    file_handler = logging.FileHandler(f'{name}.log')
    formatter = logging.Formatter(
        '%(asctime)s-%(name)s-%(levelname)s-%(message)s')
    file_handler.setFormatter(formatter)
    file_handler.setLevel(file_level)
    log.addHandler(file_handler)

    return log

