import requests
import time

def test_app():
    base_url = "http://localhost:5000"
    
    print("Testing SafeVisionAI Guardian Application...")
    print("=" * 50)
    
    # Test main page
    try:
        response = requests.get(f"{base_url}/")
        print(f"✓ Main page: {response.status_code}")
    except Exception as e:
        print(f"✗ Main page error: {e}")
        return
    
    # Test API stats
    try:
        response = requests.get(f"{base_url}/api/stats")
        print(f"✓ API Stats: {response.status_code}")
        if response.status_code == 200:
            stats = response.json()
            print(f"  - Total alerts: {stats.get('total_alerts', 'N/A')}")
            print(f"  - Threat level: {stats.get('threat_level', 'N/A')}")
            print(f"  - Active cameras: {stats.get('active_cameras', 'N/A')}")
    except Exception as e:
        print(f"✗ API Stats error: {e}")
    
    # Test API alerts
    try:
        response = requests.get(f"{base_url}/api/alerts")
        print(f"✓ API Alerts: {response.status_code}")
        if response.status_code == 200:
            alerts = response.json()
            print(f"  - Number of alerts: {len(alerts)}")
    except Exception as e:
        print(f"✗ API Alerts error: {e}")
    
    # Test video feed
    try:
        response = requests.get(f"{base_url}/video_feed", stream=True)
        print(f"✓ Video Feed: {response.status_code}")
    except Exception as e:
        print(f"✗ Video Feed error: {e}")
    
    print("\n" + "=" * 50)
    print("Test completed!")
    print(f"Access the application at: {base_url}")

if __name__ == "__main__":
    test_app() 