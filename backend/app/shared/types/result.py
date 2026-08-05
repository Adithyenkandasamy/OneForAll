"""Explicit Result type for cross-module boundaries.

Prevents exception-based control flow: functions return ``Ok(value)`` or
``Err(error)`` and callers must handle both branches.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Generic, TypeVar

T = TypeVar("T")
E = TypeVar("E")


@dataclass(frozen=True)
class Ok(Generic[T]):
    value: T

    def is_ok(self) -> bool:
        return True

    def unwrap(self) -> T:
        return self.value

    def unwrap_or(self, _default: T) -> T:  # noqa: ARG002
        return self.value


@dataclass(frozen=True)
class Err(Generic[E]):
    error: E

    def is_ok(self) -> bool:
        return False

    def unwrap(self) -> None:
        raise ValueError("Called unwrap() on an Err")

    def unwrap_or(self, default: T) -> T:  # type: ignore[type-var]
        return default


Result = Ok[T] | Err[E]


def ok(value: T) -> Ok[T]:  # type: ignore[type-var]
    return Ok(value)


def err(error: E) -> Err[E]:  # type: ignore[type-var]
    return Err(error)
