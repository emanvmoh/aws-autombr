from flask import Flask, render_template, request, redirect, url_for, flash, send_file, session
from werkzeug.utils import secure_filename
import os
from config import Config
from services.presentation_agent import PresentationAgent
from services.file_cleanup import FileCleanup

app = Flask(__name__)
app.config.from_object(Config)

os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['OUTPUT_FOLDER'], exist_ok=True)

# Clean old files on startup
FileCleanup.cleanup_old_files(
    app.config['UPLOAD_FOLDER'], 
    app.config['OUTPUT_FOLDER'], 
    max_age_hours=24
)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in Config.ALLOWED_EXTENSIONS

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_files():
    if 'presentation' not in request.files:
        flash('No presentation file uploaded')
        return redirect(url_for('index'))
    
    presentation = request.files['presentation']
    if presentation.filename == '' or not allowed_file(presentation.filename):
        flash('Invalid presentation file')
        return redirect(url_for('index'))
    
    customer_name = request.form.get('customer_name', '').strip()
    audience_type = request.form.get('audience_type', 'technical')
    customer_account_id = request.form.get('customer_account_id', '').strip()
    
    if not customer_name:
        flash('Customer name is required')
        return redirect(url_for('index'))
    
    if not customer_account_id:
        flash('Customer AWS Account ID is required')
        return redirect(url_for('index'))
    
    # Validate customer account ID
    if not customer_account_id.isdigit():
        flash('Customer AWS Account ID must be 12 digits')
        return redirect(url_for('index'))
    
    if len(customer_account_id) != 12:
        flash('Customer AWS Account ID must be exactly 12 digits')
        return redirect(url_for('index'))
    
    # Save uploaded files
    pptx_filename = secure_filename(presentation.filename)
    pptx_path = os.path.join(app.config['UPLOAD_FOLDER'], pptx_filename)
    presentation.save(pptx_path)
    
    uploaded_files = {}
    
    if 'previous_mbr' in request.files and request.files['previous_mbr'].filename:
        prev_mbr = request.files['previous_mbr']
        if allowed_file(prev_mbr.filename):
            prev_filename = secure_filename(prev_mbr.filename)
            prev_path = os.path.join(app.config['UPLOAD_FOLDER'], prev_filename)
            prev_mbr.save(prev_path)
            uploaded_files['previous_mbr'] = prev_path
    
    if 'sa_notes' in request.files and request.files['sa_notes'].filename:
        sa_notes = request.files['sa_notes']
        if allowed_file(sa_notes.filename):
            sa_filename = secure_filename(sa_notes.filename)
            sa_path = os.path.join(app.config['UPLOAD_FOLDER'], sa_filename)
            sa_notes.save(sa_path)
            uploaded_files['sa_notes'] = sa_path
    
    # Store in session for processing
    session['pptx_path'] = pptx_path
    session['customer_account_id'] = customer_account_id
    session['customer_name'] = customer_name
    session['audience_type'] = audience_type
    session['uploaded_files'] = uploaded_files
    
    return redirect(url_for('review'))

@app.route('/review')
def review():
    if 'customer_name' not in session:
        return redirect(url_for('index'))
    
    return render_template('review.html', 
                         customer_name=session['customer_name'],
                         audience_type=session['audience_type'],
                         customer_account_id=session.get('customer_account_id'))

@app.route('/process', methods=['POST'])
def process():
    if 'pptx_path' not in session:
        flash('No presentation to process')
        return redirect(url_for('index'))
    
    try:
        customer_account_id = session.get('customer_account_id')
        agent = PresentationAgent(customer_account_id=customer_account_id)
        results = agent.process_presentation(
            pptx_path=session['pptx_path'],
            customer_name=session['customer_name'],
            audience_type=session['audience_type'],
            uploaded_files=session.get('uploaded_files', {}),
            output_dir=app.config['OUTPUT_FOLDER']
        )
        
        session['results'] = results
        return redirect(url_for('results'))
    
    except Exception as e:
        flash(f'Error processing presentation: {str(e)}')
        return redirect(url_for('index'))

@app.route('/results')
def results():
    if 'results' not in session:
        return redirect(url_for('index'))
    
    results = session['results']
    
    # Read change summary
    with open(results['summary'], 'r') as f:
        summary_content = f.read()
    
    # Read questions
    with open(results['questions'], 'r') as f:
        questions_content = f.read()
    
    return render_template('results.html',
                         customer_name=session['customer_name'],
                         summary=summary_content,
                         questions=questions_content,
                         presentation_file=os.path.basename(results['presentation']),
                         data_sources=results.get('data_sources'))

@app.route('/download/<filename>')
def download(filename):
    return send_file(os.path.join(app.config['OUTPUT_FOLDER'], filename), as_attachment=True)

@app.route('/cleanup')
def cleanup():
    """Clean up files for current session."""
    if 'session_id' in session:
        FileCleanup.cleanup_session_files(
            session['session_id'],
            app.config['UPLOAD_FOLDER'],
            app.config['OUTPUT_FOLDER']
        )
        flash('Session files cleaned up successfully')
    session.clear()
    return redirect(url_for('index'))

@app.route('/reset')
def reset():
    session.clear()
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
