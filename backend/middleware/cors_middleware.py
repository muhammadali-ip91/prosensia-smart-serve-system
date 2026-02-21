"""CORS Configuration"""

from config import settings


def get_cors_config():
	"""Get CORS configuration dictionary"""
	return {
		"allow_origins": settings.cors_origins_list,
		"allow_credentials": True,
		"allow_methods": ["*"],
		"allow_headers": ["*"],
	}

