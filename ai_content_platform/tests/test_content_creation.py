
import pytest
import os
from ai_content_platform.app.modules.content import gemini_service

@pytest.fixture(autouse=True)
def mock_gemini(monkeypatch):
    """
    Automatically mock GeminiService.generate_text for all tests in this module.
    This avoids real API calls and ensures tests are fast and reliable.
    """
    # Set a dummy Gemini API key for testing
    monkeypatch.setenv("GEMINI_API_KEY", "test-gemini-api-key")
    # Mock GeminiService.generate_text to always return predictable content
    async def mock_generate_text(self, prompt, **kwargs):
        if "Summarize" in prompt:
            return "This is a summary of the AI article."
        return "This is AI generated content."
    monkeypatch.setattr(gemini_service.GeminiService, "generate_text", mock_generate_text)

@pytest.mark.usefixtures("client")
def test_create_article_with_new_and_existing_tags(client):
    # Register and login a user to get JWT access token
    client.post("/auth/register", json={"username": "alice_test", "email": "alice@example.com", "password": "string", "role": "admin"})
    login_response = client.post("/auth/login", data={"username": "alice_test", "password": "string"})
    assert login_response.status_code == 200
    tokens = login_response.json()
    access_token = tokens["access_token"]
    headers = {"Authorization": f"Bearer {access_token}"}

    # Create an article with new tags
    response = client.post(
        "/content/articles/",
        json={
            "title": "AI Content Test",
            "content": "This is a test article about AI.",
            "summary": "Test summary.",
            "tag_names": ["AI", "FastAPI", "Python"]
        },
        headers=headers
    )
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "AI Content Test"
    assert set([t["name"] for t in data["tags"]]) == {"ai", "fastapi", "python"}

    # Create another article with some existing and some new tags
    response2 = client.post(
        "/content/articles/",
        json={
            "title": "Second Article",
            "content": "Another article.",
            "summary": "Second summary.",
            "tag_names": ["AI", "NewTag"]
        },
        headers=headers
    )
    assert response2.status_code == 200
    data2 = response2.json()
    assert data2["title"] == "Second Article"
    assert set([t["name"] for t in data2["tags"]]) == {"ai", "newtag"}

    # List all tags
    tags_response = client.get("/content/tags/", headers=headers)
    assert tags_response.status_code == 200
    tags = tags_response.json()
    tag_names = [t["name"] for t in tags]
    for name in ["ai", "fastapi", "python", "newtag"]:
        assert name in tag_names

    # List all articles
    articles_response = client.get("/content/articles/", headers=headers)
    assert articles_response.status_code == 200
    articles = articles_response.json()
    assert len(articles) >= 2
    titles = [a["title"] for a in articles]
    assert "AI Content Test" in titles
    assert "Second Article" in titles

    # Update article to add more tags
    article_id = data["id"]
    update_response = client.put(
        f"/content/articles/{article_id}",
        json={
            "tag_names": ["AI", "FastAPI", "ExtraTag"]
        },
        headers=headers
    )
    assert update_response.status_code == 200
    updated = update_response.json()
    updated_tag_names = [t["name"] for t in updated["tags"]]
    for name in ["ai", "fastapi", "extratag"]:
        assert name in updated_tag_names

    # Test AI-powered article generation (protected endpoint)
    ai_gen_response = client.post(
        "/content/articles/generate/",
        json={
            "title": "AI Generated Article",
            "content": "Write about the impact of AI on society.",
            "summary": None,
            "tag_names": ["AI", "Society"]
        },
        headers=headers
    )
    assert ai_gen_response.status_code == 200
    ai_data = ai_gen_response.json()
    assert ai_data["title"] == "AI Generated Article"
    assert "ai" in [t["name"] for t in ai_data["tags"]]
    assert "society" in [t["name"] for t in ai_data["tags"]]
    assert ai_data["content"] and "AI" in ai_data["content"]
    assert ai_data["summary"]

    # Test AI-powered summarization (protected endpoint)
    article_id = ai_data["id"]
    ai_sum_response = client.post(f"/content/articles/{article_id}/summarize/", headers=headers)
    assert ai_sum_response.status_code == 200
    ai_sum_data = ai_sum_response.json()
    assert ai_sum_data["summary"]
    assert len(ai_sum_data["summary"]) > 0

    # Delete article
    del_response = client.delete(f"/content/articles/{article_id}", headers=headers)
    assert del_response.status_code == 200
    assert del_response.json()["detail"] == "Deleted"

    # Try to get deleted article
    get_deleted = client.get(f"/content/articles/{article_id}", headers=headers)
    assert get_deleted.status_code == 404
