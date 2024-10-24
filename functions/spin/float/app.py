from spin_sdk.http import IncomingHandler, Request, Response
from json import dumps
from math import sin, cos, sqrt


#POINTS = 100000
POINTS = 1000000

class Point(object):
    __slots__ = ('x', 'y', 'z')

    def __init__(self, i):
        self.x = x = sin(i)
        self.y = cos(i) * 3
        self.z = (x * x) / 2

    def __repr__(self):
        return "<Point: x=%s, y=%s, z=%s>" % (self.x, self.y, self.z)

    def normalize(self):
        x = self.x
        y = self.y
        z = self.z
        norm = sqrt(x * x + y * y + z * z)
        self.x /= norm
        self.y /= norm
        self.z /= norm

    def maximize(self, other):
        self.x = self.x if self.x > other.x else other.x
        self.y = self.y if self.y > other.y else other.y
        self.z = self.z if self.z > other.z else other.z
        return self


def maximize(points):
    next = points[0]
    for p in points[1:]:
        next = next.maximize(p)
    return next


def benchmark(n):
    points = [None] * n
    for i in range(n):
        points[i] = Point(i)
    for p in points:
        p.normalize()
    return maximize(points)


class IncomingHandler(IncomingHandler):
    def handle_request(self, request: Request) -> Response:
        point = benchmark(POINTS)
        result = {"x": point.x, "y": point.y,"z": point.z }

        return Response(
            200,
            {"content-type": "text/plain"},
            bytes(dumps(result), "utf-8")
        )
