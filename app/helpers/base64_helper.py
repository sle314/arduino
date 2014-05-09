# -*- coding: utf-8 -*-
def b64encode_quote(s):
    from urllib import quote
    from base64 import b64encode
    return b64encode(quote(s))

def unquote_b64decode(s):
    from urllib import unquote
    from base64 import b64decode
    return unquote(b64decode(s))