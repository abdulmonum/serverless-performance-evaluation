from spin_sdk.http import IncomingHandler, Request, Response
from time import time
from chameleon import PageTemplate
from urllib.parse import urlparse, parse_qs
import six


BIGTABLE_ZPT = """\
<table xmlns="http://www.w3.org/1999/xhtml"
xmlns:tal="http://xml.zope.org/namespaces/tal">
<tr tal:repeat="row python: options['table']">
<td tal:repeat="c python: row.values()">
<span tal:define="d python: c + 1"
tal:attributes="class python: 'column-' + %s(d)"
tal:content="python: d" />
</td>
</tr>
</table>"""% six.text_type.__name__ 



class IncomingHandler(IncomingHandler):
    def handle_request(self, request: Request) -> Response:
        qs = urlparse(request.uri).query
        args = parse_qs(qs)
        num_of_rows = int(args['num_of_rows'][0])
        num_of_cols = int(args['num_of_cols'][0])

        tmpl = PageTemplate(BIGTABLE_ZPT)

        data = {}
        for i in range(num_of_cols):
            data[str(i)] = i

        table = [data for x in range(num_of_rows)]
        options = {'table': table}

        data = tmpl.render(options=options)

        return Response(
            200,
            {"content-type": "text/plain"},
            bytes(data, "utf-8")
        )
