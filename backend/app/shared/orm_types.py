"""Shared helpers for ORM Column handling.

SQLAlchemy 2.0 typed ORM exposes every column attribute as
`Column[T]` rather than `T`. At call sites this produces dozens of
false-positive mypy errors. These helpers provide one explicit cast
at the boundary where ORM objects cross into business logic functions.
"""

from sqlalchemy.sql.schema import Column
from typing import Any, TypeVar

T = TypeVar("T")


def value_of(column: Column[T]) -> T:
    """Cast an ORM Column[T] to its Python type T.

    Usage::

        def service_fn(user_id: int, db: Session):
            ...
        service_fn(value_of(current_user.id), db)

    The runtime value is already a Python object — only the static
    type annotation is misleading. This helper documents the cast.
    """
    return column  # type: ignore[return-value]
