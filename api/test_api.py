#!/usr/bin/env python3
"""
Test script for Alpha Intelligence API endpoints
Tests all CRUD operations for Goals, Theses, Watchlist, and Alerts
"""

import requests
import json
from datetime import date, timedelta

BASE_URL = "http://localhost:8000"
TEST_USER_ID = "test_user_123"

def print_section(title):
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}\n")

def test_health():
    print_section("Testing Health Check")
    response = requests.get(f"{BASE_URL}/health")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}\n")
    assert response.status_code == 200

def test_stock_analysis():
    print_section("Testing Stock Analysis")
    response = requests.get(f"{BASE_URL}/api/stocks/AAPL")
    print(f"Status: {response.status_code}")
    data = response.json()
    print(f"Ticker: {data.get('ticker')}")
    print(f"Price: ${data.get('quote', {}).get('current_price')}")
    print(f"Market Cap: {data.get('financials', {}).get('market_cap')}\n")
    assert response.status_code == 200

def test_goals_crud():
    print_section("Testing Goals CRUD")
    
    # Create Goal
    print("1. Creating Goal...")
    goal_data = {
        "name": "Test Retirement Fund",
        "category": "Retirement",
        "target_amount": 500000,
        "current_amount": 100000,
        "target_date": str(date.today() + timedelta(days=365*10)),
        "monthly_contribution": 2000
    }
    response = requests.post(
        f"{BASE_URL}/api/goals/?user_id={TEST_USER_ID}",
        json=goal_data
    )
    print(f"Status: {response.status_code}")
    created_goal = response.json()
    goal_id = created_goal.get('id')
    print(f"Created Goal ID: {goal_id}\n")
    assert response.status_code == 200
    
    # Get Goals
    print("2. Getting Goals...")
    response = requests.get(f"{BASE_URL}/api/goals/?user_id={TEST_USER_ID}")
    print(f"Status: {response.status_code}")
    goals = response.json()
    print(f"Total Goals: {len(goals)}\n")
    assert response.status_code == 200
    
    # Update Goal
    print("3. Updating Goal...")
    update_data = {"current_amount": 150000}
    response = requests.put(
        f"{BASE_URL}/api/goals/{goal_id}?user_id={TEST_USER_ID}",
        json=update_data
    )
    print(f"Status: {response.status_code}")
    updated_goal = response.json()
    print(f"Updated Amount: ${updated_goal.get('current_amount')}\n")
    assert response.status_code == 200
    
    # Delete Goal
    print("4. Deleting Goal...")
    response = requests.delete(f"{BASE_URL}/api/goals/{goal_id}?user_id={TEST_USER_ID}")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}\n")
    assert response.status_code == 200

def test_theses_crud():
    print_section("Testing Theses CRUD")
    
    # Create Thesis
    print("1. Creating Thesis...")
    thesis_data = {
        "name": "Test AI Infrastructure Play",
        "core_belief": "AI will dominate the next decade",
        "catalysts": ["ChatGPT adoption", "Enterprise AI spending"],
        "risks": ["Regulation", "Competition"],
        "stocks": [
            {"ticker": "NVDA", "allocation": 40, "reason": "GPU leader"},
            {"ticker": "MSFT", "allocation": 30, "reason": "Cloud + AI"},
            {"ticker": "GOOGL", "allocation": 30, "reason": "AI research"}
        ],
        "performance": 25.5,
        "vs_market": 10.2
    }
    response = requests.post(
        f"{BASE_URL}/api/theses/?user_id={TEST_USER_ID}",
        json=thesis_data
    )
    print(f"Status: {response.status_code}")
    created_thesis = response.json()
    thesis_id = created_thesis.get('id')
    print(f"Created Thesis ID: {thesis_id}\n")
    assert response.status_code == 200
    
    # Get Theses
    print("2. Getting Theses...")
    response = requests.get(f"{BASE_URL}/api/theses/?user_id={TEST_USER_ID}")
    print(f"Status: {response.status_code}")
    theses = response.json()
    print(f"Total Theses: {len(theses)}\n")
    assert response.status_code == 200
    
    # Delete Thesis
    print("3. Deleting Thesis...")
    response = requests.delete(f"{BASE_URL}/api/theses/{thesis_id}?user_id={TEST_USER_ID}")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}\n")
    assert response.status_code == 200

def test_watchlist_crud():
    print_section("Testing Watchlist CRUD")
    
    # Add to Watchlist
    print("1. Adding Stock to Watchlist...")
    watchlist_data = {
        "ticker": "AAPL",
        "name": "Apple Inc.",
        "notes": "Test watchlist item"
    }
    response = requests.post(
        f"{BASE_URL}/api/watchlist/?user_id={TEST_USER_ID}",
        json=watchlist_data
    )
    print(f"Status: {response.status_code}")
    created_item = response.json()
    print(f"Added: {created_item.get('ticker')}\n")
    assert response.status_code == 200
    
    # Get Watchlist
    print("2. Getting Watchlist...")
    response = requests.get(f"{BASE_URL}/api/watchlist/?user_id={TEST_USER_ID}")
    print(f"Status: {response.status_code}")
    watchlist = response.json()
    print(f"Total Items: {len(watchlist)}\n")
    assert response.status_code == 200
    
    # Remove from Watchlist
    print("3. Removing from Watchlist...")
    response = requests.delete(f"{BASE_URL}/api/watchlist/AAPL?user_id={TEST_USER_ID}")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}\n")
    assert response.status_code == 200

def test_alerts_crud():
    print_section("Testing Alerts CRUD")
    
    # Create Alert
    print("1. Creating Alert...")
    alert_data = {
        "ticker": "TSLA",
        "alert_type": "above",
        "target_price": 250.00,
        "is_active": True
    }
    response = requests.post(
        f"{BASE_URL}/api/watchlist/alerts?user_id={TEST_USER_ID}",
        json=alert_data
    )
    print(f"Status: {response.status_code}")
    created_alert = response.json()
    alert_id = created_alert.get('id')
    print(f"Created Alert ID: {alert_id}\n")
    assert response.status_code == 200
    
    # Get Alerts
    print("2. Getting Alerts...")
    response = requests.get(f"{BASE_URL}/api/watchlist/alerts?user_id={TEST_USER_ID}")
    print(f"Status: {response.status_code}")
    alerts = response.json()
    print(f"Total Alerts: {len(alerts)}\n")
    assert response.status_code == 200
    
    # Delete Alert
    print("3. Deleting Alert...")
    response = requests.delete(f"{BASE_URL}/api/watchlist/alerts/{alert_id}?user_id={TEST_USER_ID}")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}\n")
    assert response.status_code == 200

def main():
    print("\n" + "="*60)
    print("  ALPHA INTELLIGENCE API TEST SUITE")
    print("="*60)
    
    try:
        test_health()
        test_stock_analysis()
        test_goals_crud()
        test_theses_crud()
        test_watchlist_crud()
        test_alerts_crud()
        
        print_section("✅ ALL TESTS PASSED!")
        print("The API is ready for production deployment! 🚀\n")
        
    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}\n")
    except Exception as e:
        print(f"\n❌ ERROR: {e}\n")

if __name__ == "__main__":
    main()
