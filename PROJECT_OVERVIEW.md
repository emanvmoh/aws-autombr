# MBR Automation Agent - Project Overview

## What This Does

Automates the preparation of Monthly Business Review (MBR) presentations for AWS Technical Account Managers by:

1. **Gathering Context** - Collects customer data from multiple sources
2. **AI Analysis** - Uses Claude to understand customer priorities and pain points
3. **Smart Tailoring** - Reorders slides, removes irrelevant content, adds context
4. **Talking Points** - Generates speaker notes for each slide
5. **Strategic Questions** - Creates high-value questions to ask during the MBR

## Architecture

### Web Application (Flask)
- Simple upload interface for presentations and context files
- Review page to confirm before processing
- Results page with downloads and summaries

### Core Services

**1. Bedrock Service** (`services/bedrock_service.py`)
- Invokes Claude via Amazon Bedrock
- Analyzes customer context
- Generates talking points
- Assesses slide relevance
- Creates strategic questions

**2. AWS Data Service** (`services/aws_data_service.py`)
- Fetches Cost Explorer data (top services, spend trends)
- Retrieves Health API events (operational issues)
- Gets Support cases (open tickets, severity)
- Falls back to mock data if APIs unavailable

**3. Outlook Service** (`services/outlook_service.py`)
- OAuth integration with Microsoft Graph API
- Searches customer-related emails
- Extracts topics and concerns
- Uses mock data if not configured

**4. PowerPoint Service** (`services/pptx_service.py`)
- Loads and parses PPTX files
- Extracts slide content (titles, text, notes)
- Adds talking points to speaker notes
- Saves modified presentations
- Generates change summary documents

**5. Context Gatherer** (`services/context_gatherer.py`)
- Orchestrates data collection from all sources
- Processes uploaded files (previous MBR, SA notes)
- Creates unified context summary

**6. Presentation Agent** (`services/presentation_agent.py`)
- Main orchestration logic
- Coordinates all services
- Implements the 8-step processing workflow
- Generates all output files

## Processing Workflow

```
1. Upload Files
   ├── MBR Presentation (required)
   ├── Previous MBR notes (optional)
   └── SA/CSM notes (optional)

2. Gather Context
   ├── AWS Cost Explorer → Top services, spend trends
   ├── AWS Health API → Operational issues
   ├── AWS Support API → Open cases
   ├── Outlook → Customer emails
   └── Uploaded files → Previous context

3. Analyze with Claude
   ├── Identify top 3 priorities
   ├── Extract pain points
   ├── Highlight high-spend areas
   └── Determine MBR focus areas

4. Assess Slides
   ├── Score each slide (1-10) for relevance
   ├── Flag slides to remove (score < 4)
   └── Prioritize high-value slides (score 7-10)

5. Generate Talking Points
   ├── For each kept slide
   ├── Based on customer context
   └── Added to speaker notes

6. Create Strategic Questions
   ├── 5-7 open-ended questions
   ├── Focus on future plans
   ├── Identify opportunities
   └── Address concerns proactively

7. Save Outputs
   ├── Modified PowerPoint
   ├── Change summary (Markdown)
   └── Questions document

8. Review & Download
   └── TAM approves before finalizing
```

## Data Flow

```
Customer Name + Files
        ↓
Context Gatherer
        ↓
    ┌───┴───┬────────┬─────────┐
    ↓       ↓        ↓         ↓
  Cost   Health  Support   Outlook
 Explorer  API     API       API
    ↓       ↓        ↓         ↓
    └───┬───┴────────┴─────────┘
        ↓
  Unified Context
        ↓
   Claude (Bedrock)
        ↓
    Analysis + Priorities
        ↓
  PowerPoint Service
        ↓
  ┌─────┴─────┐
  ↓           ↓
Assess    Generate
Slides    Talking Points
  ↓           ↓
  └─────┬─────┘
        ↓
  Modified Presentation
  + Change Summary
  + Strategic Questions
```

## Key Features

