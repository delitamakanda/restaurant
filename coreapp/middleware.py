from django.http import HttpResponseForbidden
from django.core.cache import cache
import logging
import time

from django.db import connection, reset_queries


class MetricMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def middleware(self, request):
        reset_queries()

        # get beginning stats
        start_queries = len(connection.queries)
        start_time = time.perf_counter()

        # process request
        response = self.get_response(request)

        # get end stats
        end_queries = len(connection.queries)
        end_time = time.perf_counter()

        # calculate stats
        total_time = end_time - start_time
        num_queries = end_queries - start_queries

        # log stats
        logger = logging.getLogger("debug")
        logger.debug(f"Request: {request.method} {request.path}")
        logger.debug(f"Queries: {num_queries}")
        logging.debug(f"Total times: {total_time: .2f} seconds")
        return response

    def __call__(self, request):
        return self.middleware(request)


class DDosMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        self.time_window = 60  # seconds
        self.requests_limit = 1000  # requests per time window

    def process_request(self, request):
        ip_address = request.META.get("REMOTE_ADDR")
        cache_key = f"ddos_requests_{ip_address}"

        current_requests = cache.get(cache_key, 0)
        if current_requests >= self.requests_limit:
            return HttpResponseForbidden("Too many requests, please try again later.")

        cache.set(cache_key, current_requests + 1, self.time_window)
        return None

    def __call__(self, request):
        return self.process_request(request) or self.get_response(request)
