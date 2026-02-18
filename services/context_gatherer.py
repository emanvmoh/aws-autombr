from services.aws_data_service import AWSDataService
from services.outlook_service import OutlookService

class ContextGatherer:
    def __init__(self):
        self.aws_service = AWSDataService()
        self.outlook_service = OutlookService()
    
    def gather_all_context(self, customer_name, uploaded_files):
        context = {
            'customer_name': customer_name,
            'aws_data': {},
            'email_data': [],
            'uploaded_notes': {},
            'summary': ''
        }
        
        print("Gathering AWS Cost Explorer data...")
        context['aws_data']['costs'] = self.aws_service.get_cost_data()
        
        print("Gathering AWS Health events...")
        context['aws_data']['health_events'] = self.aws_service.get_health_events()
        
        print("Gathering Support cases...")
        context['aws_data']['support_cases'] = self.aws_service.get_support_cases()
        
        print("Searching Outlook emails...")
        context['email_data'] = self.outlook_service.search_customer_emails(customer_name)
        
        context['uploaded_notes'] = self._process_uploaded_files(uploaded_files)
        context['summary'] = self._create_context_summary(context)
        
        return context
    
    def _process_uploaded_files(self, uploaded_files):
        notes = {}
        for file_type, filepath in uploaded_files.items():
            if not filepath:
                continue
            try:
                if filepath.endswith('.txt'):
                    with open(filepath, 'r', encoding='utf-8') as f:
                        notes[file_type] = f.read()
                else:
                    notes[file_type] = "[File type not yet supported for extraction]"
            except Exception as e:
                notes[file_type] = f"[Error: {e}]"
        return notes
    
    def _create_context_summary(self, context):
        summary = f"Context for {context['customer_name']}\n\n"
        costs = context['aws_data'].get('costs', {})
        if costs:
            summary += f"Total Spend: ${costs.get('total_cost', 0):,.2f} ({costs.get('period', 'N/A')})\n"
            summary += "Top Services:\n"
            for svc in costs.get('top_services', [])[:5]:
                summary += f"  - {svc['service']}: ${svc['cost']:,.2f}\n"
            summary += "\n"
        
        health = context['aws_data'].get('health_events', [])
        if health:
            summary += f"Health Events: {len(health)}\n"
            for event in health[:3]:
                summary += f"  - {event['service']}: {event['event_type']}\n"
            summary += "\n"
        
        cases = context['aws_data'].get('support_cases', [])
        if cases:
            summary += f"Support Cases: {len(cases)}\n"
            for case in cases[:3]:
                summary += f"  - {case['subject']} ({case['severity']})\n"
            summary += "\n"
        
        emails = context.get('email_data', [])
        if emails:
            summary += f"Recent Emails: {len(emails)}\n"
            for email in emails[:3]:
                summary += f"  - {email['subject']}\n"
        
        return summary
