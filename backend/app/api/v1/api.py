from fastapi import APIRouter
from app.api.v1.endpoints import (
    payments,
    caldav,
    auth,
    estimations,
    admin,
    invoices,
    packages,
    scheduling,
    task_sync,
    todo,
)

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(payments.router, prefix="/payments", tags=["payments"])
api_router.include_router(caldav.router, prefix="/caldav", tags=["caldav"])
api_router.include_router(estimations.router, prefix="/estimations", tags=["estimations"])
api_router.include_router(admin.router, prefix="/admin", tags=["admin"])
api_router.include_router(invoices.router, prefix="/invoices", tags=["invoices"])
api_router.include_router(packages.router, prefix="/packages", tags=["packages"])
api_router.include_router(task_sync.router, prefix="/task-sync", tags=["task-sync"])
api_router.include_router(scheduling.router, prefix="/scheduling", tags=["scheduling"])
api_router.include_router(todo.router, prefix="/todo", tags=["todo"], include_in_schema=True)
