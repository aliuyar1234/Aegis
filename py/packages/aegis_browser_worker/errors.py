class BrowserWorkerError(Exception):
    """Base error for the browser worker package."""


class UnsupportedWorkflowError(BrowserWorkerError):
    """Raised when a workflow exceeds the current Phase 05 browser baseline."""


class BrowserVerificationError(BrowserWorkerError):
    """Raised when a verify step cannot prove the expected browser state."""


class PlaywrightUnavailableError(BrowserWorkerError):
    """Raised when the Playwright adapter is selected without the dependency."""
