from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import AIResult, CropImage


def create_image(session: Session, image: CropImage) -> CropImage:
    session.add(image)
    session.commit()
    session.refresh(image)
    return image


def get_image(session: Session, image_id: int) -> CropImage | None:
    return session.get(CropImage, image_id)


def list_images(session: Session, zone_id: int, limit: int) -> list[CropImage]:
    statement = (
        select(CropImage)
        .where(CropImage.zone_id == zone_id)
        .order_by(CropImage.timestamp.desc(), CropImage.id.desc())
        .limit(limit)
    )
    return list(session.scalars(statement))


def create_ai_result(session: Session, result: AIResult) -> AIResult:
    session.add(result)
    session.commit()
    session.refresh(result)
    return result


def list_ai_results(session: Session, zone_id: int, limit: int) -> list[AIResult]:
    statement = (
        select(AIResult)
        .where(AIResult.zone_id == zone_id)
        .order_by(AIResult.created_at.desc(), AIResult.id.desc())
        .limit(limit)
    )
    return list(session.scalars(statement))