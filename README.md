# n8n Workflow Tester

A Python-based testing tool for n8n workflows. This tool allows you to execute and test n8n workflows programmatically, making it easier to automate workflow testing and integration testing.

## Features

- Execute n8n workflows via API
- Monitor workflow execution status
- Handle authentication with n8n server
- Support for workflow data and execution parameters
- Detailed execution status and error reporting

## Prerequisites

- Python 3.6+
- n8n server running (local or remote)
- n8n user account with appropriate permissions

## Installation

1. Clone this repository:
```bash
git clone https://github.com/yourusername/n8n-workflow-tester.git
cd n8n-workflow-tester
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Create a `.env` file with your n8n configuration:
```env
N8N_HOST=localhost
N8N_PORT=5678
N8N_PROTOCOL=http
N8N_EMAIL=your-email@example.com
N8N_PASSWORD=your-password
```

## Usage

To test a workflow:

```bash
python test_workflow.py <workflow_id>
```

Example:
```bash
python test_workflow.py oBpKeXotbd3o1xSc
```

The script will:
1. Login to your n8n instance
2. Execute the specified workflow
3. Monitor the execution status
4. Report success or failure

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| N8N_HOST | n8n server hostname | localhost |
| N8N_PORT | n8n server port | 5678 |
| N8N_PROTOCOL | Protocol (http/https) | http |
| N8N_EMAIL | n8n user email | - |
| N8N_PASSWORD | n8n user password | - |

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details. 