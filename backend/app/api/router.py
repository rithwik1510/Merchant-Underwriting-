from fastapi import APIRouter

from app.api.routes import acceptance, benchmarks, communications, health, mandates, merchants, policies, seed, underwriting


api_router = APIRouter()
api_router.include_router(health.router, tags=["health"])
api_router.include_router(seed.router, prefix="/seed", tags=["seed"])
api_router.include_router(merchants.router, prefix="/merchants", tags=["merchants"])
api_router.include_router(benchmarks.router, prefix="/benchmarks", tags=["benchmarks"])
api_router.include_router(policies.router, prefix="/policies", tags=["policies"])
api_router.include_router(underwriting.router, prefix="/underwriting", tags=["underwriting"])
api_router.include_router(communications.router, prefix="/underwriting", tags=["communications"])
api_router.include_router(acceptance.router, tags=["acceptance"])
api_router.include_router(mandates.router, tags=["mandates"])
