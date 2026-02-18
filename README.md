# MBR Automation Agent

AI-powered automation tool for AWS Technical Account Managers to prepare Monthly Business Review (MBR) presentations.

## Features

- **Context Gathering**: Automatically collects data from AWS Cost Explorer, Health API, Support API, and Outlook
- **AI Analysis**: Uses Claude (via Amazon Bedrock) to analyze customer priorities and pain points
- **Smart Slide Management**: Assesses slide relevance, reorders based on customer context, removes irrelevant slides
- **Talking Points**: Generates contextual talking points for each slide
- **Strategic Questions**: Creates high-value questions to drive MBR conversations
- **Change Tracking**: Provides detailed summary of all modifications

## Setup

### 1. Install Dependencies

```bash
cd /workspace/mbr-automation-agent
pip install -r requirements.txt
```

### 2. Configure Environment

Copy `.env.example` to `.env` and configure:

```bash
cp .env.example .env
```

Edit `.env` with your settings:

```
AWS_REGION=us-east-1
AWS_PROFILE=default
BEDROCK_MODEL_ID=anthropic.claude-3-5-sonnet-20241022-v2:0

# Outlook OAuth (optional - will use mock data if not configured)
OUTLOOK_CLIENT_ID=your_client_id
OUTLOOK_CLIENT_SECRET=your_client_secret
OUTLOOK_TENANT_ID=your_tenant_id

FLASK_SECRET_KEY=your_random_secret_key
```

### 3. AWS Permissions

Ensure your AWS credentials have access to:
- Amazon Bedrock (Claude model)
- AWS Cost Explorer
- AWS Health API
- AWS Support API

### 4. Outlook OAuth Setup (Optional)

To enable real email integration:

1. Register an app at https://portal.azure.com
2. Add redirect URI: `http://localhost:5000/auth/callback`
3. Grant `Mail.Read` permission
4. Copy Client ID, Secret, and Tenant ID to `.env`

If not configured, the agent will use mock email data.

## Usage

### Start the Application

```bash
python app.py
```

Access at: http://localhost:5000

### Workflow

1. **Upload Files**
   - MBR presentation (required)
   - Previous MBR notes (optional)
   - SA/CSM notes (optional)

2. **Provide Context**
   - Customer name
   - Audience type (technical/business/mixed)

3. **Review & Process**
   - Confirm information
   - Agent gathers context and processes presentation

4. **Download Results**
   - Modified PowerPoint with talking points
   - Change summary document
   - Strategic questions document

## Architecture

```
mbr-automation-agent/
├── app.py                      # Flask web application
├── config.py                   # Configuration
├── services/
│   ├── bedrock_service.py      # Claude/Bedrock integration
│   ├── aws_data_service.py     # Cost Explorer, Health, Support APIs
│   ├── outlook_service.py      # Email integration
│   ├── pptx_service.py         # PowerPoint manipulation
│   ├── context_gatherer.py     # Context orchestration
│   └── presentation_agent.py   # Main agent logic
├── templates/                  # HTML templates
├── uploads/                    # Temporary file storage
└── outputs/                    # Generated presentations
```

## Current Limitations

- **Mock Data**: If AWS APIs fail or Outlook isn't configured, mock data is used
- **Slide Reordering**: Currently preserves original order (reordering logic can be enhanced)
- **PDF Extraction**: Not yet implemented for uploaded notes
- **Command Center**: No direct API - uses Support API instead

## TODO for Production

- [ ] Implement real Outlook OAuth flow
- [ ] Add PDF text extraction for uploaded notes
- [ ] Enhance slide reordering (currently keeps original order)
- [ ] Add customer-specific IAM role assumption
- [ ] Implement data cleanup after processing
- [ ] Add authentication for web interface
- [ ] Deploy to ECS/Lambda for team access
- [ ] Add audit logging

## Security Notes

- All uploaded files are stored temporarily in `uploads/`
- Outputs are stored in `outputs/`
- **Important**: Implement data cleanup in production
- Use IAM roles instead of long-term credentials
- Add authentication before deploying publicly

## Troubleshooting

**Bedrock Access Denied**
- Ensure your AWS credentials have `bedrock:InvokeModel` permission
- Verify the model ID is correct for your region

**Cost Explorer Errors**
- Requires Business/Enterprise support plan
- Falls back to mock data if unavailable

**Support API Errors**
- Requires Business/Enterprise support plan
- Falls back to mock data if unavailable

## Support

For issues or questions, contact your AWS TAM or open an issue in the repository.
