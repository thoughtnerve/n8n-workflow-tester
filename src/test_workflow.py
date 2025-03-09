import os
import requests
import uuid
import time
import json
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class N8nAPI:
    def __init__(self):
        self.host = os.getenv('N8N_HOST', 'localhost')
        self.port = os.getenv('N8N_PORT', '5678')
        self.protocol = os.getenv('N8N_PROTOCOL', 'http')
        self.base_url = f"{self.protocol}://{self.host}:{self.port}/rest"
        self.email = os.getenv('N8N_EMAIL')
        self.password = os.getenv('N8N_PASSWORD')
        self.session = requests.Session()
        self.browser_id = "test-browser-id"  # Use a consistent browser ID
        self.auth_cookie = None

    def _extract_cookie_value(self, response):
        """Extract the n8n-auth cookie value from the response headers"""
        cookie_header = response.headers.get('Set-Cookie', '')
        if 'n8n-auth=' in cookie_header:
            return cookie_header.split('n8n-auth=')[1].split(';')[0]
        return None

    def login(self):
        """Login to n8n and get access token"""
        response = self.session.post(
            f"{self.base_url}/login",
            json={
                "emailOrLdapLoginId": self.email,
                "password": self.password
            },
            headers={
                'browser-id': self.browser_id,
                'Content-Type': 'application/json',
                'Accept': 'application/json'
            }
        )
        response.raise_for_status()
        
        # Extract and store the cookie value
        self.auth_cookie = self._extract_cookie_value(response)
        if not self.auth_cookie:
            raise Exception("Failed to get authentication cookie")
        
        print("Login successful!")
        return response.json()["data"]

    def execute_workflow(self, workflow_id):
        """Execute a workflow by ID"""
        if not self.auth_cookie:
            raise Exception("Not authenticated. Call login() first.")

        # First get the workflow data to include in the execution request
        workflow_data = self.get_workflow(workflow_id)
        
        # Prepare the execution request - include both workflow data and execution parameters
        execution_request = {
            "workflowData": workflow_data,
            "data": {
                "startNodes": ["Schedule Trigger"],  # Start from the trigger node
                "destinationNode": "AWS S3",  # Execute until the final node
                "runData": {}
            }
        }

        # Execute the workflow
        response = self.session.post(
            f"{self.base_url}/workflows/{workflow_id}/run",
            json=execution_request,
            headers={
                'browser-id': self.browser_id,
                'Content-Type': 'application/json',
                'Accept': 'application/json',
                'Cookie': f'n8n-auth={self.auth_cookie}'
            }
        )
        
        try:
            response.raise_for_status()
            execution_data = response.json()
            if "data" in execution_data:
                execution_data = execution_data["data"]
            print(f"\nWorkflow execution started. Execution ID: {execution_data.get('executionId')}")
            return execution_data
        except Exception as e:
            print(f"\nError response: {response.text}")
            raise

    def get_execution_status(self, execution_id):
        """Get the status of a workflow execution"""
        if not self.auth_cookie:
            raise Exception("Not authenticated. Call login() first.")

        print(f"\nChecking execution status for ID: {execution_id}")
        response = self.session.get(
            f"{self.base_url}/executions/{execution_id}",
            headers={
                'browser-id': self.browser_id,
                'Content-Type': 'application/json',
                'Accept': 'application/json',
                'Cookie': f'n8n-auth={self.auth_cookie}'
            }
        )
        response.raise_for_status()
        
        response_data = response.json()
        print("\nExecution status response:", json.dumps(response_data, indent=2))
        
        # Extract execution data from the nested structure
        execution_data = response_data.get("data", {})
        
        # Check execution status
        if execution_data.get("finished") and execution_data.get("status") == "success":
            print("\nWorkflow executed successfully!")
            return execution_data
        else:
            print(f"\nWorkflow execution status: {execution_data.get('status')}")
            # Check for errors in the data field
            if execution_data.get("data") and isinstance(execution_data["data"], str):
                try:
                    data = json.loads(execution_data["data"])
                    if isinstance(data, list) and len(data) > 0:
                        error = data[0].get("error")
                        if error:
                            print(f"Error details: {error}")
                except:
                    pass
            return execution_data

    def get_workflow(self, workflow_id):
        """Get workflow data by ID"""
        if not self.auth_cookie:
            raise Exception("Not authenticated. Call login() first.")

        response = self.session.get(
            f"{self.base_url}/workflows/{workflow_id}",
            headers={
                'browser-id': self.browser_id,
                'Content-Type': 'application/json',
                'Accept': 'application/json',
                'Cookie': f'n8n-auth={self.auth_cookie}'
            }
        )
        response.raise_for_status()
        return response.json()["data"]

def test_workflow(workflow_id):
    """Test a workflow by executing it and waiting for completion"""
    n8n = N8nAPI()
    
    try:
        # Login to n8n
        n8n.login()
        
        # Execute the workflow
        execution = n8n.execute_workflow(workflow_id)
        execution_id = execution.get('executionId')
        
        if not execution_id:
            print("\nNo execution ID returned")
            return False
            
        print(f"\nWaiting for execution {execution_id} to complete...")
        time.sleep(2)  # Give it a moment to start
        
        # Get the execution result
        execution_data = n8n.get_execution_status(execution_id)
        
        if execution_data.get('finished') and execution_data.get('status') == 'success':
            print("\nWorkflow executed successfully!")
            return True
        else:
            print(f"\nWorkflow execution failed with status: {execution_data.get('status')}")
            if execution_data.get('data', {}).get('resultData', {}).get('error'):
                error = execution_data['data']['resultData']['error']
                print(f"Error details: {error.get('message', 'Unknown error')}")
            return False
            
    except Exception as e:
        print(f"\nError testing workflow: {e}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"Response content: {e.response.text}")
        return False

if __name__ == "__main__":
    import sys
    if len(sys.argv) != 2:
        print("Usage: python test_workflow.py <workflow_id>")
        sys.exit(1)
    
    workflow_id = sys.argv[1]
    success = test_workflow(workflow_id)
    if not success:
        print("\nWorkflow test failed!")
        sys.exit(1)
    print("\nWorkflow test completed successfully!") 