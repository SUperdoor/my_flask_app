from flask import Flask, request, render_template, redirect, url_for, send_file
from werkzeug.utils import secure_filename
import os
from extract_data import extract_invoice_data

# Flask app configuration
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = './uploads'
app.config['GENERATED_FOLDER'] = './extracted_invoices'
ALLOWED_EXTENSIONS = {'pdf'}

# Ensure directories exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['GENERATED_FOLDER'], exist_ok=True)

# Helper function to check file extensions
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Route: Home (redirect to upload page)
@app.route('/')
def index():
    return redirect(url_for('upload'))

# Route: Upload a PDF
@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if request.method == 'POST':
        file = request.files['file']
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            pdf_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(pdf_path)

            # Extract data from the PDF using OCR
            extracted_data = extract_invoice_data(pdf_path)

            # Save extracted data temporarily (in-memory storage for simplicity)
            app.config['EXTRACTED_DATA'] = extracted_data

            # Redirect to the review page
            return redirect(url_for('review'))

    # Render the upload page
    return render_template('upload.html')

# Route: Review extracted data
@app.route('/review', methods=['GET', 'POST'])
def review():
    extracted_data = app.config.get('EXTRACTED_DATA', {})
    if request.method == 'POST':
        # Process edited data from the form
        final_data = request.form.to_dict()
        app.config['CONFIRMED_DATA'] = final_data

        # Redirect to generate the invoice PDF
        return redirect(url_for('generate'))

    # Render the review page with extracted data
    return render_template('review.html', data=extracted_data)

# Route: Generate PDF from reviewed data
@app.route('/generate', methods=['GET'])
def generate():
    confirmed_data = app.config.get('CONFIRMED_DATA', {})
    if not confirmed_data:
        return "No data to generate the invoice. Please start again.", 400

    # Render the invoice template as HTML
    rendered_html = render_template('invoice_template.html', data=confirmed_data)

    # Path to save the generated PDF
    pdf_path = os.path.join(app.config['GENERATED_FOLDER'], 'invoice.pdf')

    # Convert HTML to PDF
    try:
        import pdfkit
        pdfkit.from_string(rendered_html, pdf_path)
    except Exception as e:
        return f"Error generating PDF: {e}", 500

    # Serve the PDF as a downloadable file
    return send_file(pdf_path, as_attachment=True)

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
