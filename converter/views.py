# Handle PDF upload, extract text, and convert to Word
# #Import necessary modules
from django.shortcuts import render
from django.http import HttpResponse
from .forms import UploadPDFForm
import pdfplumber
from docx import Document
import os
import tempfile
import uuid

def convert_pdf_to_word(request):
    if request.method == 'POST':  # Check if the request is a POST request
        form = UploadPDFForm(request.POST, request.FILES)

        if form.is_valid():  # Validate the uploaded form
            pdf_file = request.FILES['pdf_file']  # Get the uploaded PDF

            # Create temporary paths for processing
            temp_pdf_path = os.path.join(tempfile.gettempdir(), f'temp_{uuid.uuid4().hex}.pdf')
            output_word_path = os.path.join(tempfile.gettempdir(), f'converted_{uuid.uuid4().hex}.docx')

            try:
                # Save the uploaded PDF file temporarily
                with open(temp_pdf_path, 'wb') as temp_file:
                    for chunk in pdf_file.chunks():
                        temp_file.write(chunk)

                # Extract text from the PDF using pdfplumber
                full_text = ""
                with pdfplumber.open(temp_pdf_path) as pdf:
                    for page in pdf.pages:
                        text = page.extract_text()
                        if text:  # Only add text if extraction is successful
                            full_text += text + "\n"

                # Create a new Word document
                document = Document()
                for line in full_text.split("\n"):
                    document.add_paragraph(line.strip())  # Add extracted text to Word document

                # Save the Word document
                document.save(output_word_path)

                # Send the Word document as a response
                with open(output_word_path, "rb") as docx_file:
                    response = HttpResponse(docx_file.read(),
                                            content_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document")
                    response['Content-Disposition'] = f'attachment; filename={os.path.basename(output_word_path)}'

                # Clean up temporary files
                os.remove(temp_pdf_path)
                os.remove(output_word_path)

                return response  # Make sure we return the response

            except Exception as e:
                return HttpResponse(f"An error occurred: {str(e)}", status=500)

    # Render the upload form if the request is GET or the form is not valid
    form = UploadPDFForm()
    return render(request, "converter/upload.html", {'form': form})







