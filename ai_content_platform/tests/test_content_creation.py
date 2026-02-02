# Ensure user is assigned admin role in DB (in case registration does not do it)
from ai_content_platform.app.modules.auth.models import Role, user_roles
from ai_content_platform.app.database import Base
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from ai_content_platform.app.modules.users.models import User
from ai_content_platform.app.main import app as fastapi_app
from ai_content_platform.tests.conftest import AsyncTestingSessionLocal
import pytest
import httpx
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


@pytest.mark.asyncio
async def test_create_article_with_new_and_existing_tags(client):
        # Register user
        await client.post("/auth/register", json={"username": "alice_test", "email": "alice@example.com", "password": "string", "role": "admin"})

        from ai_content_platform.app.modules.auth.models import Permission, role_permissions
        async def ensure_admin_and_permission():
                        # Get or create summarize_content permission
                        summ_perm = (await session.execute(select(Permission).where(Permission.name == 'summarize_content'))).scalar_one_or_none()
                        if not summ_perm:
                            summ_perm = Permission(name='summarize_content', description='Can summarize articles')
                            session.add(summ_perm)
                            await session.commit()
                            await session.refresh(summ_perm)
                        # Link summarize_content permission to admin role if not already
                        summ_rp_exists = (await session.execute(role_permissions.select().where(
                            (role_permissions.c.role_id == admin_role.id) & (role_permissions.c.permission_id == summ_perm.id)
                        ))).first()
                        if not summ_rp_exists:
                            await session.execute(role_permissions.insert().values(role_id=admin_role.id, permission_id=summ_perm.id))
                            await session.commit()
        async with AsyncTestingSessionLocal() as session:
                users_table = Base.metadata.tables['users']
                # Get user
                user = (await session.execute(select(users_table).where(users_table.c.username == 'alice_test'))).first()
                # Get or create admin role
                admin_role = (await session.execute(select(Role).where(Role.name == 'admin'))).scalar_one_or_none()
                if not admin_role:
                    admin_role = Role(name='admin')
                    session.add(admin_role)
                    await session.commit()
                    await session.refresh(admin_role)
                # Get or create generate_content permission
                perm = (await session.execute(select(Permission).where(Permission.name == 'generate_content'))).scalar_one_or_none()
                if not perm:
                    perm = Permission(name='generate_content', description='Can generate AI content')
                    session.add(perm)
                    await session.commit()
                    await session.refresh(perm)
                # Link permission to admin role if not already
                rp_exists = (await session.execute(role_permissions.select().where((role_permissions.c.role_id == admin_role.id) & (role_permissions.c.permission_id == perm.id)))).first()
                if not rp_exists:
                    await session.execute(role_permissions.insert().values(role_id=admin_role.id, permission_id=perm.id))
                    await session.commit()
                # Assign admin role to user if not already
                if user:
                    user_row = user[0]
                    if hasattr(user_row, 'id'):
                        user_id = user_row.id
                    elif isinstance(user_row, int):
                        user_id = user_row
                    elif isinstance(user_row, (tuple, list)):
                        user_id = user_row[0]
                    else:
                        raise Exception(f"Unexpected user row type: {type(user_row)}")
                    ur_exists = (await session.execute(user_roles.select().where((user_roles.c.user_id == user_id) & (user_roles.c.role_id == admin_role.id)))).first()
                    if not ur_exists:
                        await session.execute(user_roles.insert().values(user_id=user_id, role_id=admin_role.id))
                        await session.commit()

        await ensure_admin_and_permission()

        # Now login
        login_response = await client.post("/auth/login", data={"username": "alice_test", "password": "string"})
        assert login_response.status_code == 200
        tokens = login_response.json()
        access_token = tokens["access_token"]
        headers = {"Authorization": f"Bearer {access_token}"}

        # Debug: Print user roles and permissions after login
        async with AsyncTestingSessionLocal() as session:
            result = await session.execute(
                select(User).where(User.username == "alice_test").options(
                    selectinload(User.roles).selectinload(Role.permissions)
                )
            )
            user = result.scalars().first()
            print("User roles:", [r.name for r in user.roles])
            print("User permissions:", [p.name for r in user.roles for p in r.permissions])

        # Helper to robustly get JSON or print error
        def get_json_or_debug(response):
            try:
                if response.headers.get("content-type", "").startswith("application/json"):
                    return response.json()
                else:
                    print("Non-JSON response:", response.text)
                    return None
            except Exception as e:
                print(f"Failed to parse JSON: {e}\nResponse text: {response.text}")
                return None


        # Create an article with new tags
        response = await client.post(
            "/content/articles/",
            json={
                "title": "AI Content Test",
                "content": "This is a test article about AI.",
                "summary": "Test summary.",
                "tag_names": ["AI", "FastAPI", "Python"]
            },
            headers=headers
        )
        if response.status_code != 200:
            print("Create article failed:", response.status_code, response.text)
        assert response.status_code == 200
        data = get_json_or_debug(response)
        assert data is not None, f"Create article response is None! Status: {response.status_code}, Text: {response.text}"
        assert data["title"] == "AI Content Test"
        assert set([t["name"] for t in data["tags"]]) == {"ai", "fastapi", "python"}

        # Create another article with some existing and some new tags
        response2 = await client.post(
            "/content/articles/",
            json={
                "title": "Second Article",
                "content": "Another article.",
                "summary": "Second summary.",
                "tag_names": ["AI", "NewTag"]
            },
            headers=headers
        )
        if response2.status_code != 200:
            print("Create 2nd article failed:", response2.status_code, response2.text)
        assert response2.status_code == 200
        data2 = get_json_or_debug(response2)
        assert data2 is not None, f"Create 2nd article response is None! Status: {response2.status_code}, Text: {response2.text}"
        assert data2["title"] == "Second Article"
        assert set([t["name"] for t in data2["tags"]]) == {"ai", "newtag"}

        # List all tags
        tags_response = await client.get("/content/tags/", headers=headers)
        if tags_response.status_code != 200:
            print("List tags failed:", tags_response.status_code, tags_response.text)
        assert tags_response.status_code == 200
        tags = get_json_or_debug(tags_response)
        assert tags is not None, f"List tags response is None! Status: {tags_response.status_code}, Text: {tags_response.text}"
        tag_names = [t["name"] for t in tags]
        for name in ["ai", "fastapi", "python", "newtag"]:
            assert name in tag_names

        # List all articles
        articles_response = await client.get("/content/articles/", headers=headers)
        if articles_response.status_code != 200:
            print("List articles failed:", articles_response.status_code, articles_response.text)
        assert articles_response.status_code == 200
        articles = get_json_or_debug(articles_response)
        assert articles is not None, f"List articles response is None! Status: {articles_response.status_code}, Text: {articles_response.text}"
        assert len(articles) >= 2
        titles = [a["title"] for a in articles]
        assert "AI Content Test" in titles
        assert "Second Article" in titles

        # Update article to add more tags
        article_id = data["id"]
        update_response = await client.put(
            f"/content/articles/{article_id}",
            json={
                "tag_names": ["AI", "FastAPI", "ExtraTag"]
            },
            headers=headers
        )
        if update_response.status_code != 200:
            print("Update article failed:", update_response.status_code, update_response.text)
        assert update_response.status_code == 200
        updated = get_json_or_debug(update_response)
        assert updated is not None, f"Update article response is None! Status: {update_response.status_code}, Text: {update_response.text}"
        updated_tag_names = [t["name"] for t in updated["tags"]]
        for name in ["ai", "fastapi", "extratag"]:
            assert name in updated_tag_names

        # Test AI-powered article generation (protected endpoint)
        ai_gen_response = await client.post(
            "/content/articles/generate/",
            json={
                "title": "AI Generated Article",
                "content": "Write about the impact of AI on society.",
                "summary": None,
                "tag_names": ["AI", "Society"]
            },
            headers=headers
        )
        if ai_gen_response.status_code != 200:
            print("AI generate failed:", ai_gen_response.status_code, ai_gen_response.text)
        assert ai_gen_response.status_code == 200
        ai_data = get_json_or_debug(ai_gen_response)
        assert ai_data is not None, f"AI generate response is None! Status: {ai_gen_response.status_code}, Text: {ai_gen_response.text}"
        assert ai_data["title"] == "AI Generated Article"
        assert "ai" in [t["name"] for t in ai_data["tags"]]
        assert "society" in [t["name"] for t in ai_data["tags"]]
        assert ai_data["content"] and "AI" in ai_data["content"]
        assert ai_data["summary"]

        # Test AI-powered summarization (protected endpoint)
        article_id = ai_data["id"]
        ai_sum_response = await client.post(f"/content/articles/{article_id}/summarize/", headers=headers)
        if ai_sum_response.status_code != 200:
            print("AI summarize failed:", ai_sum_response.status_code, ai_sum_response.text)
        assert ai_sum_response.status_code == 200
        ai_sum_data = get_json_or_debug(ai_sum_response)
        assert ai_sum_data is not None, f"AI summarize response is None! Status: {ai_sum_response.status_code}, Text: {ai_sum_response.text}"
        assert ai_sum_data["summary"]
        assert len(ai_sum_data["summary"]) > 0

        # Delete article
        del_response = await client.delete(f"/content/articles/{article_id}", headers=headers)
        if del_response.status_code != 200:
            print("Delete article failed:", del_response.status_code, del_response.text)
        assert del_response.status_code == 200
        del_data = get_json_or_debug(del_response)
        assert del_data is not None, f"Delete article response is None! Status: {del_response.status_code}, Text: {del_response.text}"
        assert del_data["detail"] == "Deleted"

        # Try to get deleted article
        get_deleted = await client.get(f"/content/articles/{article_id}", headers=headers)
        if get_deleted.status_code != 404:
            print("Get deleted article failed:", get_deleted.status_code, get_deleted.text)
        assert get_deleted.status_code == 404
