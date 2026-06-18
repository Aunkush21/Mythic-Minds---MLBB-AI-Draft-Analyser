"""
Domain-specific exceptions, mapped to proper HTTP status codes via
exception handlers registered in main.py — keeps services/routers free
of repeated try/except HTTPException boilerplate.
"""
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse


class AppError(Exception):
    status_code: int = 500
    error_code: str = "internal_error"

    def __init__(self, detail: str):
        self.detail = detail
        super().__init__(detail)


class HeroNotFoundError(AppError):
    status_code = 404
    error_code = "hero_not_found"


class PatchNotFoundError(AppError):
    status_code = 404
    error_code = "patch_not_found"


class InvalidDraftError(AppError):
    status_code = 400
    error_code = "invalid_draft"


class ModelUnavailableError(AppError):
    status_code = 503
    error_code = "model_unavailable"


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(AppError)
    async def handle_app_error(request: Request, exc: AppError) -> JSONResponse:
        return JSONResponse(
            status_code=exc.status_code,
            content={"error_code": exc.error_code, "detail": exc.detail},
        )

    @app.exception_handler(Exception)
    async def handle_unexpected_error(request: Request, exc: Exception) -> JSONResponse:
        return JSONResponse(
            status_code=500,
            content={"error_code": "internal_error", "detail": "An unexpected error occurred."},
        )
