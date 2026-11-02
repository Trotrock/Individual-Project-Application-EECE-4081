import contextvars
import uuid
import json
import logging

# Thread-safe storage for the correlation identifier
request_trace_id = contextvars.ContextVar("trace_id", default="no_trace")

class TraceIDMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        token = request_trace_id.set(str(uuid.uuid4())[:10])
        try:
            response = self.get_response(request)
            return response
        finally:
            request_trace_id.reset(token)

class JSONFormatter(logging.Formatter):
    def format(self, record):
        log_data = {
            "timestamp": self.formatTime(record, self.datefmt),
            "level": record.levelname,
            "trace_id": request_trace_id.get(),
            "message": record.getMessage(),
            "logger": record.name
        }
        if hasattr(record, "extra_data"):
            log_data.update(record.extra_data)
            
        return json.dumps(log_data)
