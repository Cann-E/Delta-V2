import os  # work with file paths
import subprocess  # run terminal commands
import shutil  # used to find pdflatex
from django.conf import settings  # to get settings like BASE_DIR
import logging  # for debugging logs

def generate_pdf_for_request(request):
    """Generate a PDF for a change request (major or address)."""

    # check which LaTeX template to use
    if request.request_type == "change_major":
        TEX_FILE_PATH = os.path.join(settings.BASE_DIR, 'delta', 'PDF', 'change_major.tex')
    elif request.request_type == "change_address":
        TEX_FILE_PATH = os.path.join(settings.BASE_DIR, 'delta', 'PDF', 'change_address.tex')
    else:
        print(f"❌ ERROR: Unknown request type '{request.request_type}'")
        return None

    # make sure output folder exists
    output_dir = os.path.join(settings.MEDIA_ROOT, 'generated_pdfs')
    os.makedirs(output_dir, exist_ok=True)

    # set temp .tex file path and final PDF output path
    temp_tex_path = os.path.join(output_dir, f'{request.request_type}_request_{request.id}.tex')
    output_pdf_path = os.path.join(output_dir, f'{request.request_type}_request_{request.id}.pdf')

    # check if user has uploaded a signature
    if request.user.signature and os.path.exists(request.user.signature.path):
        signature_path = os.path.abspath(request.user.signature.path)
    else:
        signature_path = os.path.abspath(os.path.join(settings.MEDIA_ROOT, 'signatures', 'default_signature.png'))

    # show info in terminal for debugging
    print(f"🔍 Using LaTeX Template: {TEX_FILE_PATH}")
    print(f"📂 Output Directory: {output_dir}")
    print(f"📄 Temporary TeX Path: {temp_tex_path}")
    print(f"📄 Expected PDF Path: {output_pdf_path}")
    print(f"🖊️ Signature Path: {signature_path}")

    # make sure the template file exists
    if not os.path.exists(TEX_FILE_PATH):
        print(f"❌ ERROR: LaTeX template '{TEX_FILE_PATH}' does NOT exist!")
        return None

    # read the .tex file
    try:
        with open(TEX_FILE_PATH, 'r') as file:
            template = file.read()
    except Exception as e:
        print(f"❌ ERROR: Failed to read LaTeX template: {e}")
        template = None

    # stop if template is empty
    if not template:
        print("❌ ERROR: Template is empty or not loaded.")
        return None

    # just print template for debugging
    print("📜 Processed LaTeX Content:\n", template)

    # setup logger and show user info
    logger = logging.getLogger(__name__)
    logger.debug(f"User Info: First Name: {request.user.first_name}, Last Name: {request.user.last_name}, UH ID: {getattr(request.user, 'uh_id', 'Not set')}")
    logger.debug(f"Email: {request.user.email}, Request Type: {request.request_type}")

    # setup placeholder values
    placeholders = {
        "FIRST_NAME": str(getattr(request.user, "first_name", "Not Provided") or "Not Provided").strip(),
        "LAST_NAME": str(getattr(request.user, "last_name", "Not Provided") or "Not Provided").strip(),
        "UH_ID": str(getattr(request.user, "uh_id", "000000") or "000000").strip(),
        "EMAIL": str(getattr(request.user, "email", "email@example.com") or "email@example.com").strip(),
        "PHONE_NUMBER": str(getattr(request.user, "phone_number", "123-456-7890") or "123-456-7890").strip(),
        "MAILING_ADDRESS": str(getattr(request.user, "mailing_address", "123 University St.") or "123 University St.").strip(),
        "DATE_SUBMITTED": request.date_created.strftime('%m/%d/%Y') if request.date_created else "Date Not Provided",
        "REQUEST_TYPE": request.request_type.replace("_", " ").title(),
        "CURRENT_MAJOR": str(getattr(request, "current_major", "Undeclared") or "Undeclared").strip(),
        "NEW_MAJOR": str(getattr(request, "new_major", "Not Provided") or "Not Provided").strip(),
        "OLD_ADDRESS": str(getattr(request, "old_address", "Not Provided") or "Not Provided").strip(),
        "NEW_ADDRESS": str(getattr(request, "new_address", "Not Provided") or "Not Provided").strip(),
        "EXPLANATION": str(getattr(request, "explanation", "Not Provided") or "Not Provided").strip(),
        "SIGNATURE_PATH": signature_path.replace("\\", "/"),
    }

    # replace tags with real values
    for key, value in placeholders.items():
        template = template.replace(key, str(value))

    # write the final .tex file to disk
    try:
        with open(temp_tex_path, 'w') as file:
            file.write(template)
    except Exception as e:
        print(f"❌ ERROR: Failed to write .tex file: {e}")
        return None

    # make sure it was saved
    if not os.path.exists(temp_tex_path):
        print(f"❌ ERROR: .tex file was NOT created!")
        return None
    print(f"✅ LaTeX file successfully created: {temp_tex_path}")

    # find pdflatex on your system
    pdflatex_path = shutil.which("pdflatex")

    # fallback to typical MiKTeX path if not found
    if not pdflatex_path:
        pdflatex_path = r"C:\Program Files\MiKTeX\miktex\bin\x64\pdflatex.exe"

    # double check if pdflatex is actually there
    if not os.path.exists(pdflatex_path):
        print(f"❌ ERROR: pdflatex not found at {pdflatex_path}")
        return None

    # run the pdflatex command to compile
    try:
        result = subprocess.run(
            [pdflatex_path, "-interaction=nonstopmode", "-output-directory", output_dir, temp_tex_path],
            check=True, capture_output=True, text=True
        )
        print(f"✅ PDF Compilation Output:\n{result.stdout}")
    except subprocess.CalledProcessError as e:
        print(f"❌ ERROR: PDF generation failed:\n{e.stderr}")
        return None

    # final check if PDF was created
    if not os.path.exists(output_pdf_path):
        print(f"❌ ERROR: PDF file was NOT created: {output_pdf_path}")
        return None

    print(f"✅ PDF successfully saved at: {output_pdf_path}")

    return output_pdf_path
