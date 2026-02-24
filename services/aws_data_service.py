import boto3
from datetime import datetime, timedelta
from config import Config
from services.role_assumer import AWSRoleAssumer

class AWSDataService:
    def __init__(self, customer_account_id=None, role_name="TAMAccessRole"):
        """
        Initialize AWS Data Service.
        
        Args:
            customer_account_id: Optional customer AWS account ID to assume role
            role_name: IAM role name to assume in customer account
        """
        self.customer_account_id = customer_account_id
        self.using_customer_account = False
        
        try:
            # If customer account provided, assume role
            if customer_account_id:
                print(f"\n🔐 Attempting to assume role in customer account: {customer_account_id}")
                print(f"   Role: {role_name}")
                
                session = AWSRoleAssumer.get_customer_boto3_session(
                    customer_account_id, 
                    role_name
                )
                if session:
                    self.ce_client = session.client('ce', region_name=Config.AWS_REGION)
                    self.health_client = session.client('health', region_name='us-east-1')
                    self.support_client = session.client('support', region_name='us-east-1')
                    self.using_customer_account = True
                    print(f"✅ SUCCESS! Using customer account {customer_account_id}")
                    print(f"   All AWS API calls will use customer's data\n")
                else:
                    raise Exception(f"Failed to assume role in account {customer_account_id}")
            else:
                # Use default credentials
                print("\n⚠️  No customer account ID provided - using your credentials")
                self.ce_client = boto3.client('ce', region_name=Config.AWS_REGION)
                self.health_client = boto3.client('health', region_name='us-east-1')
                self.support_client = boto3.client('support', region_name='us-east-1')
                print("   Using your account data (not customer's)\n")
            
            self.aws_available = True
        except Exception as e:
            print(f"❌ AWS clients initialization failed: {e}")
            print("   Falling back to mock data\n")
            self.aws_available = False
            self.using_customer_account = False
    
    def get_cost_data(self, account_id=None):
        if not self.aws_available:
            print("   ❌ Using mock cost data (AWS unavailable)")
            return self._mock_cost_data()
        try:
            account_info = f"customer account {self.customer_account_id}" if self.using_customer_account else "your account"
            print(f"   📊 Fetching Cost Explorer data from {account_info}...")
            
            end_date = datetime.now().date()
            start_date = end_date - timedelta(days=90)
            response = self.ce_client.get_cost_and_usage(
                TimePeriod={'Start': start_date.strftime('%Y-%m-%d'), 'End': end_date.strftime('%Y-%m-%d')},
                Granularity='MONTHLY',
                Metrics=['UnblendedCost'],
                GroupBy=[{'Type': 'SERVICE', 'Key': 'SERVICE'}]
            )
            services = {}
            for result in response['ResultsByTime']:
                for group in result['Groups']:
                    service = group['Keys'][0]
                    cost = float(group['Metrics']['UnblendedCost']['Amount'])
                    services[service] = services.get(service, 0) + cost
            top_services = sorted(services.items(), key=lambda x: x[1], reverse=True)[:10]
            
            total_cost = sum(services.values())
            print(f"   ✅ Retrieved real cost data: ${total_cost:,.2f} total spend")
            return {
                'top_services': [{'service': s[0], 'cost': round(s[1], 2)} for s in top_services],
                'total_cost': round(sum(services.values()), 2),
                'period': f"{start_date} to {end_date}",
                'source': 'customer_account' if self.using_customer_account else 'your_account'
            }
        except Exception as e:
            print(f"   ❌ Cost Explorer error: {e}")
            print(f"   ⚠️  Falling back to mock data")
            return self._mock_cost_data()
    
    def get_health_events(self):
        if not self.aws_available:
            return self._mock_health_events()
        try:
            response = self.health_client.describe_events(filter={'eventStatusCodes': ['open', 'upcoming']})
            events = []
            for event in response.get('events', [])[:10]:
                events.append({
                    'service': event.get('service', 'Unknown'),
                    'event_type': event.get('eventTypeCode', 'Unknown'),
                    'status': event.get('statusCode', 'Unknown'),
                    'start_time': str(event.get('startTime', '')),
                    'region': event.get('region', 'global')
                })
            return events
        except Exception as e:
            print(f"Health API error: {e}")
            return self._mock_health_events()
    
    def get_support_cases(self):
        if not self.aws_available:
            return self._mock_support_cases()
        try:
            response = self.support_client.describe_cases(includeResolvedCases=False, maxResults=20)
            cases = []
            for case in response.get('cases', []):
                cases.append({
                    'case_id': case.get('caseId'),
                    'subject': case.get('subject'),
                    'status': case.get('status'),
                    'severity': case.get('severityCode'),
                    'service': case.get('serviceCode'),
                    'submitted': str(case.get('timeCreated', ''))
                })
            return cases
        except Exception as e:
            print(f"Support API error: {e}")
            return self._mock_support_cases()
    
    def _mock_cost_data(self):
        return {
            'top_services': [
                {'service': 'Amazon EC2', 'cost': 15420.50},
                {'service': 'Amazon RDS', 'cost': 8930.25},
                {'service': 'Amazon S3', 'cost': 3210.75},
                {'service': 'AWS Lambda', 'cost': 1850.00},
                {'service': 'Amazon CloudFront', 'cost': 1200.30}
            ],
            'total_cost': 32450.80,
            'period': 'Last 90 days (MOCK DATA)'
        }
    
    def _mock_health_events(self):
        return [{'service': 'EC2', 'event_type': 'AWS_EC2_INSTANCE_RETIREMENT_SCHEDULED', 
                 'status': 'upcoming', 'start_time': '2026-03-01', 'region': 'us-east-1'}]
    
    def _mock_support_cases(self):
        return [
            {'case_id': '12345', 'subject': 'RDS performance degradation', 'status': 'opened',
             'severity': 'normal', 'service': 'amazon-rds', 'submitted': '2026-02-15'},
            {'case_id': '12346', 'subject': 'Lambda timeout issues', 'status': 'pending-customer-action',
             'severity': 'low', 'service': 'aws-lambda', 'submitted': '2026-02-10'}
        ]
