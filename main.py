from fastapi import FastAPI, Request
from auth_routes import auth_router
from order_routes import order_router
from fastapi_jwt_auth import AuthJWT
from pydantic import BaseSettings
from config import Settings
from fastapi.openapi.utils import get_openapi
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles

# Create the FastAPI app
app = FastAPI()

# Set up Jinja2 templates
templates = Jinja2Templates(directory="templates")

# Mount static files for custom styling
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get('/')
async def read_root(request: Request):
    # Render a basic landing page
    return templates.TemplateResponse("index.html", {"request": request, "title": "Pizza Delivery API"})

# JWT Configurations using Settings from config.py
@AuthJWT.load_config
def get_config():
    return Settings()

# Include the routers
app.include_router(auth_router)
app.include_router(order_router)

# Define a custom OpenAPI schema with BearerAuth
def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title="🍕 Pizza Delivery API 🍕",
        version="1.0.0",
        description="An API for a Pizza Delivery Service with JWT Authentication.",
        routes=app.routes,
    )
    # Define security scheme globally
    openapi_schema["components"]["securitySchemes"] = {
        "BearerAuth": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT"
        }
    }
    # Apply the security scheme to all endpoints
    openapi_schema["security"] = [{"BearerAuth": []}]
    app.openapi_schema = openapi_schema
    return app.openapi_schema

# Assign the custom OpenAPI schema
app.openapi = custom_openapi
