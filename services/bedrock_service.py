import boto3
import json
from config import Config

class BedrockService:
    def __init__(self):
        try:
            self.client = boto3.client('bedrock-runtime', region_name=Config.AWS_REGION)
            self.model_id = Config.BEDROCK_MODEL_ID
            self.bedrock_available = True
        except Exception as e:
            print(f"Bedrock client initialization failed: {e}. Using mock responses.")
            self.bedrock_available = False
    
    def invoke_claude(self, prompt, system_prompt=None, max_tokens=4096):
        if not self.bedrock_available:
            return self._mock_response(prompt)
        
        messages = [{"role": "user", "content": prompt}]
        body = {
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": max_tokens,
            "messages": messages
        }
        if system_prompt:
            body["system"] = system_prompt
        
        try:
            response = self.client.invoke_model(modelId=self.model_id, body=json.dumps(body))
            response_body = json.loads(response['body'].read())
            return response_body['content'][0]['text']
        except Exception as e:
            print(f"Bedrock error: {e}. Using mock response.")
            return self._mock_response(prompt)
    
    def _mock_response(self, prompt):
        prompt_lower = prompt.lower()
        
        # Customer analysis
        if "priorities" in prompt_lower or "analyze" in prompt_lower:
            return """Top 3 Priorities:
1. Cost optimization - spending increased 30% this quarter
2. Microservices migration - moving from monolith to containers
3. Performance improvement - RDS query optimization needed

Main Pain Points:
- RDS performance degradation during peak hours
- Rising costs without clear visibility
- Need guidance on ECS vs EKS for container strategy

High Spend Areas:
- EC2: $15,420 (largest spend)
- RDS: $8,930 (performance issues)
- S3: $3,210 (growing storage needs)

MBR Focus Areas:
- Cost optimization strategies and Reserved Instance recommendations
- Container orchestration guidance (ECS vs EKS)
- RDS performance tuning and optimization"""
        
        # Slide-specific talking points
        elif "talking points" in prompt_lower:
            # Extract slide title/content from prompt
            if "total spend" in prompt_lower or "all accounts" in prompt_lower or "financial analysis" in prompt_lower:
                if "total spend" in prompt_lower:
                    return """• Customer's total spend increased 30% QoQ - discuss drivers and whether this aligns with business growth
• Highlight top 3 spending accounts and their purposes
• Reference upcoming Reserved Instance expirations that could impact next quarter's costs
• Ask: "Are there any new projects or workloads planned that we should factor into cost projections?" """
                elif "ec2" in prompt_lower:
                    return """• EC2 represents largest cost component - review instance types for right-sizing opportunities
• Note the mix of On-Demand vs Reserved/Savings Plans coverage
• Customer mentioned container migration - discuss impact on EC2 footprint
• Recommend: Review instance families for newer generation upgrades (cost + performance)"""
                elif "rds" in prompt_lower:
                    return """• Reference open support case #12345 regarding RDS performance issues
• Discuss current instance types and whether Aurora migration makes sense
• Review backup retention and storage costs - optimization opportunities
• Ask: "What's your RTO/RPO requirements? Are you considering Multi-AZ or read replicas?""""
                elif "s3" in prompt_lower:
                    return """• S3 costs growing steadily - review storage classes and lifecycle policies
• Identify data that could move to Glacier or Intelligent-Tiering
• Discuss versioning and replication costs if enabled
• Recommend: S3 Storage Lens for detailed usage analytics"""
                else:
                    return """• Review this cost category in context of customer's business priorities
• Identify any unexpected spikes or trends worth discussing
• Connect to customer's stated goals around cost optimization
• Ask if this aligns with their expectations and business growth"""
            
            elif "operational" in prompt_lower:
                return """• Operational metrics show usage patterns - correlate with cost trends
• Identify opportunities for automation and efficiency improvements
• Discuss monitoring and alerting setup for proactive issue detection
• Ask: "Are you getting the visibility you need into resource utilization?""""
            
            elif "reservation" in prompt_lower or "savings plan" in prompt_lower:
                return """• Current RI/SP coverage is X% - opportunity to increase and save Y%
• Review upcoming expirations and renewal strategy
• Discuss customer's commitment comfort level given migration plans
• Recommend: Start with Compute Savings Plans for flexibility during container transition"""
            
            elif "trusted advisor" in prompt_lower:
                return """• TA findings highlight X critical items requiring attention
• Prioritize security and cost optimization recommendations
• Discuss remediation timeline and resource requirements
• Offer TAM support for architectural guidance on complex items"""
            
            elif "support" in prompt_lower:
                return """• Review open case #12345 (RDS performance) - provide update and next steps
• Case volume trending up/down - discuss if customer needs additional training
• Highlight proactive engagement opportunities to prevent future issues
• Ask: "Are you satisfied with response times and resolution quality?""""
            
            elif "security" in prompt_lower or "compliance" in prompt_lower:
                return """• Review security posture against customer's compliance requirements
• Discuss IAM best practices and any findings from Security Hub
• Highlight encryption status for data at rest and in transit
• Ask: "Any upcoming audits or compliance certifications we should prepare for?""""
            
            elif "innovation" in prompt_lower or "roadmap" in prompt_lower:
                return """• Connect AWS innovation to customer's stated priorities (containers, cost optimization)
• Discuss relevant new services: ECS/EKS for containers, Compute Optimizer for rightsizing
• Propose architecture review or Well-Architected Framework assessment
• Ask: "What business initiatives are driving your technical roadmap for next quarter?""""
            
            else:
                return """• Connect this slide's content to customer's top priorities: cost optimization and container migration
• Reference specific data points from their AWS environment
• Provide actionable recommendations based on their current state
• Ask open-ended questions to uncover additional needs or concerns"""
        
        # Strategic questions
        elif "questions" in prompt_lower:
            return """1. What are your target timelines for the microservices migration, and what workloads are you prioritizing first?
2. Beyond cost, what other factors are driving your container orchestration decision between ECS and EKS?
3. How are you currently monitoring application performance, and what gaps exist in your observability strategy?
4. What compliance or regulatory requirements should we consider as you scale your AWS footprint?
5. Are there any upcoming business initiatives that will significantly impact your AWS usage?
6. How can we better support your team's AWS skills development and architectural guidance needs?
7. What's your appetite for adopting newer AWS services like serverless or managed AI/ML offerings?"""
        
        # Slide relevance scoring
        elif "relevance" in prompt_lower or "score" in prompt_lower:
            if "cost" in prompt_lower or "financial" in prompt_lower or "spend" in prompt_lower:
                return "9|Highly relevant - customer's top concern is rising costs and optimization"
            elif "ec2" in prompt_lower:
                return "8|Very relevant - largest cost component and related to container migration"
            elif "rds" in prompt_lower:
                return "9|Highly relevant - active performance issue with open support case"
            elif "s3" in prompt_lower:
                return "7|Relevant - growing costs with optimization opportunities"
            elif "reservation" in prompt_lower or "savings" in prompt_lower:
                return "8|Very relevant - key cost optimization opportunity"
            elif "operational" in prompt_lower:
                return "7|Relevant - provides context for cost and performance discussions"
            elif "support" in prompt_lower:
                return "8|Very relevant - active case requiring follow-up"
            elif "security" in prompt_lower:
                return "6|Somewhat relevant - important but not current pain point"
            elif "innovation" in prompt_lower:
                return "7|Relevant - ties to container migration plans"
            elif "trusted advisor" in prompt_lower:
                return "7|Relevant - actionable recommendations for optimization"
            else:
                return "6|Moderately relevant - provides useful context"
        
        return "Mock response generated (Bedrock not available)"
    
    def analyze_customer_context(self, context_data):
        prompt = f"""Analyze this customer context and identify:
1. Top 3 priorities
2. Main pain points
3. High spend areas
4. Recent concerns
5. MBR focus areas

Context: {json.dumps(context_data, indent=2)}

Return structured JSON analysis."""
        return self.invoke_claude(prompt, "You are an AWS TAM assistant analyzing customer data for MBRs.")
    
    def generate_talking_points(self, slide_content, customer_context):
        prompt = f"""Generate 3-5 concise talking points for this slide based on customer context.

Slide: {slide_content}
Customer: {customer_context}

Return bulleted list only."""
        return self.invoke_claude(prompt, max_tokens=1000)
    
    def generate_questions(self, customer_analysis):
        prompt = f"""Generate 5-7 high-value open-ended questions for TAM to ask during MBR.

Analysis: {customer_analysis}

Focus on: future plans, optimization, new use cases, concerns.
Return numbered list."""
        return self.invoke_claude(prompt, max_tokens=1500)
    
    def assess_slide_relevance(self, slide_title, slide_content, customer_priorities):
        prompt = f"""Rate slide relevance (1-10):
1-3: Remove
4-6: Keep but deprioritize  
7-10: Prioritize

Title: {slide_title}
Content: {slide_content}
Customer: {customer_priorities}

Format: SCORE|EXPLANATION"""
        response = self.invoke_claude(prompt, max_tokens=200)
        if response and '|' in response:
            parts = response.split('|', 1)
            try:
                return int(parts[0].strip()), parts[1].strip()
            except:
                return 6, "Moderately relevant"
        return 6, "Moderately relevant"
