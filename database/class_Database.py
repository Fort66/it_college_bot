from unittest import result
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select, delete, update, insert, text
from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession
from datetime import datetime

from .models import Base, Disciplines, TypeExam, Teachers, Groups, Students, Quests, Answers

from icecream import ic

from sqlalchemy.engine import Engine
from sqlalchemy import event


class Database:
    def __init__(self):
        self.engine = create_async_engine('sqlite+aiosqlite:///it_college.db')
        self.Session = async_sessionmaker(self.engine, class_=AsyncSession, expire_on_commit=False)

    async def create_tables(self):
        async with self.engine.begin() as connect:
            await connect.run_sync(Base.metadata.create_all)

    async def get_table(self, table_name):
        async with self.Session() as session:
            result = await session.execute(select(table_name))
            return result.scalars().all()

    async def get_record(self, table_name, field_name, **kwargs):
        async with self.Session() as session:
            field = getattr(table_name, field_name)
            result = await session.execute(select(table_name).where(field == kwargs[field_name]))
            return result.scalars().first()


    async def get_records(self, table_name, field_name, **kwargs):
        async with self.Session() as session:
            field = getattr(table_name, field_name)
            result = await session.execute(select(table_name).where(field == kwargs[field_name]))
            return result.scalars().all()

    async def update_record(
        self,
        table_name,
        field_name,
        **kwargs
        ):
        async with self.Session() as session:
            field = getattr(table_name, field_name)
            await session.execute(
                update(table_name)
                .where(field == kwargs[field_name])
                .values(
                    kwargs
                )
            )
            await session.commit()

    async def add_record(self, table_name, **kwargs):
        async with self.Session() as session:
            await session.execute(
                insert(table_name)
                .values(kwargs)
            )
            await session.commit()

    async def delete_record(self, table_name, field_name, **kwargs):
        async with self.Session() as session:
            await session.execute(text("PRAGMA foreign_keys=ON"))
            field = getattr(table_name, field_name)
            await session.execute(
                delete(table_name)
                .where(field == kwargs[field_name])
            )
            await session.commit()
            await session.execute(text("PRAGMA foreign_keys=OFF"))
