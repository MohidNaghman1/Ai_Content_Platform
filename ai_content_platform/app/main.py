
from fastapi import FastAPI, Depends
from ai_content_platform.app.modules.auth.routes import auth_router
from ai_content_platform.app.shared.dependencies import require_role
from ai_content_platform.app.modules.users.routes import user_router
from ai_content_platform.app.modules.content.routes import content_router
from ai_content_platform.app.modules.chat.routes import chat_router
from ai_content_platform.app.modules.admin.routes import admin_router
from ai_content_platform.app.modules.notifications.routes import router as notifications_router
from ai_content_platform.app.shared.middleware import LoggingMiddleware


app = FastAPI()
app.add_middleware(LoggingMiddleware)

app.include_router(auth_router, prefix="/auth", tags=["auth"])
app.include_router(user_router, prefix="/users", tags=["users"])
app.include_router(content_router, prefix="/content", tags=["content"])
app.include_router(chat_router, prefix="/chat", tags=["chat"])
app.include_router(notifications_router, prefix="/api/notifications", tags=["notifications"])
app.include_router(admin_router, prefix="/admin", tags=["admin"])

# Debug: print all registered routes
print("ROUTES:", [route.path for route in app.routes])

# Example admin-only route
@app.get("/admin")
def read_admin_data(current_user: dict = Depends(require_role("admin"))):
    return {"admin_data": "Secret admin stuff!", "user": current_user}
