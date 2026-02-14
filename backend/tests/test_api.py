"""Tests for API endpoints (integration-style with mocked DB)."""

import pytest
from unittest.mock import patch, AsyncMock, MagicMock
from datetime import datetime, timezone

from fastapi.testclient import TestClient


class TestHealthEndpoint:
    def test_health_check(self):
        # Patch scheduler to avoid DB dependency during import
        with patch("app.schedulers.scheduler.init_scheduler"):
            with patch("app.schedulers.scheduler.start_scheduler"):
                from app.main import app

                client = TestClient(app)
                response = client.get("/health")
                assert response.status_code == 200
                data = response.json()
                assert data["status"] == "healthy"


class TestNarrativesEndpoint:
    """Test narrative list/detail endpoints with mocked database."""

    def _mock_narrative(self, id=1, title="Test Narrative", is_active=True):
        mock = MagicMock()
        mock.id = id
        mock.title = title
        mock.summary = "Test summary"
        mock.confidence = "high"
        mock.confidence_reasoning = "Strong signals"
        mock.is_active = is_active
        mock.velocity_score = 5.5
        mock.rank = 1
        mock.tags = ["defi", "infrastructure"]
        mock.key_evidence = ["evidence1"]
        mock.supporting_source_names = ["Helius Blog"]
        mock.ideas = []
        mock.narrative_sources = []
        mock.created_at = datetime(2026, 1, 1, tzinfo=timezone.utc)
        mock.updated_at = datetime(2026, 1, 1, tzinfo=timezone.utc)
        mock.last_detected_at = datetime(2026, 1, 1, tzinfo=timezone.utc)
        return mock
