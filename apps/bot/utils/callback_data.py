from enum import Enum
from typing import Optional

from aiogram.filters.callback_data import CallbackData


class MainMenuAction(str, Enum):
    ORDER = 'order'
    ACTIVE = 'active'
    SETTINGS = 'settings'
    CREATE_DETECTION = 'new_detection'


class MainMenuCallbackData(CallbackData, prefix='main_menu'):
    action: MainMenuAction


def cb_main_menu_callback_data(action):
    return MainMenuCallbackData(action=action.value).pack()


class BackToMainMenuAction(str, Enum):
    BACK = 'back'


class BackToMainMenuCallbackData(CallbackData, prefix='back_main_menu'):
    action: BackToMainMenuAction


def cb_back_to_main_menu_callback_data(action: BackToMainMenuAction):
    return BackToMainMenuCallbackData(action=action.value).pack()


class SelectLanguage(str, Enum):
    UZ = 'uz'
    RU = 'ru'
    EN = 'en'


class SelectLanguageCallbackData(CallbackData, prefix='select_language'):
    language: SelectLanguage


def cb_select_language_callback_data(lang):
    return SelectLanguageCallbackData(language=lang.value).pack()


class DetectionActiveMainMenuAction(str, Enum):
    ACTIVE = 'active'
    DEACTIVATED = 'deactivated'
    FILTER = 'filters'
    REPORT = 'report'
    DELETED = 'deleted'
    RUN_DETECTION = 'run_detection'


class ActiveMainMenuCallbackData(CallbackData, prefix='active_main_menu'):
    action: DetectionActiveMainMenuAction
    id: int


def select_active_menu_callback_data(action: DetectionActiveMainMenuAction, detection_id: int):
    return ActiveMainMenuCallbackData(action=action, id=detection_id).pack()


class CreateDetectionAction(str, Enum):
    ACTIVE = 'active'
    FILTER = 'filter'


class CreateDetectionCallbackData(CallbackData, prefix='create_detection'):
    action: CreateDetectionAction
    brand_id: Optional[int] = None
    model_id: Optional[int] = None


def create_detection_callback_data(action: CreateDetectionAction):
    return CreateDetectionCallbackData(action=action).pack()