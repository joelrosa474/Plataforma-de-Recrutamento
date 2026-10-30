
import logging
import os
from typing import Iterable

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException
from dotenv import load_dotenv

load_dotenv()

from src.adapters.api import vagas_router, candidaturas_router, auth_router, admin_router, notificacoes_router, talentos_router
from src.infrastructure.database.config import engine, Base, migrate_sqlite_schema, check_db_health
from src.infrastructure.database import models  # Importa os modelos para registar no Base

logger = logging.getLogger("rh_api")
logger.setLevel(logging.INFO)
if not logger.handlers:
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(name)s %(message)s"))
    logger.addHandler(handler)


def get_allowed_origins() -> list[str]:
    raw = os.getenv("CORS_ORIGINS", "http://localhost:3000,http://127.0.0.1:3000")
    return [origin.strip() for origin in raw.split(",") if origin.strip()]


def get_csrf_trusted_origins() -> set[str]:
    """Origens que podem emitir pedidos com o cookie de sessão.

    API_ORIGIN é configurável para manter o Swagger funcional sem confiar no
    cabeçalho Host recebido, que pode ser forjado por um cliente externo.
    """
    raw_api_origins = os.getenv("API_ORIGIN", "http://localhost:8000,http://127.0.0.1:8000")
    api_origins = {origin.strip() for origin in raw_api_origins.split(",") if origin.strip()}
    return set(get_allowed_origins()) | api_origins


SAFE_METHODS = {"GET", "HEAD", "OPTIONS"}


# Cria as tabelas SQLite se não existirem
Base.metadata.create_all(bind=engine)
migrate_sqlite_schema()

app = FastAPI(
    title="Plataforma de Recrutamento RH API",
    description="Backend para a plataforma de recrutamento usando FastAPI e DDD",
    version="1.0.0",
)


@app.middleware("http")
async def request_logging_and_headers(request: Request, call_next):
    request_id = request.headers.get("x-request-id") or os.urandom(8).hex()
    request.state.request_id = request_id

    # As operações autenticadas usam cookies. Rejeitar uma origem explícita que
    # não esteja autorizada reduz o risco de CSRF, mantendo compatibilidade com
    # clientes não-browser (que não enviam o cabeçalho Origin).
    origin = request.headers.get("origin")
    allowed_origins = get_csrf_trusted_origins()
    if request.method not in SAFE_METHODS and origin and origin not in allowed_origins:
        response = JSONResponse(
            status_code=403,
            content=build_error_payload(
                "A origem deste pedido não está autorizada.",
                "csrf_origin_forbidden",
                403,
                request_id=request_id,
            ),
        )
        response.headers["X-Request-Id"] = request_id
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Permissions-Policy"] = "camera=(), microphone=(), geolocation=()"
        return response

    response = await call_next(request)
    response.headers["X-Request-Id"] = request_id
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    response.headers["Permissions-Policy"] = "camera=(), microphone=(), geolocation=()"
    logger.info(
        "http_request",
        extra={
            "method": request.method,
            "path": request.url.path,
            "status_code": response.status_code,
            "request_id": request_id,
        },
    )
    return response


def build_error_payload(
    detail: str,
    code: str,
    status_code: int,
    request_id: str | None = None,
    fields: list | None = None,
):
    payload = {
        "detail": detail,
        "error": {
            "code": code,
            "message": detail,
            "status": status_code,
            "request_id": request_id,
        },
    }
    if fields is not None:
        payload["error"]["fields"] = fields
    return payload


@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    status_code = exc.status_code
    custom_error = exc.detail if isinstance(exc.detail, dict) else {}
    detail = custom_error.get("message") if custom_error else exc.detail
    detail = detail if isinstance(detail, str) else "Ocorreu um erro na operação."

    if custom_error.get("code"):
        code = custom_error["code"]
    elif status_code == 400:
        code = "bad_request"
    elif status_code == 401:
        code = "invalid_credentials"
    elif status_code == 403:
        code = "forbidden"
    elif status_code == 404:
        code = "not_found"
    elif status_code == 409:
        code = "conflict"
    elif status_code == 422:
        code = "validation_error"
    elif status_code == 429:
        code = "rate_limited"
    else:
        code = "http_error"

    logger.warning(
        "http_exception",
        extra={
            "path": request.url.path,
            "status_code": status_code,
            "detail": detail,
            "request_id": getattr(request.state, "request_id", None),
        },
    )
    return JSONResponse(
        status_code=status_code,
        content=build_error_payload(
            detail,
            code,
            status_code,
            request_id=getattr(request.state, "request_id", None),
            fields=custom_error.get("fields"),
        ),
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    logger.warning(
        "validation_error",
        extra={
            "path": request.url.path,
            "request_id": getattr(request.state, "request_id", None),
            "errors": exc.errors(),
        },
    )
    return JSONResponse(
        status_code=422,
        content=build_error_payload(
            "Os dados enviados são inválidos.",
            "validation_error",
            422,
            request_id=getattr(request.state, "request_id", None),
            fields=exc.errors(),
        ),
    )


@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    logger.exception(
        "unhandled_exception",
        extra={
            "path": request.url.path,
            "request_id": getattr(request.state, "request_id", None),
        },
    )
    return JSONResponse(
        status_code=500,
        content=build_error_payload(
            "Erro interno do servidor.",
            "internal_server_error",
            500,
            request_id=getattr(request.state, "request_id", None),
        ),
    )


app.add_middleware(
    CORSMiddleware,
    allow_origins=get_allowed_origins(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Inclui os roteadores (Adapters Primários)
app.include_router(auth_router.router)
app.include_router(vagas_router.router)
app.include_router(candidaturas_router.router)
app.include_router(admin_router.router)
app.include_router(notificacoes_router.router)
app.include_router(talentos_router.router)


@app.get("/")
@app.get("/health")
def health_check():
    db_ok = check_db_health()
    return {
        "status": "ok" if db_ok else "degraded",
        "database": "connected" if db_ok else "error",
        "message": "API de Recrutamento rodando perfeitamente!" if db_ok else "API de Recrutamento com degradação na base de dados.",
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("src.main:app", host="0.0.0.0", port=8000, reload=True)
