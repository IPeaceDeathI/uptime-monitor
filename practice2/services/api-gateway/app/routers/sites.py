from fastapi import APIRouter, Depends, HTTPException, status
from prometheus_client import Counter
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_session
from app.models import CheckResult, Site
from app.schemas import CheckResultRead, SiteCreate, SiteRead

router = APIRouter(prefix="/sites", tags=["sites"])

SITES_REGISTERED_TOTAL = Counter(
    "sites_registered_total",
    "Business counter: new monitoring targets registered via API",
)


@router.post("", response_model=SiteRead, status_code=status.HTTP_201_CREATED)
async def create_site(payload: SiteCreate, session: AsyncSession = Depends(get_session)) -> Site:
    site = Site(url=str(payload.url), name=payload.name, interval_sec=payload.interval_sec)
    session.add(site)
    try:
        await session.commit()
    except IntegrityError as exc:
        await session.rollback()
        raise HTTPException(status_code=409, detail="URL already exists") from exc
    await session.refresh(site)
    SITES_REGISTERED_TOTAL.inc()
    return site


@router.get("", response_model=list[SiteRead])
async def list_sites(session: AsyncSession = Depends(get_session)) -> list[Site]:
    res = await session.execute(select(Site).order_by(Site.id))
    return list(res.scalars().all())


@router.get("/{site_id}", response_model=SiteRead)
async def get_site(site_id: int, session: AsyncSession = Depends(get_session)) -> Site:
    site = await session.get(Site, site_id)
    if not site:
        raise HTTPException(status_code=404, detail="Site not found")
    return site


@router.get("/{site_id}/checks", response_model=list[CheckResultRead])
async def list_checks(
    site_id: int, limit: int = 50, session: AsyncSession = Depends(get_session)
) -> list[CheckResult]:
    site = await session.get(Site, site_id)
    if not site:
        raise HTTPException(status_code=404, detail="Site not found")
    q = (
        select(CheckResult)
        .where(CheckResult.site_id == site_id)
        .order_by(CheckResult.checked_at.desc())
        .limit(min(limit, 500))
    )
    res = await session.execute(q)
    return list(res.scalars().all())


@router.delete("/{site_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_site(site_id: int, session: AsyncSession = Depends(get_session)) -> None:
    site = await session.get(Site, site_id)
    if not site:
        raise HTTPException(status_code=404, detail="Site not found")
    await session.delete(site)
    await session.commit()
