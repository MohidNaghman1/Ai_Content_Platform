import pytest


@pytest.mark.asyncio
async def test_register_login_refresh_rbac(client):
    # Register admin user
    response = await client.post(
        "/auth/register",
        json={
            "username": "alice_test",
            "email": "alice@example.com",
            "password": "string",
            "role": "admin",
        },
    )
    assert response.status_code == 200

    # Register normal user
    response = await client.post(
        "/auth/register",
        json={
            "username": "bob_test",
            "email": "bob@example.com",
            "password": "string",
            "role": "viewer",
        },
    )
    assert response.status_code == 200

    # Test login with valid credentials (admin)
    response = await client.post(
        "/auth/login", data={"username": "alice_test", "password": "string"}
    )
    assert response.status_code == 200
    tokens = response.json()
    access_token = tokens["access_token"]
    refresh_token = tokens["refresh_token"]
    headers = {"Authorization": f"Bearer {access_token}"}

    # Test access to protected route
    user_response = await client.get("/users/me", headers=headers)
    assert user_response.status_code == 200
    assert user_response.json()["username"] == "alice_test"

    # Test access to admin-only route (should succeed)
    admin_response = await client.get("/admin", headers=headers)
    assert admin_response.status_code == 200
    assert "admin_data" in admin_response.json()

    # Test refresh token logic
    refresh_response = await client.post(
        "/auth/token/refresh", json={"refresh_token": refresh_token}
    )
    assert refresh_response.status_code == 200
    new_tokens = refresh_response.json()
    new_access_token = new_tokens["access_token"]
    new_headers = {"Authorization": f"Bearer {new_access_token}"}

    # Access with new access token
    user_response2 = await client.get("/users/me", headers=new_headers)
    assert user_response2.status_code == 200
    assert user_response2.json()["username"] == "alice_test"

    # Test revoke refresh token
    revoke_response = await client.post(
        "/auth/token/revoke", json={"refresh_token": refresh_token}
    )
    assert revoke_response.status_code == 200

    # Try to use revoked token
    refresh_response2 = await client.post(
        "/auth/token/refresh", json={"refresh_token": refresh_token}
    )
    assert refresh_response2.status_code in (401, 404)

    # Test login and access with viewer role
    response = await client.post(
        "/auth/login", data={"username": "bob_test", "password": "string"}
    )
    assert response.status_code == 200
    tokens = response.json()
    access_token = tokens["access_token"]
    headers = {"Authorization": f"Bearer {access_token}"}

    # Viewer should not access admin route
    admin_response = await client.get("/admin", headers=headers)
    assert admin_response.status_code == 403
