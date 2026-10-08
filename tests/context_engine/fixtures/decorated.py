import functools


def cache_result(fn):
    return functools.lru_cache(maxsize=None)(fn)


@cache_result
def slow_square(n):
    return n * n


class Shape:
    """A shape."""

    def area(self):
        return 0
