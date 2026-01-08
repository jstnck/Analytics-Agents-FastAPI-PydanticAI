def test_root_endpoint(client):
    """Test the root endpoint returns welcome message."""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "Analytics Agent API" in data["message"]


def test_health_check(client):
    """Test the health check endpoint."""
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"


def test_chat_endpoint(client):
    """Test the chat endpoint returns proper response."""
    payload = {"message": "Hello, agent!"}
    response = client.post("/api/v1/chat", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "conversation_id" in data
    assert "timestamp" in data
    assert "Hello, agent!" in data["message"]


def test_chat_endpoint_with_conversation_id(client):
    """Test chat endpoint maintains conversation ID."""
    conv_id = "test-conv-123"
    payload = {"message": "Test message", "conversation_id": conv_id}
    response = client.post("/api/v1/chat", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["conversation_id"] == conv_id


def test_chat_endpoint_generates_conversation_id(client):
    """Test chat endpoint generates conversation ID if not provided."""
    payload = {"message": "Test message"}
    response = client.post("/api/v1/chat", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "conversation_id" in data
    assert data["conversation_id"].startswith("conv-")


def test_chat_endpoint_empty_message(client):
    """Test chat endpoint rejects empty message."""
    payload = {"message": ""}
    response = client.post("/api/v1/chat", json=payload)
    assert response.status_code == 422  # Validation error
