
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

app.include_router(auth_router)
app.include_router(user_router)
app.include_router(content_router)
app.include_router(chat_router)
app.include_router(notifications_router)
app.include_router(admin_router)

# Example admin-only route
@app.get("/")
def root():
    return {"message": "Welcome to the AI Content Platform API"}

@app.get("/health")
async def health():
    return {"status": "healthy"}
