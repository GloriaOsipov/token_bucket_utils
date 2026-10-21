import unittest

from token_bucket_utils import TokenBucket


class TestTokenBucket(unittest.TestCase):
    def test_initial_burst(self):
        bucket = TokenBucket(rate=1.0, capacity=5.0, now=lambda: 0.0)
        self.assertTrue(bucket.take(5))

    def test_burst_then_empty(self):
        bucket = TokenBucket(rate=1.0, capacity=5.0, now=lambda: 0.0)
        self.assertTrue(bucket.take(5))
        self.assertFalse(bucket.take(1))

    def test_refill_after_elapsed(self):
        clock = [0.0]
        bucket = TokenBucket(rate=2.0, capacity=5.0, now=lambda: clock[0])
        self.assertTrue(bucket.take(5))
        self.assertFalse(bucket.take(1))
        clock[0] = 3.0  # 6 tokens accrued, capped at capacity 5
        self.assertTrue(bucket.take(5))

    def test_partial_refill_insufficient(self):
        clock = [0.0]
        bucket = TokenBucket(rate=1.0, capacity=5.0, now=lambda: clock[0])
        self.assertTrue(bucket.take(5))
        clock[0] = 2.0  # only 2 tokens available
        self.assertFalse(bucket.take(3))
        self.assertTrue(bucket.take(2))

    def test_take_zero_always_succeeds(self):
        bucket = TokenBucket(rate=1.0, capacity=1.0, now=lambda: 0.0)
        self.assertTrue(bucket.take(0))
        self.assertTrue(bucket.take(0))

    def test_take_exceeding_capacity_fails(self):
        bucket = TokenBucket(rate=1.0, capacity=5.0, now=lambda: 0.0)
        self.assertFalse(bucket.take(6))

    def test_negative_n_raises(self):
        bucket = TokenBucket(rate=1.0, capacity=5.0, now=lambda: 0.0)
        with self.assertRaises(ValueError):
            bucket.take(-1)

    def test_non_positive_rate_raises(self):
        with self.assertRaises(ValueError):
            TokenBucket(rate=0, capacity=5.0, now=lambda: 0.0)

    def test_non_positive_capacity_raises(self):
        with self.assertRaises(ValueError):
            TokenBucket(rate=1.0, capacity=0, now=lambda: 0.0)

    def test_failed_take_leaves_state_unchanged(self):
        clock = [0.0]
        bucket = TokenBucket(rate=1.0, capacity=5.0, now=lambda: clock[0])
        self.assertTrue(bucket.take(4))  # 1 token left
        clock[0] = 1.0  # 2 tokens
        self.assertFalse(bucket.take(3))
        self.assertTrue(bucket.take(2))

    def test_negative_clock_jump_clamped(self):
        clock = [0.0]
        bucket = TokenBucket(rate=1.0, capacity=5.0, now=lambda: clock[0])
        self.assertTrue(bucket.take(5))
        clock[0] = -10.0
        self.assertFalse(bucket.take(1))

    def test_properties(self):
        bucket = TokenBucket(rate=1.5, capacity=3.0, now=lambda: 0.0)
        self.assertEqual(bucket.rate, 1.5)
        self.assertEqual(bucket.capacity, 3.0)

    def test_tokens_property_refills(self):
        clock = [0.0]
        bucket = TokenBucket(rate=1.0, capacity=5.0, now=lambda: clock[0])
        self.assertTrue(bucket.take(5))
        clock[0] = 2.0
        self.assertAlmostEqual(bucket.tokens, 2.0)


if __name__ == "__main__":
    unittest.main()
