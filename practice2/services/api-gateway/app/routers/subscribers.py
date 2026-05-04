from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_session
from app.models import Site, Subscriber
from app.schemas import SubscriberCreate, SubscriberRead

router = APIRouter(prefix="/subscribers", tags=["subscribers"])


@router.post("", response_model=SubscriberRead, status_code=status.HTTP_201_CREATED)
async def create_subscriber(
    payload: SubscriberCreate, session: AsyncSession = Depends(get_session)
) -> Subscriber:
    if payload.site_id is not None:
        site = await session.get(Site, payload.site_id)
        if not site:
            raise HTTPException(status_code=404, detail="Site not found")
    sub = Subscriber(telegram_chat_id=payload.telegram_chat_id, site_id=payload.site_id)
    session.add(sub)
    await session.commit()
    await session.refresh(sub)
    return sub


@router.get("", response_model=list[SubscriberRead])
async def list_subscribers(session: AsyncSession = Depends(get_session)) -> list[Subscriber]:
    res = await session.execute(select(Subscriber).order_by(Subscriber.id))
    return list(res.scalars().all())
