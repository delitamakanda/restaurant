import logging
import time

from django.db import connection, reset_queries


def metric_middleware(get_response):
    def middleware(request):
        reset_queries()

        # get beginning stats
        start_queries = len(connection.queries)
        start_time = time.perf_counter()

        # process request
        response = get_response(request)

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

    return middleware
