from pydantic import BaseModel, Field


class TranslationRequest(BaseModel):
    text: str = Field(..., description="Text to translate", min_length=1)
    source_lang: str = Field(default="en", description="Source language ISO code")
    target_lang: str = Field(default="hi", description="Target language ISO code")


class TranslationResponse(BaseModel):
    original_text: str
    translated_text: str
    source_lang: str
    target_lang: str
    cached: bool = False
    provider: str = "agrovisor-edge-dictionary"


class LanguageInfo(BaseModel):
    code: str
    name: str
    native_name: str


class LanguagesResponse(BaseModel):
    languages: list[LanguageInfo]
