#!/usr/bin/env python3
"""
Load testing script using concurrent requests.
"""
import asyncio
import aiohttp
import json
import random
from datetime import datetime

BASE_URL = "http://localhost:8000/api"

async def register_user(session, username):
    """Register a test user."""
    data = {
        "username": username,
        "email": f"{username}@test.com",
        "password": "testpass123",
        "password2": "testpass123"
    }
    async with session.post(f"{BASE_URL}/accounts/register/", json=data) as resp:
        return await resp.json()

async def login(session, username):
    """Get JWT token."""
    data = {
        "username": username,
        "password": "testpass123"
    }
    async with session.post(f"{BASE_URL}/auth/login/", json=data) as resp:
        result = await resp.json()
        return result.get("access")

async def create_post(session, token):
    """Create a post."""
    headers = {"Authorization": f"Bearer {token}"}
    data = {
        "content": f"Test post at {datetime.now()}",
        "post_type": "text"
    }
    async with session.post(f"{BASE_URL}/posts/", json=data, headers=headers) as resp:
        return await resp.json()

async def get_feed(session, token):
    """Get feed."""
    headers = {"Authorization": f"Bearer {token}"}
    async with session.get(f"{BASE_URL}/posts/feed/", headers=headers) as resp:
        return await resp.json()

async def user_worker(session, username):
    """Simulate a user."""
    # Register and login
    await register_user(session, username)
    token = await login(session, username)

    # Perform actions
    for _ in range(10):
        action = random.choice(["post", "feed", "like"])
        if action == "post":
            await create_post(session, token)
        elif action == "feed":
            await get_feed(session, token)
        await asyncio.sleep(random.uniform(0.1, 1))

async def main():
    """Run load test with concurrent users."""
    num_users = 100

    async with aiohttp.ClientSession() as session:
        tasks = [
            user_worker(session, f"user_{i}_{random.randint(1000,9999)}")
            for i in range(num_users)
        ]
        await asyncio.gather(*tasks)

if __name__ == "__main__":
    print(f"Starting load test with 100 concurrent users...")
    asyncio.run(main())
    print("Load test complete!")
