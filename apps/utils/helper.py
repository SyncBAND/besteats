from constance import config


def get_config_value(key):
    """
    get config settings
    """
    return getattr(config, key)


def set_config_value(key, value):
    """
    update config settings
    """
    setattr(config, key, value)
