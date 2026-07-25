class IkiSchemaError(Exception):
    """Base class for all ikischema exceptions."""


class SchemaInferenceError(IkiSchemaError):
    """Raised when a schema cannot be inferred from the given source."""


class AmbiguousTypeError(SchemaInferenceError):
    """Reserved for genuinely unrecoverable type ambiguity."""


class ContractViolationError(IkiSchemaError):
    """Raised when a breaking contract violation is found."""

    def __init__(self, violations):
        self.violations = violations
        breaking = [v for v in violations if getattr(
            v, "severity", None) == "breaking"]
        super().__init__(f"{len(breaking)} breaking violation(s): {breaking}")


class ContractLoadError(IkiSchemaError):
    """Raised when a contract cannot be loaded from disk."""
