import pytest
from backend.app.core.rate_limiter import rate_limiter

@pytest.fixture(autouse=True)
def reset_rate_limits_between_tests():
    """Ensures each test gets a clean rate limit window."""
    rate_limiter.reset()
    yield
    rate_limiter.reset()