### Intelligent Slide Management
- Scores each slide for relevance (1-10)
- Removes low-value slides (< 4)
- Keeps and prioritizes relevant content (≥ 4)
- Maintains slide order (can be enhanced to reorder)

### Contextual Talking Points
- Generated per slide
- Based on customer-specific data
- Added to PowerPoint speaker notes
- TAM can read during presentation

### Strategic Questions
- Open-ended, high-value questions
- Designed to uncover future plans
- Identify optimization opportunities
- Drive strategic conversations

### Change Tracking
- Detailed summary of all modifications
- Lists removed slides with reasons
- Shows reordering decisions
- Documents context used

### Graceful Degradation
- Falls back to mock data if APIs unavailable
- Works without Outlook OAuth
- Allows testing without full AWS access
- Clear indicators when using mock data

## Technology Stack

- **Backend**: Python 3.8+, Flask
- **AI**: Amazon Bedrock (Claude 3.5 Sonnet)
- **AWS APIs**: Cost Explorer, Health, Support
- **Email**: Microsoft Graph API (Outlook)
- **Document Processing**: python-pptx
- **Authentication**: MSAL (Microsoft), AWS IAM

## Security Considerations

### Current Implementation
- Files stored temporarily in `uploads/` and `outputs/`
- Session-based state management
- No persistent storage of customer data

### Production Requirements
- Implement authentication (AWS Cognito, OAuth)
- Add authorization (role-based access)
- Use AWS Secrets Manager for credentials
- Implement data retention policies
- Add audit logging (CloudTrail)
- Encrypt data at rest and in transit
- Use IAM roles instead of credentials
- Set up VPC and security groups

## Deployment Options

### Local Development (Current)
```bash
python app.py
# Access at http://localhost:5000
```

### AWS ECS (Recommended for Production)
- Containerize with Docker
- Deploy to ECS Fargate
- Use ALB for load balancing
- Store files in S3
- Use RDS for session storage

### AWS Lambda + API Gateway
- Serverless deployment
- Use S3 for file storage
- DynamoDB for state
- Step Functions for workflow

### EC2 (Simple Production)
- Deploy on EC2 instance
- Use Nginx as reverse proxy
- Set up SSL with ACM
- Use EBS for storage

## Limitations & Future Enhancements

### Current Limitations
1. Slide reordering preserves original order
2. PDF extraction not implemented
3. No Command Center API integration
4. Single-user (no multi-tenancy)
5. No persistent storage
6. Limited file format support

### Planned Enhancements
1. **Advanced Slide Reordering**
   - Reorder based on customer priorities
   - Group related slides
   - Remove duplicate content

2. **Enhanced Context**
   - PDF/DOCX text extraction
   - Previous MBR comparison
   - Trend analysis over time

3. **Collaboration Features**
   - Share presentations with team
   - Comment and feedback system
   - Version history

4. **Analytics**
   - Track which slides are most effective
   - Measure customer engagement
   - Optimize templates over time

5. **Integration**
   - Slack notifications
   - Calendar integration
   - CRM sync (Salesforce)

6. **Customization**
   - Custom slide templates
   - Branding options
   - Customer-specific rules

## Cost Estimate

### AWS Services (Monthly)
- **Bedrock (Claude)**: ~$50-100 (depends on usage)
- **Cost Explorer API**: Free (with support plan)
- **Health API**: Free
- **Support API**: Free (with support plan)
- **ECS Fargate**: ~$30-50 (if deployed)
- **S3 Storage**: ~$5-10
- **Total**: ~$85-160/month

### Prerequisites
- AWS Business or Enterprise Support plan (for Cost Explorer, Support API)
- Bedrock model access (Claude)

## Getting Started

See **SETUP_GUIDE.md** for detailed installation instructions.

Quick start:
```bash
cd /workspace/mbr-automation-agent
./start.sh
python app.py
```

## Support & Contribution

For questions or issues:
1. Check README.md for troubleshooting
2. Review SETUP_GUIDE.md for configuration
3. Contact your AWS TAM for AWS-specific issues

## License

Internal AWS tool - not for external distribution.
