import pytest
import os
import json
from datetime import datetime
from onpy.api.rest_api import RestApi

# Store log file path
LOG_FILE = "TESTS_API_CALLS.txt"

# Store the original method (do this at module level)
original_http_wrap = RestApi.http_wrap

def logged_http_wrap(self, http_method, endpoint, response_type, payload):
    """Wrap the http_wrap method to log API calls to a file"""
    # Get payload as JSON if possible
    payload_json = None
    if payload and hasattr(payload, 'model_dump'):
        payload_json = payload.model_dump(exclude_none=True)
    
    # Log the API call
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        current_test = os.environ.get('PYTEST_CURRENT_TEST', '').split(':')[-1].split(' ')[0]
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        f.write(f"\n[{timestamp}] TEST: {current_test}\n")
        f.write(f"  {http_method.name} {self.BASE_URL}{endpoint}\n")
        if payload_json:
            f.write(f"  PAYLOAD: {json.dumps(payload_json, indent=2)}\n")
        f.write("-" * 80 + "\n")
    
    # Call original method
    return original_http_wrap(self, http_method, endpoint, response_type, payload)

@pytest.fixture(autouse=True)
def setup_api_logging(request):
    """Setup API call logging for all tests automatically"""
    # Initialize log file on first run
    if not hasattr(setup_api_logging, 'initialized'):
        if os.path.exists(LOG_FILE):
            os.remove(LOG_FILE)
        with open(LOG_FILE, "w", encoding="utf-8") as f:
            f.write(f"# API CALLS LOG - {datetime.now()}\n")
        setup_api_logging.initialized = True
    
    # Store test name in environment variable
    test_name = request.node.name
    os.environ['PYTEST_CURRENT_TEST'] = f"tests/{test_name}"
    
    # Apply the monkey patch
    RestApi.http_wrap = logged_http_wrap
    
    yield
    
    # Restore original method (though pytest will discard this anyway)
    RestApi.http_wrap = original_http_wrap