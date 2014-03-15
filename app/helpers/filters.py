from jinja2 import evalcontextfilter, Markup, escape
from app.web import app


@app.template_filter()
@evalcontextfilter
def b64decode(ctx, value):
    from app.helpers.base64_helper import unquote_b64decode
    return unquote_b64decode(value)

@app.template_filter()
@evalcontextfilter
def b64encode(ctx, value):
    from app.helpers.base64_helper import b64encode_quote
    return b64encode_quote(value)