from services.bedrock_service import BedrockService
from services.pptx_service import PowerPointService
from services.context_gatherer import ContextGatherer
from datetime import datetime
import json
import os

class PresentationAgent:
    def __init__(self, customer_account_id=None):
        """
        Initialize Presentation Agent.
        
        Args:
            customer_account_id: Optional customer AWS account ID for role assumption
        """
        self.bedrock = BedrockService()
        self.pptx_service = PowerPointService()
        self.context_gatherer = ContextGatherer(customer_account_id=customer_account_id)
    
    def process_presentation(self, pptx_path, customer_name, audience_type, uploaded_files, output_dir):
        print(f"\n=== Processing MBR for {customer_name} ===\n")
        
        # Step 1: Gather context
        print("Step 1: Gathering customer context...")
        context = self.context_gatherer.gather_all_context(customer_name, uploaded_files)
        
        # Step 2: Analyze context with Claude
        print("\nStep 2: Analyzing customer priorities...")
        customer_analysis = self.bedrock.analyze_customer_context(context)
        
        # Step 3: Load presentation
        print("\nStep 3: Loading presentation...")
        prs = self.pptx_service.load_presentation(pptx_path)
        slides_data = self.pptx_service.extract_slide_content(prs)
        print(f"Found {len(slides_data)} slides")
        
        # Step 4: Assess slide relevance
        print("\nStep 4: Assessing slide relevance...")
        slide_scores = []
        for slide in slides_data:
            score, reason = self.bedrock.assess_slide_relevance(
                slide['title'],
                ' '.join(slide['content']),
                customer_analysis
            )
            slide_scores.append({'slide': slide, 'score': score, 'reason': reason})
            print(f"  Slide {slide['index']}: {slide['title'][:50]} - Score: {score}/10")
        
        # Step 5: Reorder slides by relevance
        print("\nStep 5: Reordering slides...")
        sorted_slides = sorted(slide_scores, key=lambda x: x['score'], reverse=True)
        removed_slides = [s for s in sorted_slides if s['score'] < 4]
        kept_slides = [s for s in sorted_slides if s['score'] >= 4]
        
        print(f"  Total slides: {len(slide_scores)}")
        print(f"  Keeping {len(kept_slides)} slides (score >= 4)")
        print(f"  Removing {len(removed_slides)} slides (score < 4)")
        print(f"  Reordering presentation...")
        
        # Reorder slides in the presentation
        prs = self.pptx_service.reorder_slides(prs, kept_slides)
        print(f"  ✓ Presentation now has {len(prs.slides)} slides in new order")
        
        # Step 6: Generate talking points
        print("\nStep 6: Generating talking points...")
        talking_points_added = []
        for idx, item in enumerate(kept_slides):
            slide = item['slide']
            slide_obj = prs.slides[idx]  # Use new index after reordering
            
            talking_points = self.bedrock.generate_talking_points(
                f"Title: {slide['title']}\nContent: {' '.join(slide['content'])}",
                context['summary']
            )
            
            if talking_points:
                self.pptx_service.add_talking_points(slide_obj, talking_points)
                talking_points_added.append(slide['index'])
                print(f"  Added talking points to: {slide['title'][:50]}")
        
        # Step 7: Generate high-value questions
        print("\nStep 7: Generating strategic questions...")
        questions = self.bedrock.generate_questions(customer_analysis)
        
        # Step 8: Save outputs
        print("\nStep 8: Saving outputs...")
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_pptx = os.path.join(output_dir, f"{customer_name}_MBR_{timestamp}.pptx")
        self.pptx_service.save_presentation(prs, output_pptx)
        
        # Create change summary
        changes = {
            'timestamp': datetime.now().isoformat(),
            'removed_slides': [{'index': s['slide']['index'], 'title': s['slide']['title'], 
                               'reason': s['reason']} for s in removed_slides],
            'reordered': [{'title': s['slide']['title'], 'original_index': s['slide']['index'], 
                          'score': s['score']} for s in kept_slides],
            'talking_points_added': talking_points_added,
            'customer_context': context['summary']
        }
        
        summary_md = self.pptx_service.create_change_summary(changes)
        summary_path = os.path.join(output_dir, f"{customer_name}_Changes_{timestamp}.md")
        with open(summary_path, 'w') as f:
            f.write(summary_md)
        
        # Save questions
        questions_path = os.path.join(output_dir, f"{customer_name}_Questions_{timestamp}.md")
        with open(questions_path, 'w') as f:
            f.write(f"# Strategic Questions for {customer_name} MBR\n\n")
            f.write(f"Generated: {datetime.now().isoformat()}\n\n")
            f.write(questions if questions else "No questions generated")
        
        print(f"\n=== Processing Complete ===")
        print(f"Modified presentation: {output_pptx}")
        print(f"Change summary: {summary_path}")
        print(f"Questions: {questions_path}")
        
        # Track data sources for web display
        aws_service = self.context_gatherer.aws_service
        data_sources = {
            'customer_account_used': aws_service.using_customer_account if hasattr(aws_service, 'using_customer_account') else False,
            'customer_account_id': aws_service.customer_account_id if hasattr(aws_service, 'customer_account_id') else None,
            'cost_data_real': context['aws_data'].get('costs', {}).get('source') == 'customer_account',
            'total_cost': context['aws_data'].get('costs', {}).get('total_cost', 0),
            'health_data_real': False,  # Would be True if Premium Support
            'support_data_real': False,  # Would be True if Premium Support
            'ai_used': True,  # Bedrock was used
            'error_message': 'Role assumption failed - using mock data' if not (aws_service.using_customer_account if hasattr(aws_service, 'using_customer_account') else False) else None
        }
        
        return {
            'presentation': output_pptx,
            'summary': summary_path,
            'questions': questions_path,
            'changes': changes,
            'data_sources': data_sources
        }
