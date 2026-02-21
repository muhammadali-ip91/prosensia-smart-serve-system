"""Request/Response Logging Middleware"""

import time
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from loguru import logger
from config import settings


class LoggingMiddleware(BaseHTTPMiddleware):
	"""Log every request and response"""

	async def dispatch(self, request: Request, call_next):
		# Start timer
		start_time = time.time()

		# Process request
		response = await call_next(request)

		# Calculate duration
		duration_ms = round((time.time() - start_time) * 1000, 2)

		# Log
		if settings.ENABLE_REQUEST_LOGGING:
			logger.info(
				f"{request.method} {request.url.path} "
				f"| Status: {response.status_code} "
				f"| Time: {duration_ms}ms"
			)

		# Add custom header
		response.headers["X-Response-Time"] = f"{duration_ms}ms"

		return response

