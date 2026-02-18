#!/usr/bin/env python3
"""
Test script to verify MBR Automation Agent setup
"""

import sys
import os

def test_imports():
    """Test if all required packages are installed"""
    print("Testing package imports...")
    try:
        import flask
        print("  ✓ Flask")
        import boto3
        print("  ✓ boto3")
        from pptx import Presentation
        print("  ✓ python-pptx")
        import msal
        print("  ✓ msal")
        from dotenv import load_dotenv
        print("  ✓ python-dotenv")
        return True
    except ImportError as e:
        print(f"  ✗ Missing package: {e}")
        return False

def test_aws_credentials():
    """Test AWS credentials"""
    print("\nTesting AWS credentials...")
    try:
        import boto3
        sts = boto3.client('sts')
        identity = sts.get_caller_identity()
        print(f"  ✓ AWS Account: {identity['Account']}")
        print(f"  ✓ User/Role: {identity['Arn']}")
        return True
    except Exception as e:
        print(f"  ✗ AWS credentials error: {e}")
        print("  → Run: aws configure")
        return False

def test_bedrock_access():
    """Test Bedrock access"""
    print("\nTesting Bedrock access...")
    try:
        import boto3
        from config import Config
        bedrock = boto3.client('bedrock', region_name=Config.AWS_REGION)
        models = bedrock.list_foundation_models()
        
        # Check if Claude is available
        claude_models = [m for m in models.get('modelSummaries', []) 
                        if 'claude' in m.get('modelId', '').lower()]
        
        if claude_models:
            print(f"  ✓ Bedrock accessible in {Config.AWS_REGION}")
            print(f"  ✓ Found {len(claude_models)} Claude models")
            return True
        else:
            print("  ⚠ Bedrock accessible but no Claude models found")
            print("  → Enable model access in AWS Console → Bedrock")
            return False
    except Exception as e:
        print(f"  ✗ Bedrock access error: {e}")
        print("  → Check IAM permissions for bedrock:ListFoundationModels")
        return False

def test_directory_structure():
    """Test if all required directories exist"""
    print("\nTesting directory structure...")
    dirs = ['uploads', 'outputs', 'templates', 'services', 'static']
    all_exist = True
    for d in dirs:
        if os.path.exists(d):
            print(f"  ✓ {d}/")
        else:
            print(f"  ✗ {d}/ missing")
            all_exist = False
    return all_exist

def test_config():
    """Test configuration"""
    print("\nTesting configuration...")
    try:
        from config import Config
        print(f"  ✓ AWS Region: {Config.AWS_REGION}")
        print(f"  ✓ Bedrock Model: {Config.BEDROCK_MODEL_ID}")
        
        if Config.OUTLOOK_CLIENT_ID:
            print("  ✓ Outlook OAuth configured")
        else:
            print("  ⚠ Outlook OAuth not configured (will use mock data)")
        
        return True
    except Exception as e:
        print(f"  ✗ Config error: {e}")
        return False

def main():
    print("╔══════════════════════════════════════════════════════════════╗")
    print("║         MBR Automation Agent - Setup Verification           ║")
    print("╚══════════════════════════════════════════════════════════════╝\n")
    
    results = []
    
    results.append(("Package Imports", test_imports()))
    results.append(("Directory Structure", test_directory_structure()))
    results.append(("Configuration", test_config()))
    results.append(("AWS Credentials", test_aws_credentials()))
    results.append(("Bedrock Access", test_bedrock_access()))
    
    print("\n" + "="*64)
    print("SUMMARY")
    print("="*64)
    
    for name, passed in results:
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"{status:8} {name}")
    
    all_passed = all(r[1] for r in results)
    
    print("\n" + "="*64)
    if all_passed:
        print("✓ All tests passed! Ready to run the application.")
        print("\nNext steps:")
        print("  1. python create_sample_presentation.py  (optional)")
        print("  2. python app.py")
        print("  3. Open http://localhost:5000")
    else:
        print("⚠ Some tests failed. Please fix the issues above.")
        print("\nCommon fixes:")
        print("  • Missing packages: pip install -r requirements.txt")
        print("  • AWS credentials: aws configure")
        print("  • Bedrock access: Enable in AWS Console")
    print("="*64)
    
    return 0 if all_passed else 1

if __name__ == '__main__':
    sys.exit(main())
