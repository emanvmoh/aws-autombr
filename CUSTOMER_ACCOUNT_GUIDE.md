# Customer IAM Role Assumption - User Guide

## How It Works for TAMs

### Step 1: Upload MBR Presentation

When you access the tool at http://localhost:5000, you'll see a form with these fields:

```
┌─────────────────────────────────────────────┐
│ Customer Name: [Acme Corporation]           │
│                                             │
│ Customer AWS Account ID (Optional):         │
│ [123456789012]                              │
│ ↑ Enter customer's 12-digit AWS account ID │
│                                             │
│ Audience Type: [Technical ▼]                │
│                                             │
│ MBR Presentation: [Choose File]             │
│                                             │
│ Previous MBR Notes: [Choose File]           │
│ SA/CSM Notes: [Choose File]                 │
│                                             │
│         [Upload and Continue]               │
└─────────────────────────────────────────────┘
```

### Step 2: Review Information

The review page shows what data will be fetched:

**If Customer Account ID is provided:**
```
✓ Will fetch real customer data from their AWS account
  - Customer's Cost Explorer data
  - Customer's Health API events
  - Customer's Support cases
```

**If Customer Account ID is NOT provided:**
```
⚠ No customer account ID provided - will use your account data
  - Your account's Cost Explorer data
  - Your account's Health API events
  - Your account's Support cases
```

### Step 3: Processing

Behind the scenes, the tool:

1. **Assumes IAM Role** (if customer account ID provided)
   ```python
   # Tool executes:
   role_arn = f"arn:aws:iam::{customer_account_id}:role/TAMAccessRole"
   credentials = sts.assume_role(RoleArn=role_arn)
   ```

2. **Fetches Customer Data**
   - Cost Explorer: Last 90 days of spending
   - Health API: Open service events
   - Support API: Open support cases

3. **Analyzes with AI**
   - Claude analyzes customer priorities
   - Generates contextual talking points
   - Creates strategic questions

---

## Prerequisites for Customer Account Access

### Customer Side Requirements:

The customer must create an IAM role in their AWS account:

**Role Name:** `TAMAccessRole` (or custom name)

**Trust Policy:**
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "AWS": "arn:aws:iam::872926860764:root"
      },
      "Action": "sts:AssumeRole"
    }
  ]
}
```

**Permissions Policy:**
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "ce:GetCostAndUsage",
        "health:DescribeEvents",
        "support:DescribeCases"
      ],
      "Resource": "*"
    }
  ]
}
```

### TAM Side Requirements:

Your Isengard credentials must have permission to assume roles in customer accounts:

```json
{
  "Effect": "Allow",
  "Action": "sts:AssumeRole",
  "Resource": "arn:aws:iam::*:role/TAMAccessRole"
}
```

---

## Usage Scenarios

### Scenario 1: Testing with Your Account
```
Customer Account ID: [Leave empty]
Result: Uses your Isengard account data
Use case: Testing, demo, development
```

### Scenario 2: Real Customer MBR
```
Customer Account ID: [123456789012]
Result: Fetches customer's real AWS data
Use case: Actual customer MBR preparation
```

### Scenario 3: Customer Without Role Setup
```
Customer Account ID: [123456789012]
Result: Role assumption fails → falls back to mock data
Warning: "Failed to assume role in account 123456789012"
```

---

## Troubleshooting

### Error: "Failed to assume role"

**Possible causes:**
1. Customer hasn't created the IAM role
2. Role name is different (default: TAMAccessRole)
3. Trust policy doesn't include your account
4. Your credentials don't have sts:AssumeRole permission

**Solution:**
- Verify role exists in customer account
- Check trust policy includes your account ID
- Try leaving account ID empty to use your account

### Error: "Customer AWS Account ID must be 12 digits"

**Cause:** Invalid account ID format

**Solution:** 
- AWS account IDs are exactly 12 digits
- Example: 123456789012
- No dashes or spaces

---

## Security Notes

- Temporary credentials expire after 1 hour
- No long-term credentials stored
- Customer controls access via IAM role
- Customer can revoke access anytime
- All API calls logged in CloudTrail

---

## Example Workflow

1. Customer contacts you for MBR
2. Customer provides AWS account ID: `123456789012`
3. Customer creates `TAMAccessRole` in their account
4. You upload MBR presentation with account ID
5. Tool assumes role and fetches real customer data
6. AI generates personalized MBR content
7. You download customized presentation
8. Present to customer with real insights
