""" Commons """
import os.path
import sys


def resolve_route(rute,relative = '.'): # Resolves the route of the file
    """resolve_route"""
    if hasattr(sys,'_MEIPASS'): # Checks if the file is running in a frozen environment
        return os.path.join(sys._MEIPASS,rute)
    return os.path.join(os.path.abspath(relative),rute)


ROUTE = lambda route: os.path.join(os.path.abspath("."), route)
