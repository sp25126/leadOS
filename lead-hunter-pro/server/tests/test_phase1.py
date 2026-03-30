import pytest
import asyncio
import os
import json
from unittest.mock import patch, AsyncMock
from utils.rate_limiter import QuotaManager
from utils.phone_normalizer import normalize_phone


class TestQuotaManager:
    def setup_method(self):
        # Fresh quota state for each test
        if os.path.exists("quota_state_test.json"):
            os.remove("quota_state_test.json")
        self.qm = QuotaManager(state_file="quota_state_test.json")

    def test_has_quota_fresh(self):
        assert self.qm.has_quota("google_maps") == True

    def test_consume_reduces_remaining(self):
        before = self.qm.remaining("here_places")
        self.qm.consume("here_places", 10)
        assert self.qm.remaining("here_places") == before - 10

    def test_exhausted_source_returns_false(self):
        self.qm.consume("hunter_io", 25)
        assert self.qm.has_quota("hunter_io") == False

    def test_persists_across_instances(self):
        self.qm.consume("google_maps", 500)
        qm2 = QuotaManager(state_file="quota_state_test.json")
        assert qm2.remaining("google_maps") == 9500

    def test_remaining_never_negative(self):
        self.qm.consume("hunter_io", 999)
        assert self.qm.remaining("hunter_io") == 0


class TestPhoneNormalizer:
    def test_10_digit_adds_country_code(self):
        assert normalize_phone("9876543210") == "+919876543210"

    def test_leading_zero_replaced(self):
        assert normalize_phone("09876543210") == "+919876543210"

    def test_spaces_and_dashes_stripped(self):
        assert normalize_phone("+91 98765-43210") == "+919876543210"

    def test_already_formatted_unchanged(self):
        assert normalize_phone("+919876543210") == "+919876543210"

    def test_none_returns_empty(self):
        assert normalize_phone(None) == ""

    def test_too_short_returns_empty(self):
        assert normalize_phone("12345") == ""

    def test_international_non_india(self):
        result = normalize_phone("+12025551234")
        assert result == "+12025551234"
