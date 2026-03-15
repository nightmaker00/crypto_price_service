from sqlalchemy import and_, desc, select
from sqlalchemy.ext.asyncio import async_sessionmaker

from app.domain.entities.price import Price
from app.domain.repositories.price_repository import PriceRepository
from app.infrastructure.database.models import PriceModel


class SqlAlchemyPriceRepository(PriceRepository):
    def __init__(self, session_factory: async_sessionmaker) -> None:
        self._session_factory = session_factory

    async def save(self, price: Price) -> Price:
        async with self._session_factory() as session:
            db_price = PriceModel(
                ticker=price.ticker, price=price.price, timestamp=price.timestamp
            )
            session.add(db_price)
            await session.commit()
            return Price(ticker=db_price.ticker, price=db_price.price, timestamp=db_price.timestamp)

    async def get_all_by_ticker(self, ticker: str) -> list[Price]:
        async with self._session_factory() as session:
            result = await session.execute(
                select(PriceModel).where(PriceModel.ticker == ticker).order_by(PriceModel.timestamp)
            )
            rows = result.scalars().all()
            return [Price(ticker=row.ticker, price=row.price, timestamp=row.timestamp) for row in rows]

    async def get_latest_by_ticker(self, ticker: str) -> Price | None:
        async with self._session_factory() as session:
            result = await session.execute(
                select(PriceModel)
                .where(PriceModel.ticker == ticker)
                .order_by(desc(PriceModel.timestamp))
                .limit(1)
            )
            row = result.scalars().first()
            if row is None:
                return None
            return Price(ticker=row.ticker, price=row.price, timestamp=row.timestamp)

    async def get_by_ticker_and_period(
        self, ticker: str, start_timestamp: int, end_timestamp: int
    ) -> list[Price]:
        async with self._session_factory() as session:
            result = await session.execute(
                select(PriceModel)
                .where(
                    and_(
                        PriceModel.ticker == ticker,
                        PriceModel.timestamp >= start_timestamp,
                        PriceModel.timestamp <= end_timestamp,
                    )
                )
                .order_by(PriceModel.timestamp)
            )
            rows = result.scalars().all()
            return [Price(ticker=row.ticker, price=row.price, timestamp=row.timestamp) for row in rows]
