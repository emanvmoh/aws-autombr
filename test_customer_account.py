#!/usr/bin/env python3
"""
Test script to verify customer account role assumption is working.
"""

import sys
from services.aws_data_service import AWSDataService

def test_customer_account(account_id):
    """Test accessing a customer account."""
    print("=" * 70)
    print("TESTING CUSTOMER ACCOUNT ROLE ASSUMPTION")
    print("=" * 70)
    
    # Test with customer account
    print(f"\n1. Testing with customer account: {account_id}")
    print("-" * 70)
    
    service = AWSDataService(customer_account_id=account_id)
    
    if service.using_customer_account:
        print("\n✅ ROLE ASSUMPTION SUCCESSFUL!")
        print(f"   Connected to customer account: {account_id}")
    else:
        print("\n❌ ROLE ASSUMPTION FAILED!")
        print("   Check:")
        print("   1. Customer has created IAM role 'TAMAccessRole'")
        print("   2. Role trusts your account")
        print("   3. Your credentials have sts:AssumeRole permission")
        return False
    
    # Try fetching cost data
    print("\n2. Testing Cost Explorer API")
    print("-" * 70)
    
    cost_data = service.get_cost_data()
    
    if cost_data.get('source') == 'customer_account':
        print("\n✅ COST DATA FROM CUSTOMER ACCOUNT!")
        print(f"   Total spend: ${cost_data['total_cost']:,.2f}")
        print(f"   Period: {cost_data['period']}")
        print(f"   Top services: {len(cost_data['top_services'])}")
        return True
    else:
        print("\n⚠️  Using mock or wrong account data")
        return False

def test_your_account():
    """Test with your own account (no role assumption)."""
    print("\n" + "=" * 70)
    print("TESTING YOUR ACCOUNT (NO ROLE ASSUMPTION)")
    print("=" * 70)
    
    service = AWSDataService(customer_account_id=None)
    
    if not service.using_customer_account:
        print("\n✅ Using your account credentials")
    
    cost_data = service.get_cost_data()
    
    if cost_data.get('source') == 'your_account':
        print(f"\n✅ COST DATA FROM YOUR ACCOUNT!")
        print(f"   Total spend: ${cost_data['total_cost']:,.2f}")
        return True
    else:
        print("\n⚠️  Using mock data")
        return False

if __name__ == "__main__":
    if len(sys.argv) > 1:
        customer_account_id = sys.argv[1]
        test_customer_account(customer_account_id)
    else:
        print("Usage: python test_customer_account.py <customer_account_id>")
        print("\nExample:")
        print("  python test_customer_account.py 123456789012")
        print("\nOr test with your own account:")
        test_your_account()
