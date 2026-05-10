"""Cross-dialect type aliases.

We target Postgres in production but use SQLite in tests. JSONB and UUID
need explicit fallbacks so model metadata can be created on both.
"""

from sqlalchemy import JSON
from sqlalchemy.dialects.postgresql import JSONB as _PG_JSONB
from sqlalchemy.dialects.postgresql import UUID as _PG_UUID
from sqlalchemy.types import CHAR, TypeDecorator
import uuid as _uuid


JSONB = _PG_JSONB().with_variant(JSON(), "sqlite")


class GUID(TypeDecorator):
    """Platform-independent UUID — Postgres UUID, otherwise CHAR(32)."""

    impl = CHAR
    cache_ok = True

    def load_dialect_impl(self, dialect):
        if dialect.name == "postgresql":
            return dialect.type_descriptor(_PG_UUID(as_uuid=True))
        return dialect.type_descriptor(CHAR(32))

    def process_bind_param(self, value, dialect):
        if value is None or dialect.name == "postgresql":
            return value
        if not isinstance(value, _uuid.UUID):
            value = _uuid.UUID(value)
        return value.hex

    def process_result_value(self, value, dialect):
        if value is None:
            return value
        if isinstance(value, _uuid.UUID):
            return value
        return _uuid.UUID(value)
