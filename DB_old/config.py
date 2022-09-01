#!/usr/bin/python
from configparser import ConfigParser


def config(filename='database.ini', section='postgresql'):
    # criando o parser
    parser = ConfigParser()
    # lendo o config file
    parser.read(filename)

    # pega section, default to postgresql
    db = {}
    if parser.has_section(section):
        params = parser.items(section)
        for param in params:
            db[param[0]] = param[1]
    else:
        raise Exception('Section {0} não encontrada no {1} arquivo de configuração'.format(section, filename))

    return db