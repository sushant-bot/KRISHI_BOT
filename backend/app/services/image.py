from datetime import UTC, datetime

from sqlalchemy.orm import Session

from app.models import AIResult, CropImage
from app.repositories import image as image_repository
from app.schemas.image import AIResultCreate, CropImageCreate
from app.services.farm import ConflictError, NotFoundError, get_farm, get_zone


def create_image(session: Session, payload: CropImageCreate) -> CropImage:
    get_farm(session, payload.farm_id)
    zone = get_zone(session, payload.zone_id)
    if zone.farm_id != payload.farm_id:
        raise ConflictError("The zone does not belong to the supplied farm.")
    return image_repository.create_image(
        session,
        CropImage(
            farm_id=payload.farm_id,
            zone_id=payload.zone_id,
            image_path=payload.image_path,
            timestamp=payload.timestamp or datetime.now(UTC),
        ),
    )


def get_image(session: Session, image_id: int) -> CropImage:
    image = image_repository.get_image(session, image_id)
    if image is None:
        raise NotFoundError("Crop image was not found.")
    return image


def list_images(session: Session, zone_id: int, limit: int) -> list[CropImage]:
    get_zone(session, zone_id)
    return image_repository.list_images(session, zone_id, limit)


def create_ai_result(session: Session, payload: AIResultCreate) -> AIResult:
    image = get_image(session, payload.image_id)
    return image_repository.create_ai_result(
        session,
        AIResult(
            image_id=image.id,
            zone_id=image.zone_id,
            crop_health=payload.crop_health,
            disease=payload.disease,
            confidence=payload.confidence,
            growth_stage=payload.growth_stage,
            provider=payload.provider,
        ),
    )


def list_ai_results(session: Session, zone_id: int, limit: int) -> list[AIResult]:
    get_zone(session, zone_id)
    return image_repository.list_ai_results(session, zone_id, limit)