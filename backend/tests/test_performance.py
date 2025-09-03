"""
Performance tests for the scoring engine.
"""

import os
import time
from decimal import Decimal

import psutil
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from scoringengine.models import Lead, Recommendation, ScoringModel, ValueRange
from tests.fixtures import (
    choice_question,
    date_question,
    question,
    slider_question,
    user,
)


class PerformanceTestCase(TestCase):
    """Base class for performance tests."""

    def setUp(self):
        self.client = APIClient()
        self.user = user()
        self.token = self.user.auth_token
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.token.key}")

        # Create test data
        self.question = question()
        self.choice_question = choice_question()
        self.slider_question = slider_question()
        self.date_question = date_question()

        # Create scoring models
        self.scoring_model = ScoringModel.objects.create(
            question=self.question,
            owner=self.user,
            weight=Decimal("1.0"),
            x_axis=True,
            y_axis=False,
        )

        # Create value ranges
        ValueRange.objects.create(
            scoring_model=self.scoring_model,
            start=Decimal("0"),
            end=Decimal("25"),
            points=10,
        )
        ValueRange.objects.create(
            scoring_model=self.scoring_model,
            start=Decimal("25"),
            end=Decimal("50"),
            points=20,
        )

        # Create recommendation
        self.recommendation = Recommendation.objects.create(
            question=self.question,
            owner=self.user,
            rule="If {age} >= 25",
            response_text="You are eligible!",
        )


class TestLeadCreationPerformance(PerformanceTestCase):
    """Performance tests for lead creation."""

    def test_lead_creation_speed(self):
        """Test that lead creation is fast (< 100ms)."""
        url = reverse("api:v1:leads-list")
        data = {
            "answers": {
                "age": "30",
                "income": "Medium",
                "satisfaction": "8",
                "start_date": "2024-01-15",
            }
        }

        start_time = time.time()
        response = self.client.post(url, data, format="json")
        end_time = time.time()

        execution_time = (end_time - start_time) * 1000  # Convert to milliseconds

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertLess(
            execution_time,
            100,
            f"Lead creation took {execution_time:.2f}ms, expected < 100ms",
        )

    def test_bulk_lead_creation_performance(self):
        """Test performance of creating multiple leads."""
        url = reverse("api:v1:leads-list")

        start_time = time.time()

        for i in range(10):
            data = {
                "answers": {
                    "age": str(25 + i),
                    "income": ["Low", "Medium", "High"][i % 3],
                    "satisfaction": str(5 + i % 6),
                    "start_date": f"2024-{i+1:02d}-15",
                }
            }
            response = self.client.post(url, data, format="json")
            self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        end_time = time.time()
        total_time = (end_time - start_time) * 1000
        avg_time = total_time / 10

        self.assertLess(
            avg_time,
            50,
            f"Average lead creation took {avg_time:.2f}ms, expected < 50ms",
        )
        self.assertEqual(Lead.objects.filter(owner=self.user).count(), 10)


class TestQueryPerformance(PerformanceTestCase):
    """Performance tests for database queries."""

    def setUp(self):
        super().setUp()
        # Create multiple leads for testing
        for i in range(50):
            Lead.objects.create(
                owner=self.user,
                x_axis=Decimal(f"{20 + i}"),
                y_axis=Decimal(f"{10 + i}"),
                total_score=Decimal(f"{30 + i * 2}"),
            )

    def test_lead_list_query_performance(self):
        """Test that lead list queries are fast."""
        url = reverse("api:v1:leads-list")

        start_time = time.time()
        response = self.client.get(url)
        end_time = time.time()

        execution_time = (end_time - start_time) * 1000

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertLess(
            execution_time,
            50,
            f"Lead list query took {execution_time:.2f}ms, expected < 50ms",
        )

    def test_analytics_query_performance(self):
        """Test that analytics queries are fast."""
        url = reverse("api:v1:analytics-lead-summary")

        start_time = time.time()
        response = self.client.get(url)
        end_time = time.time()

        execution_time = (end_time - start_time) * 1000

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertLess(
            execution_time,
            100,
            f"Analytics query took {execution_time:.2f}ms, expected < 100ms",
        )

    def test_question_analytics_performance(self):
        """Test that question analytics queries are fast."""
        url = reverse("api:v1:analytics-question-analytics")

        start_time = time.time()
        response = self.client.get(url)
        end_time = time.time()

        execution_time = (end_time - start_time) * 1000

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertLess(
            execution_time,
            100,
            f"Question analytics query took {execution_time:.2f}ms, expected < 100ms",
        )


class TestCachePerformance(PerformanceTestCase):
    """Performance tests for caching."""

    def setUp(self):
        super().setUp()
        # Create some leads
        for i in range(10):
            Lead.objects.create(
                owner=self.user,
                x_axis=Decimal(f"{20 + i}"),
                y_axis=Decimal(f"{10 + i}"),
                total_score=Decimal(f"{30 + i * 2}"),
            )

    def test_cache_effectiveness(self):
        """Test that caching improves performance."""
        url = reverse("api:v1:analytics-lead-summary")

        # First request (cache miss)
        start_time = time.time()
        response1 = self.client.get(url)
        first_request_time = (time.time() - start_time) * 1000

        # Second request (cache hit)
        start_time = time.time()
        response2 = self.client.get(url)
        second_request_time = (time.time() - start_time) * 1000

        self.assertEqual(response1.status_code, status.HTTP_200_OK)
        self.assertEqual(response2.status_code, status.HTTP_200_OK)

        # Cache hit should be significantly faster
        self.assertLess(
            second_request_time,
            first_request_time * 0.5,
            f"Cache hit ({second_request_time:.2f}ms) should be faster than cache miss ({first_request_time:.2f}ms)",
        )


