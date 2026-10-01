class _UnsetType:
    """
    Sentinel type representing a field that was not provided at all.

    ``None`` can't be used for this because it may itself be a valid value.
    For partial updates we therefore need three distinct states:

        UNSET   -> do not change the field
        None    -> explicitly clear the field
        value   -> replace the field

    Use the shared ``UNSET`` instance below instead of creating new instances.
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
