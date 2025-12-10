from typing import Union
from http import HTTPStatus
from fastapi import Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
import httpx
import asyncio
import logging

logger = logging.getLogger(__name__)


class HttpxExceptionMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        try:
            response = await call_next(request)
            return response

        except httpx.TimeoutException as exc:
            logger.error(f"Request timeout: {exc}", exc_info=True)
            return JSONResponse(
                status_code=HTTPStatus.GATEWAY_TIMEOUT,
                content={
                    "error": "Gateway Timeout",
                    "message": "The upstream service took too long to respond",
                    "detail": str(exc),
                    "timeout_type": exc.__class__.__name__
                }
            )

        except httpx.ConnectTimeout as exc:
            logger.error(f"Connection timeout: {exc}", exc_info=True)
            return JSONResponse(
                status_code=HTTPStatus.REQUEST_TIMEOUT,
                content={
                    "error": "Connection Timeout",
                    "message": "Failed to establish connection within the timeout period",
                    "detail": str(exc)
                }
            )

        except httpx.ReadTimeout as exc:
            logger.error(f"Read timeout: {exc}", exc_info=True)
            return JSONResponse(
                status_code=HTTPStatus.REQUEST_TIMEOUT,
                content={
                    "error": "Read Timeout",
                    "message": "The server did not send any data in the allotted time",
                    "detail": str(exc)
                }
            )

        except httpx.ConnectError as exc:
            logger.error(f"Connection error: {exc}", exc_info=True)
            return JSONResponse(
                status_code=HTTPStatus.BAD_GATEWAY,
                content={
                    "error": "Bad Gateway",
                    "message": "Unable to connect to the upstream service",
                    "detail": str(exc),
                    "upstream_service": self._extract_host_from_exception(exc)
                }
            )

        except httpx.NetworkError as exc:
            logger.error(f"Network error: {exc}", exc_info=True)
            return JSONResponse(
                status_code=HTTPStatus.SERVICE_UNAVAILABLE,
                content={
                    "error": "Service Unavailable",
                    "message": "Network error occurred while connecting to upstream service",
                    "detail": str(exc)
                }
            )

        except httpx.ProxyError as exc:
            logger.error(f"Proxy error: {exc}", exc_info=True)
            return JSONResponse(
                status_code=HTTPStatus.BAD_GATEWAY,
                content={
                    "error": "Proxy Error",
                    "message": "Proxy server error occurred",
                    "detail": str(exc)
                }
            )

        except httpx.HTTPStatusError as exc:
            logger.error(f"HTTP status error: {exc}", exc_info=True)
            # Пробрасываем статус код от upstream сервиса
            status_code = exc.response.status_code
            try:
                error_detail = exc.response.json()
            except:
                error_detail = exc.response.text

            return JSONResponse(
                status_code=status_code,
                content={
                    "error": HTTPStatus(status_code).phrase,
                    "message": f"Upstream service returned error: {status_code}",
                    "detail": error_detail,
                    "upstream_response": {
                        "status_code": status_code,
                        "headers": dict(exc.response.headers)
                    }
                }
            )

        except httpx.RequestError as exc:
            logger.error(f"Request error: {exc}", exc_info=True)
            return JSONResponse(
                status_code=HTTPStatus.BAD_REQUEST,
                content={
                    "error": "Request Error",
                    "message": "Failed to prepare or send the HTTP request",
                    "detail": str(exc),
                    "request_method": exc.request.method if hasattr(exc, 'request') else None,
                    "request_url": str(exc.request.url) if hasattr(exc, 'request') else None
                }
            )

        except httpx.DecodingError as exc:
            logger.error(f"Decoding error: {exc}", exc_info=True)
            return JSONResponse(
                status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
                content={
                    "error": "Decoding Error",
                    "message": "Failed to decode response from upstream service",
                    "detail": str(exc),
                    "encoding": getattr(exc, 'encoding', None)
                }
            )

        except httpx.TooManyRedirects as exc:
            logger.error(f"Too many redirects: {exc}", exc_info=True)
            return JSONResponse(
                status_code=HTTPStatus.LOOP_DETECTED,
                content={
                    "error": "Too Many Redirects",
                    "message": "Maximum redirects exceeded",
                    "detail": str(exc),
                    "max_redirects": getattr(exc, 'max_redirects', None)
                }
            )

        except httpx.UnsupportedProtocol as exc:
            logger.error(f"Unsupported protocol: {exc}", exc_info=True)
            return JSONResponse(
                status_code=HTTPStatus.BAD_REQUEST,
                content={
                    "error": "Unsupported Protocol",
                    "message": "The requested protocol is not supported",
                    "detail": str(exc),
                    "protocol": getattr(exc, 'protocol', None)
                }
            )

        except httpx.ProtocolError as exc:
            logger.error(f"Protocol error: {exc}", exc_info=True)
            return JSONResponse(
                status_code=HTTPStatus.BAD_REQUEST,
                content={
                    "error": "Protocol Error",
                    "message": "HTTP protocol violation",
                    "detail": str(exc)
                }
            )

        except httpx.LocalProtocolError as exc:
            logger.error(f"Local protocol error: {exc}", exc_info=True)
            return JSONResponse(
                status_code=HTTPStatus.BAD_REQUEST,
                content={
                    "error": "Local Protocol Error",
                    "message": "Local HTTP protocol error",
                    "detail": str(exc)
                }
            )

        except httpx.RemoteProtocolError as exc:
            logger.error(f"Remote protocol error: {exc}", exc_info=True)
            return JSONResponse(
                status_code=HTTPStatus.BAD_GATEWAY,
                content={
                    "error": "Remote Protocol Error",
                    "message": "Upstream service violated HTTP protocol",
                    "detail": str(exc)
                }
            )

        except asyncio.TimeoutError as exc:
            logger.error(f"Async timeout: {exc}", exc_info=True)
            return JSONResponse(
                status_code=HTTPStatus.GATEWAY_TIMEOUT,
                content={
                    "error": "Async Timeout",
                    "message": "Async operation timed out",
                    "detail": str(exc)
                }
            )
        except Exception as exc:
            raise exc

    def _extract_host_from_exception(self, exc: httpx.ConnectError) -> Union[str, None]:
        if hasattr(exc, 'request') and hasattr(exc.request, 'url'):
            return str(exc.request.url.host)
        return None
