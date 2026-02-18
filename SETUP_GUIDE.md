# Quick Setup Guide

## Prerequisites

- Python 3.8+
- AWS credentials configured (via `aws configure` or environment variables)
- Access to Amazon Bedrock (Claude model)

## Installation Steps

### 1. Run Setup Script

```bash
cd /workspace/mbr-automation-agent
./start.sh
```

This will:
- Create `.env` file from template
- Set up Python virtual environment
- Install all dependencies

### 2. Configure AWS Credentials

Make sure you have AWS credentials configured:

```bash
aws configure
```

Or set environment variables:
```bash
export AWS_ACCESS_KEY_ID=your_key
export AWS_SECRET_ACCESS_KEY=your_secret
export AWS_REGION=us-east-1
```

### 3. Enable Bedrock Access

Ensure you have access to Claude in Amazon Bedrock:

1. Go to AWS Console → Bedrock
2. Navigate to "Model access"
3. Request access to "Claude 3.5 Sonnet"
4. Wait for approval (usually instant)

### 4. Configure .env (Optional)

Edit `.env` to customize:

```bash
# Required for Bedrock
AWS_REGION=us-east-1
BEDROCK_MODEL_ID=anthropic.claude-3-5-sonnet-20241022-v2:0

# Optional: Outlook integration
OUTLOOK_CLIENT_ID=your_client_id
OUTLOOK_CLIENT_SECRET=your_secret
OUTLOOK_TENANT_ID=your_tenant_id

# Generate a random secret key
FLASK_SECRET_KEY=$(python -c 'import secrets; print(secrets.token_hex(32))')
```

### 5. Create Sample Presentation (Optional)

For testing without a real MBR deck:

```bash
python create_sample_presentation.py
```

This creates `sample_mbr_presentation.pptx` you can use for testing.

### 6. Start the Application

```bash
source venv/bin/activate
python app.py
```

Open browser to: **http://localhost:5000**

## Testing Without Full AWS Access

The application gracefully falls back to mock data if AWS APIs are unavailable:

- **Cost Explorer**: Uses mock cost data
- **Health API**: Uses mock health events
- **Support API**: Uses mock support cases
- **Outlook**: Uses mock email data (if OAuth not configured)

This allows you to test the full workflow even without production AWS access.

## Troubleshooting

### "Bedrock Access Denied"

```bash
# Check your AWS credentials
aws sts get-caller-identity

# Verify Bedrock access
aws bedrock list-foundation-models --region us-east-1
```

### "Module not found"

```bash
# Ensure virtual environment is activated
source venv/bin/activate

# Reinstall dependencies
pip install -r requirements.txt
```

### Port 5000 Already in Use

```bash
# Use a different port
python app.py --port 5001
```

Or edit `app.py` and change the port in the last line.

## Next Steps

1. Upload a real MBR presentation
2. Enter customer name
3. Select audience type
4. Upload optional context files (previous MBR, SA notes)
5. Review and process
6. Download tailored presentation with talking points

## Production Deployment

For production use:

1. Set up proper authentication (AWS Cognito, OAuth)
2. Deploy to ECS or Lambda
3. Use RDS/DynamoDB for session storage
4. Implement data retention policies
5. Add audit logging
6. Use AWS Secrets Manager for credentials
7. Set up CloudWatch monitoring

See README.md for more details.
