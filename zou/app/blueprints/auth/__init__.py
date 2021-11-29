from flask import Blueprint
from zou.app.utils.api import configure_api_from_blueprint

from .resources import (
    LoginResource,
    LogoutResource,
    AuthenticatedResource,
    ChangePasswordResource,
    RegistrationResource,
    RefreshTokenResource,
    ResetPasswordResource,
    Sso2LoginResource, RegisterTokensResource
)

routes = [
    ("/auth/login", LoginResource),
    ("/auth/sso2/login",Sso2LoginResource),
    ("/auth/register-tokens",RegisterTokensResource),
    ("/auth/logout", LogoutResource),
    ("/auth/authenticated", AuthenticatedResource),
    ("/auth/register", RegistrationResource),
    ("/auth/change-password", ChangePasswordResource),
    ("/auth/reset-password", ResetPasswordResource),
    ("/auth/refresh-token", RefreshTokenResource),
]

blueprint = Blueprint("auth", "auth")
api = configure_api_from_blueprint(blueprint, routes)
