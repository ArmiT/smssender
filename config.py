__author__ = 'ArmiT'

import ConfigParser

CONFIG = {}


def init(config_file):
    conf = DictionaryConfigParser()
    conf.read(config_file)

    return conf.as_dict()


class DictionaryConfigParser(ConfigParser.ConfigParser):

    def as_dict(self):
        d = dict(self._sections)
        for k in d:
            d[k] = dict(self._defaults, **d[k])
            d[k].pop('__NAME__', None)
        return d
