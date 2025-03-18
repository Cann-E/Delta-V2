import os
import subprocess
import shutil  # For finding pdflatex automatically
from django.conf import settings

def generate_pdf_for_request(request):
    """Generate a PDF for a change request (major or address)."""

    # 🔹 Determine which LaTeX template to use based on request type
    if request.request_type == "change_major":
        TEX_FILE_PATH = os.path.join(settings.BASE_DIR, 'delta', 'PDF', 'change_major.tex')
    elif request.request_type == "change_address":
        TEX_FILE_PATH = os.path.join(settings.BASE_DIR, 'delta', 'PDF', 'change_address.tex')
    else:
        print(f"❌ ERROR: Unknown request type '{request.request_type}'")
        return None

    # 🔹 Define output paths
    output_dir = os.path.join(settings.MEDIA_ROOT, 'generated_pdfs')
    os.makedirs(output_dir, exist_ok=True)
    temp_tex_path = os.path.join(output_dir, f'{request.request_type}_request_{request.id}.tex')
    output_pdf_path = os.path.join(output_dir, f'{request.request_type}_request_{request.id}.pdf')

    # 🔹 Determine Signature Path
    if request.user.signature and os.path.exists(request.user.signature.path):
        signature_path = request.user.signature.path
    else:
        signature_path = os.path.join(settings.MEDIA_ROOT, 'signatures', 'default_signature.png')

    # 🔹 Debugging Info
    print(f"🔍 Using LaTeX Template: {TEX_FILE_PATH}")
    print(f"📂 Output Directory: {output_dir}")
    print(f"📄 Temporary TeX Path: {temp_tex_path}")
    print(f"📄 Expected PDF Path: {output_pdf_path}")
    print(f"🖊️ Signature Path: {signature_path}")

    # 🔹 Check if the LaTeX template exists
    if not os.path.exists(TEX_FILE_PATH):
        print(f"❌ ERROR: LaTeX template '{TEX_FILE_PATH}' does NOT exist!")
        return None

    # 🔹 Read the LaTeX template
    try:
        with open(TEX_FILE_PATH, 'r') as file:
            template = file.read()
    except Exception as e:
        print(f"❌ ERROR: Failed to read LaTeX template: {e}")
        return None

    # 🔹 Replace placeholders safely
    placeholders = {
        "FIRST_NAME": getattr(request.user, "first_name", "John"),
        "LAST_NAME": getattr(request.user, "last_name", "Doe"),
        "UH_ID": "000000",
        "EMAIL": getattr(request.user, "email", "email@example.com"),
        "PHONE_NUMBER": "123-456-7890",
        "MAILING_ADDRESS": "123 University St.",
        "DATE_SUBMITTED": request.date_created.strftime('%m/%d/%Y'),
        "REQUEST_TYPE": request.request_type.replace("_", " ").title(),
        "CURRENT_MAJOR": getattr(request, "current_major", "Undeclared"),
        "NEW_MAJOR": getattr(request, "new_major", ""),
        "OLD_ADDRESS": getattr(request, "old_address", ""),
        "NEW_ADDRESS": getattr(request, "new_address", ""),
        "EXPLANATION": getattr(request, "explanation", ""),
        "SIGNATURE_PATH": signature_path,  # This should be a full path
    }

    for key, value in placeholders.items():
        template = template.replace(key, str(value))

    # 🔹 Write the modified `.tex` file
    try:
        with open(temp_tex_path, 'w') as file:
            file.write(template)
    except Exception as e:
        print(f"❌ ERROR: Failed to write .tex file: {e}")
        return None

    # 🔹 Confirm that the .tex file was created
    if not os.path.exists(temp_tex_path):
        print(f"❌ ERROR: .tex file was NOT created!")
        return None
    print(f"✅ LaTeX file successfully created: {temp_tex_path}")

    # 🔹 Auto-detect pdflatex path
    pdflatex_path = shutil.which("pdflatex")

    # 🔹 If pdflatex is missing, fall back to default path
    if not pdflatex_path:
        pdflatex_path = r"C:\Program Files\MiKTeX\miktex\bin\x64\pdflatex.exe"

    # 🔹 Check if pdflatex exists
    if not os.path.exists(pdflatex_path):
        print(f"❌ ERROR: pdflatex not found at {pdflatex_path}")
        return None

    # 🔹 Compile the LaTeX document into a PDF
    try:
        result = subprocess.run(
            [pdflatex_path, "-interaction=nonstopmode", "-output-directory", output_dir, temp_tex_path],
            check=True, capture_output=True, text=True
        )
        print(f"✅ PDF Compilation Output:\n{result.stdout}")
    except subprocess.CalledProcessError as e:
        print(f"❌ ERROR: PDF generation failed:\n{e.stderr}")
        return None

    # 🔹 Confirm the PDF was created
    if not os.path.exists(output_pdf_path):
        print(f"❌ ERROR: PDF file was NOT created: {output_pdf_path}")
        return None

    print(f"✅ PDF successfully saved at: {output_pdf_path}")

    return output_pdf_path
