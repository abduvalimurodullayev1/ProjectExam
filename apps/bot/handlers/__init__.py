from .create_detections import router as create_detections_router
from .commands import router as commands_router
from .registration import router as registration_router
from .settings import router as settings_router
from .active_detactions import router as active_detactions_router
def setup_handlers(dp):
    dp.include_router(commands_router)
    dp.include_router(registration_router)
    dp.include_router(settings_router)
    dp.include_router(active_detactions_router)
    dp.include_router(create_detections_router)
