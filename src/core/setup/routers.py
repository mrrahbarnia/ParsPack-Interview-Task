from fastapi import APIRouter

from src.core.config import ENVS

# from src.modules.url_shortener.entrypoint import url_router_v1

router = APIRouter(prefix=f"{ENVS.FASTAPI.ENDPOINT_PREFIX}")

# router.include_router(router=url_router_v1)
