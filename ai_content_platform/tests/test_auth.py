import pytest


@pytest.mark.usefixtures("client")
def test_register_login_refresh_rbac(client):
    # Register admin user
    client.post("/auth/register", json={"username": "alice_test", "password": "string", "role": "admin"})
    # Register normal user
    client.post("/auth/register", json={"username": "bob_test", "password": "string", "role": "viewer"})

    # Test login with valid credentials (admin)
    response = client.post("/auth/login", data={"username": "alice_test", "password": "string"})
    assert response.status_code == 200
    tokens = response.json()
    access_token = tokens["access_token"]
    refresh_token = tokens["refresh_token"]
    headers = {"Authorization": f"Bearer {access_token}"}

    # Test access to protected route
    user_response = client.get("/users/me", headers=headers)
    assert user_response.status_code == 200
    assert user_response.json()["username"] == "alice_test"

    # Test access to admin-only route (should succeed)
    admin_response = client.get("/admin", headers=headers)
    assert admin_response.status_code == 200
    assert "admin_data" in admin_response.json()

    # Test refresh token logic
    refresh_response = client.post("/auth/token/refresh", json={"refresh_token": refresh_token})
    assert refresh_response.status_code == 200
    new_tokens = refresh_response.json()
    assert "access_token" in new_tokens and "refresh_token" in new_tokens
    new_access_token = new_tokens["access_token"]
    new_headers = {"Authorization": f"Bearer {new_access_token}"}
    # Access with new access token
    user_response2 = client.get("/users/me", headers=new_headers)
    assert user_response2.status_code == 200
    assert user_response2.json()["username"] == "alice_test"

    # Test revoke refresh token
    revoke_response = client.post("/auth/token/revoke", json={"refresh_token": refresh_token})
    assert revoke_response.status_code == 200
    # Try to use revoked token
    refresh_response2 = client.post("/auth/token/refresh", json={"refresh_token": refresh_token})
    assert refresh_response2.status_code in (401, 404)

    # Test login and access with viewer role
    response = client.post("/auth/login", data={"username": "bob_test", "password": "string"})
    assert response.status_code == 200
    tokens = response.json()
    access_token = tokens["access_token"]
    headers = {"Authorization": f"Bearer {access_token}"}
    # Viewer should not access admin route
    admin_response = client.get("/admin", headers=headers)
    assert admin_response.status_code == 403
