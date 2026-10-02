from typing import TypeGuard, TypeVar


class _UnsetType:
    """
    Sentinel type for fields that were not provided at all.

    `None` cannot be used for this because, for nullable fields, `None` is a
    valid value and means "explicitly set this field to null".

    Having a separate UNSET value lets us distinguish between:

    - UNSET -> field was not provided, leave the existing value unchanged
    - None  -> field was explicitly provided as null
    - value -> field was explicitly provided with a new value

    The class itself is an implementation detail. Application code should
    normally use the UNSET singleton rather than creating _UnsetType instances.
    """

    # The sentinel carries no data or mutable state.
    # An empty __slots__ also prevents arbitrary attributes from being added.
    __slots__ = ()

    def __repr__(self) -> str:
        # Keeps debugger, log, and dataclass output readable.
        return "UNSET"


# Use one shared instance so application code can reliably check
# omitted values with identity comparisons: `value is UNSET`.
UNSET = _UnsetType()


T = TypeVar("T")


def is_set[T](value: T | _UnsetType) -> TypeGuard[T]:
    """
    Return True when a value is not UNSET and narrow its type for mypy.

    A regular check such as:

        if value is not UNSET:

    is enough for us at runtime, but mypy does not reliably narrow
    `T | _UnsetType` to `T` when comparing against our custom singleton.

    TypeGuard tells the type checker that once this function returns True,
    the value can safely be treated as the original type T.

    For example:

        name: str | _UnsetType

        if is_set(name):
            # name is treated as str here
            ...

    It also preserves valid nullable values:

        description: str | None | _UnsetType

        if is_set(description):
            # description is str | None here
            ...

    This keeps UNSET handling explicit without scattering cast() calls
    throughout the service layer.
    """

    return value is not UNSET
