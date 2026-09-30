from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.topic import Topic


class SQLAlchemyTopicRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_by_id(self, topic_id: UUID) -> Topic | None:
        stmt = select(Topic).where(Topic.id == topic_id)
        result = await self._session.execute(stmt)

        return result.scalar_one_or_none()

    async def get_roots(self) -> list[Topic]:
        stmt = select(Topic).where(Topic.parent_id.is_(None))
        result = await self._session.execute(stmt)

        return list(result.scalars().all())

    async def get_children(self, parent_id: UUID) -> list[Topic]:
        stmt = select(Topic).where(Topic.parent_id == parent_id)
        result = await self._session.execute(stmt)

        return list(result.scalars().all())
