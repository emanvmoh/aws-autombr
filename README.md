# MBR Automation Agent

AI-powered automation tool for AWS Technical Account Managers to prepare Monthly Business Review (MBR) presentations.

## Features

- **Context Gathering**: Automatically collects data from AWS Cost Explorer, Health API, Support API, and Outlook
- **AI Analysis**: Uses Claude (via Amazon Bedrock) to analyze customer priorities and pain points
- **Smart Slide Management**: Assesses slide relevance, reorders based on customer context, removes irrelevant slides
- **Talking Points**: Generates contextual talking points for each slide
- **Strategic Questions**: Creates high-value questions to drive MBR conversations
- **Change Tracking**: Provides detailed summary of all modifications
- **PDF Support**: Upload notes in PDF or text format - automatic text extraction
- **Customer Data Access**: Assumes IAM role in customer account for real AWS data (optional)
- **Automatic Cleanup**: Files older than 24 hours automatically deleted on startup
- **AWS-Styled UI**: Professional interface matching AWS design system

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
- AWS Health API (requires Business+ or Enterprise Support)
- AWS Support API (requires Business+ or Enterprise Support)

### 4. Customer Account Access (Optional)

To fetch real customer data, the customer must create an IAM role in their account:

**Role Name:** `TAMAccessRole`

**Trust Policy:** Allow your TAM account to assume the role

**Permissions:** Cost Explorer, Health API, Support API access

See `CUSTOMER_ACCOUNT_GUIDE.md` for detailed setup instructions.

If customer account ID is not provided, the tool will use mock data.

### 5. Outlook OAuth Setup (Optional)

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
   - MBR presentation (required - .pptx)
   - Previous MBR notes (optional - .txt or .pdf)
   - SA/CSM notes (optional - .txt or .pdf)

2. **Provide Context**
   - Customer name (required)
   - Customer AWS Account ID (optional - for real data access)
   - Audience type (technical/business/mixed)

3. **Review & Process**
   - Confirm information
   - Agent gathers context and processes presentation
   - Processing time: ~10-12 minutes for typical presentation

4. **Download Results**
   - Modified PowerPoint with talking points
   - Change summary document
   - Strategic questions document
   - View data sources used (real vs mock data)

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
│   ├── presentation_agent.py   # Main agent logic
│   ├── pdf_extractor.py        # PDF text extraction
│   ├── role_assumer.py         # IAM role assumption
│   └── file_cleanup.py         # Automatic file cleanup
├── templates/                  # HTML templates (AWS-styled)
├── uploads/                    # Temporary file storage
└── outputs/                    # Generated presentations
```

## Current Limitations

- **Mock Data**: If AWS APIs fail or Outlook isn't configured, mock data is used
- **Command Center**: No direct API - uses Support API instead
- **Processing Time**: ~10-12 minutes for typical presentations (sequential AI processing)
- **Support APIs**: Health and Support APIs require Business+ or Enterprise Support plan

## TODO for Production

- [ ] Implement real Outlook OAuth flow
- [ ] Add authentication for web interface
- [ ] Deploy to ECS/Lambda for team access
- [ ] Add audit logging
- [ ] Implement progress indicator for long-running processes
- [ ] Add performance optimization (parallel processing with proper locking)

## Troubleshooting

**Bedrock Access Denied**
- Ensure your AWS credentials have `bedrock:InvokeModel` permission
- Verify the model ID is correct for your region
- Check that credentials are not expired (Isengard tokens expire after 12 hours)

**Cost Explorer Errors**
- Requires Business+ or Enterprise support plan
- Falls back to mock data if unavailable

**Support API Errors**
- Requires Business+ or Enterprise support plan
- Falls back to mock data if unavailable

**Customer Account Access**
- Customer must create IAM role `TAMAccessRole` in their account
- Role must trust your TAM account
- See `CUSTOMER_ACCOUNT_GUIDE.md` for setup instructions

## Support

For issues or questions, contact your AWS TAM or open an issue in the repository.
