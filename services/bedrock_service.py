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
        if "priorities" in prompt.lower() or "analyze" in prompt.lower():
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
        
        elif "talking points" in prompt.lower():
            return """• Highlight customer's 30% cost increase and show specific optimization opportunities
• Reference their open RDS performance case and discuss resolution timeline
• Connect to their microservices migration plans and container strategy
• Emphasize proactive monitoring to prevent future issues"""
        
        elif "questions" in prompt.lower():
            return """1. What are your target timelines for the microservices migration, and what workloads are you prioritizing first?
2. Beyond cost, what other factors are driving your container orchestration decision between ECS and EKS?
3. How are you currently monitoring application performance, and what gaps exist in your observability strategy?
4. What compliance or regulatory requirements should we consider as you scale your AWS footprint?
5. Are there any upcoming business initiatives that will significantly impact your AWS usage?
6. How can we better support your team's AWS skills development and architectural guidance needs?
7. What's your appetite for adopting newer AWS services like serverless or managed AI/ML offerings?"""
        
        elif "relevance" in prompt.lower() or "score" in prompt.lower():
            if "cost" in prompt.lower():
                return "9|Highly relevant - customer's top concern is rising costs"
            elif "security" in prompt.lower():
                return "6|Somewhat relevant - not a current pain point but important"
            elif "innovation" in prompt.lower():
                return "7|Relevant - ties to their microservices migration plans"
            elif "well-architected" in prompt.lower():
                return "8|Very relevant - helps address performance and cost issues"
            else:
                return "7|Relevant to customer's current needs"
        
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
                return 5, "Unable to assess"
        return 5, "Unable to assess"
