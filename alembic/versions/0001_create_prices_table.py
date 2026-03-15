from typing import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0001_create_prices_table"
down_revision: str | None = None
branch_labels: Sequence[str] | None = None
depends_on: Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "prices",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("ticker", sa.String(length=20), nullable=False),
        sa.Column("price", sa.Float(), nullable=False),
        sa.Column("timestamp", sa.BigInteger(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_prices_ticker", "prices", ["ticker"], unique=False)
    op.create_index("ix_prices_timestamp", "prices", ["timestamp"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_prices_timestamp", table_name="prices")
    op.drop_index("ix_prices_ticker", table_name="prices")
    op.drop_table("prices")
