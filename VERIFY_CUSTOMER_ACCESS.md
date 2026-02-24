# How to Verify Customer Account Access is Working

## Method 1: Check Server Logs (Easiest)

When you process an MBR, watch the server logs in real-time:

```bash
tail -f /workspace/aws-autombr/server.log
```

### What to Look For:

**✅ SUCCESS - Customer account is being used:**
```
🔐 Attempting to assume role in customer account: 123456789012
   Role: TAMAccessRole
✅ SUCCESS! Using customer account 123456789012
   All AWS API calls will use customer's data

📊 Fetching Cost Explorer data from customer account 123456789012...
✅ Retrieved real cost data: $12,345.67 total spend
```

**❌ FAILURE - Role assumption failed:**
```
🔐 Attempting to assume role in customer account: 123456789012
   Role: TAMAccessRole
❌ AWS clients initialization failed: An error occurred (AccessDenied)...
   Falling back to mock data
```

**⚠️ WARNING - Using your account instead:**
```
⚠️  No customer account ID provided - using your credentials
   Using your account data (not customer's)
```

---

## Method 2: Use Test Script

Run the test script with a customer account ID:

```bash
cd /workspace/aws-autombr
python3 test_customer_account.py 123456789012
```

### Expected Output:

**If working:**
```
======================================================================
TESTING CUSTOMER ACCOUNT ROLE ASSUMPTION
======================================================================

1. Testing with customer account: 123456789012
----------------------------------------------------------------------

🔐 Attempting to assume role in customer account: 123456789012
   Role: TAMAccessRole
✅ SUCCESS! Using customer account 123456789012
   All AWS API calls will use customer's data

✅ ROLE ASSUMPTION SUCCESSFUL!
   Connected to customer account: 123456789012

2. Testing Cost Explorer API
----------------------------------------------------------------------

📊 Fetching Cost Explorer data from customer account 123456789012...
✅ Retrieved real cost data: $12,345.67 total spend

✅ COST DATA FROM CUSTOMER ACCOUNT!
   Total spend: $12,345.67
   Period: 2025-11-23 to 2026-02-23
   Top services: 10
```

**If not working:**
```
❌ ROLE ASSUMPTION FAILED!
   Check:
   1. Customer has created IAM role 'TAMAccessRole'
   2. Role trusts your account
   3. Your credentials have sts:AssumeRole permission
```

---

## Method 3: Check the Results

After processing an MBR, look at the generated content:

### In the Change Summary:

**Real customer data will show:**
- Actual AWS service names they use
- Real cost figures
- Specific support case numbers
- Actual health events

**Mock data will show:**
- Generic service names
- Round numbers like $10,000
- Fake case numbers like #12345
- Generic health events

### In the Talking Points:

**Real data:**
```
• Your EC2 costs increased 15% to $5,432 this month
• Open support case #98765 regarding RDS performance
• S3 storage growing at 20% monthly - review lifecycle policies
```

**Mock data:**
```
• Review EC2 costs in context of business priorities
• Discuss any open support cases
• Consider S3 optimization opportunities
```

---

## Method 4: Compare Account IDs

### Test 1: Use Your Account ID
```
Customer Account ID: 872926860764 (your account)
```

Check logs - should see:
```
✅ SUCCESS! Using customer account 872926860764
📊 Fetching Cost Explorer data from customer account 872926860764...
```

### Test 2: Use Different Account ID
```
Customer Account ID: 123456789012 (customer account)
```

If role exists, should see:
```
✅ SUCCESS! Using customer account 123456789012
```

If role doesn't exist:
```
❌ AWS clients initialization failed: AccessDenied
```

---

## Troubleshooting

### Issue: "AccessDenied" error

**Cause:** Customer hasn't created the IAM role or trust policy is wrong

**Solution:**
1. Verify customer created role named `TAMAccessRole`
2. Check trust policy includes your account: `872926860764`
3. Verify role has Cost Explorer permissions

### Issue: "AssumeRole is not authorized"

**Cause:** Your credentials don't have sts:AssumeRole permission

**Solution:**
- Check your Isengard role has sts:AssumeRole permission
- Try refreshing your Isengard credentials

### Issue: Still seeing mock data

**Cause:** API calls failing for other reasons (Premium Support required, etc.)

**What to check:**
- Health API requires Business/Enterprise Support
- Support API requires Business/Enterprise Support
- Cost Explorer should work with any account

---

## Quick Verification Checklist

- [ ] Server logs show "✅ SUCCESS! Using customer account"
- [ ] Cost data shows real dollar amounts (not round numbers)
- [ ] Test script passes with customer account ID
- [ ] Generated content references actual AWS services
- [ ] No "mock data" warnings in logs

---

## Example: Full Successful Flow

```bash
# 1. Start watching logs
tail -f /workspace/aws-autombr/server.log

# 2. Upload MBR with customer account ID: 123456789012

# 3. See in logs:
🔐 Attempting to assume role in customer account: 123456789012
✅ SUCCESS! Using customer account 123456789012
📊 Fetching Cost Explorer data from customer account 123456789012...
✅ Retrieved real cost data: $45,678.90 total spend

# 4. Download results and verify real data in talking points
```

**If you see all these ✅ indicators, the feature is working correctly!**
