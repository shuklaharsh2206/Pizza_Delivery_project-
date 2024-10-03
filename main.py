from fastapi import FastAPI
from auth_routes import auth_router
from order_routes import order_router
from fastapi_jwt_auth import AuthJWT
from pydantic import BaseSettings
from config import Settings
from fastapi.openapi.models import SecurityScheme  # Import SecurityScheme for OpenAPI
from fastapi.openapi.utils import get_openapi

# Create the FastAPI app
app = FastAPI()
@app.get('/')
async def hello():
    return {'Message':'Hello World'}

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
        title="Pizza Delivery API",
        version="1.0.0",
        description="An API for a Pizza Delivery Service",
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