class TestConcurrentAccessPerformance(PerformanceTestCase):
    """Performance tests for concurrent access."""

    def test_concurrent_lead_creation(self):
        """Test that multiple concurrent lead creations work correctly."""
        import queue
        import threading

        url = reverse("api:v1:leads-list")
        results = queue.Queue()

        def create_lead(thread_id):
            data = {
                "answers": {
                    "age": str(25 + thread_id),
                    "income": "Medium",
                    "satisfaction": "8",
                    "start_date": "2024-01-15",
                }
            }

            start_time = time.time()
            response = self.client.post(url, data, format="json")
            end_time = time.time()

            results.put(
                {
                    "thread_id": thread_id,
                    "status_code": response.status_code,
                    "time": (end_time - start_time) * 1000,
                }
            )

        # Create 5 concurrent threads
        threads = []
        for i in range(5):
            thread = threading.Thread(target=create_lead, args=(i,))
            threads.append(thread)
            thread.start()

        # Wait for all threads to complete
        for thread in threads:
            thread.join()

        # Check results
        successful_creations = 0
        total_time = 0

        while not results.empty():
            result = results.get()
            if result["status_code"] == status.HTTP_201_CREATED:
                successful_creations += 1
            total_time += result["time"]

        self.assertEqual(
            successful_creations, 5, "All concurrent lead creations should succeed"
        )
        self.assertLess(
            total_time / 5, 100, "Average concurrent creation time should be < 100ms"
        )


class TestMemoryUsagePerformance(PerformanceTestCase):
    """Performance tests for memory usage."""

    def test_memory_efficient_lead_creation(self):
        """Test that lead creation doesn't cause memory leaks."""

        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB

        url = reverse("api:v1:leads-list")

        # Create 100 leads
        for i in range(100):
            data = {
                "answers": {
                    "age": str(25 + i),
                    "income": ["Low", "Medium", "High"][i % 3],
                    "satisfaction": str(5 + i % 6),
                    "start_date": f"2024-{i+1:02d}-15",
                }
            }
            response = self.client.post(url, data, format="json")
            self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        final_memory = process.memory_info().rss / 1024 / 1024  # MB
        memory_increase = final_memory - initial_memory

        # Memory increase should be reasonable (< 50MB for 100 leads)
        self.assertLess(
            memory_increase,
            50,
            f"Memory usage increased by {memory_increase:.2f}MB, expected < 50MB",
        )


class TestDatabaseIndexPerformance(PerformanceTestCase):
    """Performance tests for database indexes."""

    def setUp(self):
        super().setUp()
        # Create many leads with different scores
        for i in range(1000):
            Lead.objects.create(
                owner=self.user,
                x_axis=Decimal(f"{i % 100}"),
                y_axis=Decimal(f"{i % 50}"),
                total_score=Decimal(f"{i % 200}"),
            )

    def test_indexed_query_performance(self):
        """Test that queries on indexed fields are fast."""
        # Test query on owner field (should be indexed)
        start_time = time.time()
        leads = Lead.objects.filter(owner=self.user)
        owner_query_time = (time.time() - start_time) * 1000

        # Test query on total_score field (should be indexed)
        start_time = time.time()
        high_score_leads = Lead.objects.filter(total_score__gte=100)
        score_query_time = (time.time() - start_time) * 1000

        self.assertLess(
            owner_query_time,
            10,
            f"Owner query took {owner_query_time:.2f}ms, expected < 10ms",
        )
        self.assertLess(
            score_query_time,
            10,
            f"Score query took {score_query_time:.2f}ms, expected < 10ms",
        )

        # Verify results
        self.assertEqual(leads.count(), 1000)
        self.assertGreater(high_score_leads.count(), 0)


class TestAPILoadTest(PerformanceTestCase):
    """Load testing for API endpoints."""

    def test_api_load_handling(self):
        """Test that API can handle multiple rapid requests."""
        url = reverse("api:v1:leads-list")

        # Make 50 rapid requests
        start_time = time.time()
        successful_requests = 0

        for i in range(50):
            data = {
                "answers": {
                    "age": str(25 + i),
                    "income": "Medium",
                    "satisfaction": "8",
                    "start_date": "2024-01-15",
                }
            }
            response = self.client.post(url, data, format="json")
            if response.status_code == status.HTTP_201_CREATED:
                successful_requests += 1

        total_time = (time.time() - start_time) * 1000
        avg_time = total_time / 50

        self.assertEqual(
            successful_requests, 50, "All requests should succeed under load"
        )
        self.assertLess(
            avg_time,
            50,
            f"Average request time under load: {avg_time:.2f}ms, expected < 50ms",
        )
        self.assertLess(
            total_time,
            5000,
            f"Total time for 50 requests: {total_time:.2f}ms, expected < 5000ms",
        )
