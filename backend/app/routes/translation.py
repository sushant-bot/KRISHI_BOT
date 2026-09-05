from fastapi import APIRouter, Depends

from app.schemas.translation import (
    LanguageInfo,
    LanguagesResponse,
    TranslationRequest,
    TranslationResponse,
)
from app.services.translation import TranslationService, get_translation_service

router = APIRouter(prefix="/translate", tags=["translation"])


@router.get("/languages", response_model=LanguagesResponse)
def list_supported_languages(
    service: TranslationService = Depends(get_translation_service),
) -> LanguagesResponse:
    languages = service.get_supported_languages()
    return LanguagesResponse(
        languages=[
            LanguageInfo(code=l["code"], name=l["name"], native_name=l["native_name"])
            for l in languages
        ]
    )


@router.post("", response_model=TranslationResponse)
def translate_text(
    payload: TranslationRequest,
    service: TranslationService = Depends(get_translation_service),
) -> TranslationResponse:
    result = service.translate_text(
        text=payload.text,
        source_lang=payload.source_lang,
        target_lang=payload.target_lang,
    )
    return TranslationResponse(**result)


class BatchTranslationRequest:
    pass
