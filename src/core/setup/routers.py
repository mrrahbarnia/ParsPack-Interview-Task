from fastapi import APIRouter

from src.core.config import ENVS

from src.modules.auth.entrypoint import auth_router_v1

router = APIRouter(prefix=f"{ENVS.FASTAPI.ENDPOINT_PREFIX}")

router.include_router(router=auth_router_v1)
