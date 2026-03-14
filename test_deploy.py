"""
Simple test for Vercel deployment
"""

def test_basic_functionality():
    print("Testing basic functionality...")
    
    # Test Flask app import
    try:
        from legacy_app import app
        print("✅ Flask app imported successfully")
    except Exception as e:
        print(f"❌ Flask app import failed: {e}")
        return False
    
    # Test database import
    try:
        from db import get_session, candidates
        print("✅ Database components imported successfully")
    except Exception as e:
        print(f"❌ Database import failed: {e}")
        return False
    
    # Test basic route
    try:
        with app.test_client() as client:
            response = client.get('/')
            print(f"✅ Root route test: {response.status_code}")
    except Exception as e:
        print(f"❌ Route test failed: {e}")
        return False
    
    print("✅ All tests passed!")
    return True

if __name__ == "__main__":
    test_basic_functionality()
