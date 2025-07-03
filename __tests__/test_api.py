import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock


class TestRootEndpoint:
    def test_root_returns_service_info(self, client):
        """Тест корневого эндпоинта"""
        response = client.get("/")
        assert response.status_code == 200
        
        data = response.json()
        assert data["service"] == "LISA Backend API"
        assert data["status"] == "running"
        assert "version" in data
        assert "timestamp" in data

    def test_root_has_correct_content_type(self, client):
        """Тест типа контента"""
        response = client.get("/")
        assert response.headers["content-type"] == "application/json"


class TestHealthEndpoint:
    def test_health_check(self, client):
        """Тест эндпоинта health check"""
        response = client.get("/health")
        assert response.status_code == 200
        
        data = response.json()
        assert data["status"] == "healthy"
        assert "uptime" in data


class TestDashboardStats:
    def test_dashboard_stats_structure(self, client):
        """Тест структуры статистики дашборда"""
        response = client.get("/api/dashboard/stats")
        assert response.status_code == 200
        
        data = response.json()
        required_fields = [
            "total_agents", 
            "online_agents", 
            "system_status", 
            "last_updated"
        ]
        
        for field in required_fields:
            assert field in data

    def test_dashboard_stats_types(self, client):
        """Тест типов данных в статистике"""
        response = client.get("/api/dashboard/stats")
        data = response.json()
        
        assert isinstance(data["total_agents"], int)
        assert isinstance(data["online_agents"], int)
        assert isinstance(data["system_status"], str)
        assert data["system_status"] in ["healthy", "warning", "error"]

    @patch('main.get_agent_count')
    def test_dashboard_stats_with_mock(self, mock_get_agent_count, client):
        """Тест с мокингом данных"""
        mock_get_agent_count.return_value = 42
        
        response = client.get("/api/dashboard/stats")
        data = response.json()
        
        assert data["total_agents"] == 42


class TestAgentEndpoints:
    def test_get_agents_list(self, client):
        """Тест получения списка агентов"""
        response = client.get("/api/agents")
        assert response.status_code == 200
        
        data = response.json()
        assert isinstance(data, list)

    def test_create_agent(self, client, test_data):
        """Тест создания агента"""
        response = client.post("/api/agents", json=test_data)
        assert response.status_code == 201
        
        data = response.json()
        assert data["agent_id"] == test_data["agent_id"]
        assert data["agent_name"] == test_data["agent_name"]

    def test_get_agent_by_id(self, client):
        """Тест получения агента по ID"""
        agent_id = "test-agent-001"
        response = client.get(f"/api/agents/{agent_id}")
        
        # Может быть 200 или 404 в зависимости от реализации
        assert response.status_code in [200, 404]

    def test_agent_not_found(self, client):
        """Тест несуществующего агента"""
        response = client.get("/api/agents/nonexistent-agent")
        assert response.status_code == 404


class TestErrorHandling:
    def test_invalid_endpoint(self, client):
        """Тест несуществующего эндпоинта"""
        response = client.get("/api/nonexistent")
        assert response.status_code == 404

    def test_invalid_method(self, client):
        """Тест неподдерживаемого HTTP метода"""
        response = client.patch("/api/dashboard/stats")
        assert response.status_code == 405

    def test_invalid_json_payload(self, client):
        """Тест невалидного JSON"""
        response = client.post(
            "/api/agents", 
            data="invalid json",
            headers={"content-type": "application/json"}
        )
        assert response.status_code == 422


class TestPerformance:
    @pytest.mark.slow
    def test_dashboard_stats_performance(self, client):
        """Тест производительности эндпоинта"""
        import time
        
        start_time = time.time()
        response = client.get("/api/dashboard/stats")
        end_time = time.time()
        
        assert response.status_code == 200
        assert (end_time - start_time) < 1.0  # Должен отвечать быстрее 1 секунды
