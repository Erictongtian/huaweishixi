from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

from app.core.config import settings
from app.core.exceptions import (
    BusinessException,
    ConflictException,
    NotFoundException,
    PermissionException,
    ValidationException,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield


app = FastAPI(
    title="二手设备销售管理系统",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(BusinessException)
async def business_exception_handler(request: Request, exc: BusinessException):
    return JSONResponse(
        status_code=exc.code,
        content={"code": exc.code, "message": exc.message, "errors": []},
    )


@app.exception_handler(PermissionException)
async def permission_exception_handler(request: Request, exc: PermissionException):
    return JSONResponse(
        status_code=403,
        content={"code": 403, "message": exc.message, "errors": []},
    )


@app.exception_handler(NotFoundException)
async def not_found_exception_handler(request: Request, exc: NotFoundException):
    return JSONResponse(
        status_code=404,
        content={"code": 404, "message": exc.message, "errors": []},
    )


@app.exception_handler(ConflictException)
async def conflict_exception_handler(request: Request, exc: ConflictException):
    return JSONResponse(
        status_code=409,
        content={"code": 409, "message": exc.message, "errors": []},
    )


@app.exception_handler(ValidationException)
async def validation_exception_handler(request: Request, exc: ValidationException):
    return JSONResponse(
        status_code=422,
        content={"code": 422, "message": exc.message, "errors": exc.errors},
    )


@app.exception_handler(RequestValidationError)
async def request_validation_handler(request: Request, exc: RequestValidationError):
    errors = []
    for err in exc.errors():
        field = ".".join(str(loc) for loc in err.get("loc", []))
        errors.append({"field": field, "message": err.get("msg", "")})
    return JSONResponse(
        status_code=422,
        content={"code": 422, "message": "请求参数验证失败", "errors": errors},
    )


from app.api.v1 import auth, devices, orders, reviews, categories, users, upload, admin  # noqa: E402

app.include_router(auth.router, prefix="/api/v1/auth", tags=["认证"])
app.include_router(devices.router, prefix="/api/v1/devices", tags=["设备"])
app.include_router(orders.router, prefix="/api/v1/orders", tags=["订单"])
app.include_router(reviews.router, prefix="/api/v1/reviews", tags=["评价"])
app.include_router(categories.router, prefix="/api/v1/categories", tags=["分类"])
app.include_router(users.router, prefix="/api/v1/users", tags=["用户"])
app.include_router(upload.router, prefix="/api/v1", tags=["文件上传"])
app.include_router(admin.router, prefix="/api/v1/admin", tags=["管理员"])

Path(settings.UPLOAD_DIR).mkdir(parents=True, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=settings.UPLOAD_DIR), name="uploads")
