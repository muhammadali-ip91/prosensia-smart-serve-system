"""Global Error Handlers"""

from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
from loguru import logger
from utils.helpers import get_current_timestamp


def add_error_handlers(app: FastAPI):
	"""Register global error handlers"""

	@app.exception_handler(HTTPException)
	async def http_exception_handler(request: Request, exc: HTTPException):
		"""Handle HTTP exceptions"""

		error_detail = exc.detail if isinstance(exc.detail, dict) else {
			"code": f"HTTP_{exc.status_code}",
			"message": str(exc.detail)
		}

		return JSONResponse(
			status_code=exc.status_code,
			content={
				"success": False,
				"error": error_detail,
				"timestamp": get_current_timestamp(),
				"path": str(request.url.path)
			}
		)

	@app.exception_handler(Exception)
	async def general_exception_handler(request: Request, exc: Exception):
		"""Handle unexpected exceptions"""

		logger.error(f"Unhandled exception: {exc} | Path: {request.url.path}")

		return JSONResponse(
			status_code=500,
			content={
				"success": False,
				"error": {
					"code": "SYS_004",
					"message": "Internal server error. Please try again later."
				},
				"timestamp": get_current_timestamp(),
				"path": str(request.url.path)
			}
		)

