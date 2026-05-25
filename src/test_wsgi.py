import urllib.parse

def application(environ, start_response):
    start_response('200 OK', [('Content-type', 'text/plain; charset=utf-8')])

    get_params = urllib.parse.parse_qs(environ.get('QUERY_STRING', ''))
    post_params = {}

    if environ.get('REQUEST_METHOD') == 'POST':
        content_length = environ.get('CONTENT_LENGTH', '')
        content_length = int(content_length) if content_length else 0

        if content_length > 0:
            body = environ['wsgi.input'].read(content_length).decode('utf-8')
            post_params = urllib.parse.parse_qs(body)

    out = [f"Method: {environ.get('REQUEST_METHOD', 'UNKNOWN')}"]

    out.append("\nGET:")
    if get_params:
        for k, v in get_params.items():
            out.append(f"  {k} = {', '.join(v)}")
    else:
        out.append("  None")

    out.append("\nPOST:")
    if post_params:
        for k, v in post_params.items():
            out.append(f"  {k} = {', '.join(v)}")
    else:
        out.append("  None")

    return ['\n'.join(out).encode('utf-8')]

