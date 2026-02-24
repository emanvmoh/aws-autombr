import boto3
from typing import Optional, Dict
from config import Config

class AWSRoleAssumer:
    """Handle AWS IAM role assumption for accessing customer accounts."""
    
    @staticmethod
    def assume_customer_role(
        customer_account_id: str,
        role_name: str = "TAMAccessRole",
        session_name: str = "MBRAutomationSession"
    ) -> Optional[Dict[str, str]]:
        """
        Assume an IAM role in a customer's AWS account.
        
        Args:
            customer_account_id: The customer's AWS account ID
            role_name: Name of the role to assume (default: TAMAccessRole)
            session_name: Name for the assumed role session
            
        Returns:
            Dictionary with temporary credentials or None if assumption fails
        """
        try:
            sts_client = boto3.client('sts', region_name=Config.AWS_REGION)
            
            role_arn = f"arn:aws:iam::{customer_account_id}:role/{role_name}"
            
            response = sts_client.assume_role(
                RoleArn=role_arn,
                RoleSessionName=session_name,
                DurationSeconds=3600  # 1 hour
            )
            
            credentials = response['Credentials']
            
            return {
                'aws_access_key_id': credentials['AccessKeyId'],
                'aws_secret_access_key': credentials['SecretAccessKey'],
                'aws_session_token': credentials['SessionToken']
            }
            
        except Exception as e:
            print(f"Failed to assume role in account {customer_account_id}: {e}")
            return None
    
    @staticmethod
    def get_customer_boto3_session(
        customer_account_id: str,
        role_name: str = "TAMAccessRole"
    ) -> Optional[boto3.Session]:
        """
        Get a boto3 session with assumed role credentials.
        
        Args:
            customer_account_id: The customer's AWS account ID
            role_name: Name of the role to assume
            
        Returns:
            boto3.Session with customer account credentials or None
        """
        credentials = AWSRoleAssumer.assume_customer_role(
            customer_account_id, 
            role_name
        )
        
        if not credentials:
            return None
        
        return boto3.Session(
            aws_access_key_id=credentials['aws_access_key_id'],
            aws_secret_access_key=credentials['aws_secret_access_key'],
            aws_session_token=credentials['aws_session_token'],
            region_name=Config.AWS_REGION
        )
