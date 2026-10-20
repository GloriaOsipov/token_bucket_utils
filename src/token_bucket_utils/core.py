from __future__ import annotations

import time
from typing import Callable


class TokenBucket:
    """
    A token bucket rate limiter with burst capacity and monotonic refill.

    The bucket holds up to ``capacity`` tokens. Tokens refill at ``rate`` per
    second and never exceed ``capacity``. ``take(n)`` checks whether ``n`` tokens
    are available; if so it deducts them and returns ``True``, otherwise it
    returns ``False`` and does not modify state.

    A ``now`` callable may be supplied to provide the current monotonic time.
    This exists so callers can inject a fake clock in tests (wall-clock time is
    non-deterministic and must never be relied on by tests). By default we use
    ``time.monotonic`` because we only ever compare differences between
    readings; it never goes backwards.
    """

    def __init__(
        self,
        rate: float,
        capacity: float,
        now: Callable[[], float] = time.monotonic,
    ) -> None:
        if rate <= 0:
            raise ValueError("rate must be positive")
        if capacity <= 0:
            raise ValueError("capacity must be positive")
        self._rate = float(rate)
        self._capacity = float(capacity)
        self._now = now
        # Start full so a freshly created bucket can absorb one burst up to
        # its capacity.
        self._tokens = float(capacity)
        self._last = now()

    def _refill(self) -> None:
        current = self._now()
        elapsed = current - self._last
        # Guard against a clock that jumped backwards. ``time.monotonic`` can
        # in principle return non-decreasing values, but an injected fake may
        # not; clamping prevents negative refill which would create tokens.
        if elapsed < 0:
            elapsed = 0.0
        self._tokens = min(self._capacity, self._tokens + elapsed * self._rate)
        self._last = current

    def take(self, n: float = 1.0) -> bool:
        """
        Attempt to consume ``n`` tokens. Returns ``True`` if the request was
        granted (tokens deducted), ``False`` otherwise (state unchanged).

        Requesting more than ``capacity`` always fails because the bucket can
        never hold that many tokens at once.
        """
        if n < 0:
            raise ValueError("n must be non-negative")
        self._refill()
        if n == 0:
            return True
        if self._tokens >= n:
            self._tokens -= n
            return True
        return False

    @property
    def tokens(self) -> float:
        """Current token count after applying any pending refill."""
        self._refill()
        return self._tokens

    @property
    def rate(self) -> float:
        return self._rate

    @property
    def capacity(self) -> float:
        return self._capacity
