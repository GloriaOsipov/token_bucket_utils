# token_bucket_utils

A token bucket rate limiter with burst capacity and monotonic refill.

## Usage

```python
from token_bucket_utils import TokenBucket

bucket = TokenBucket(rate=5.0, capacity=10.0)

if bucket.take(3):
    print("allowed")
else:
    print("denied")
```

`TokenBucket(rate, capacity, now=None)` constructs a bucket that starts full.
`take(n=1)` consumes `n` tokens if available and returns `True`; otherwise it
returns `False` and leaves the bucket untouched. The `tokens` property returns
the current count after applying pending refill.

## Why this exists

Rate limiters often need to allow short bursts while bounding the long-term
rate. A token bucket does this by decoupling burst size (`capacity`) from
steady-state throughput (`rate`). This implementation makes one deliberate
choice: `take` is non-blocking and never waits. If you want to wait for enough
tokens, compute the delay externally and sleep yourself. Keeping the bucket
free of blocking makes it easy to use in event loops and test with a fake
clock.

A clock function can be passed as `now` to make behaviour deterministic in
tests; the default is `time.monotonic`, which does not go backwards.

## Edge cases worth knowing

- Requesting more than `capacity` always fails — the bucket can never hold
  that many tokens at once.
- If the supplied clock moves backwards, the elapsed time is clamped to zero
  so no tokens are created.
- A failed `take` does not consume partial tokens; state is unchanged.

## Running the tests

```
PYTHONPATH=src python -m unittest discover -s tests
```

## Design notes

The window stores values eagerly rather than keeping running aggregates. Running
sums drift with floating point over long streams, and recomputing from a small
buffer is cheap enough that the drift is not worth the speed.

