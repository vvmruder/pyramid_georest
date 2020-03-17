# -*- coding: utf-8 -*-


def camel_casify(string):
    return ''.join(x for x in string.title() if not x.isspace())
