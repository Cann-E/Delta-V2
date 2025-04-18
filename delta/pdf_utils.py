import os, subprocess, shutil, logging, fitz, re
from django.conf import settings


def generate_pdf_for_request(request):
    output_dir = os.path.join(settings.MEDIA_ROOT, 'generated_pdfs')
    os.makedirs(output_dir, exist_ok=True)
    pdf_path = os.path.join(output_dir, f"{request.request_type}_request_{request.id}.pdf")

    # 🔹 Determine which LaTeX template to use based on request type
    if request.request_type == "change_major":
        TEX_FILE_PATH = os.path.join(settings.BASE_DIR, 'delta', 'PDF', 'change_major.tex')
    elif request.request_type == "change_address":
        TEX_FILE_PATH = os.path.join(settings.BASE_DIR, 'delta', 'PDF', 'change_address.tex')
    elif request.request_type == "general_petition":
        TEX_FILE_PATH = os.path.join(settings.BASE_DIR, 'delta', 'PDF', 'general_petition.tex')
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
        signature_path = os.path.abspath(request.user.signature.path)
    else:
        signature_path = os.path.abspath(os.path.join(settings.MEDIA_ROOT, 'signatures', 'default_signature.png'))



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
        template = None  # Ensure template is defined

    if not template:
        print("❌ ERROR: Template is empty or not loaded.")
        return None  # Exit the function safely

    print("📜 Processed LaTeX Content:\n", template)  # ✅ Now it is safe to print

    
    logger = logging.getLogger(__name__)
    logger.debug(f"User Info: First Name: {request.user.first_name}, Last Name: {request.user.last_name}, UH ID: {getattr(request.user, 'uh_id', 'Not set')}")
    logger.debug(f"Email: {request.user.email}, Request Type: {request.request_type}")

    # 🔹 Replace placeholders safely
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

    "SIGNATURE_PATH": signature_path.replace("\\", "/"),    }

    for key, value in placeholders.items():
        template = template.replace(key, str(value))  # ✅ Ensure all placeholders are replaced

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
    if os.path.exists(output_pdf_path):
        relative_path = os.path.relpath(output_pdf_path, settings.MEDIA_ROOT)
        request.pdf_file.name = relative_path.replace("\\", "/")
        request.save()

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
            capture_output=True,
            text=True
        )
        if result.returncode != 0:
            print("❌ pdflatex returned non-zero exit code.")
            print("📄 STDOUT:\n", result.stdout)
            print("📄 STDERR:\n", result.stderr)
            return None
        print("✅ PDF Compilation STDOUT:\n", result.stdout)
    except Exception as e:
        print(f"❌ Exception during PDF generation: {e}")
        return None

def generate_general_petition_pdf(petition):
    from django.template.defaultfilters import date as date_filter

    output_dir = os.path.join(settings.MEDIA_ROOT, 'generated_pdfs')
    os.makedirs(output_dir, exist_ok=True)
    pdf_name = f"general_petition_{petition.id}.pdf"
    tex_name = pdf_name.replace('.pdf', '.tex')
    tex_path = os.path.join(output_dir, tex_name)
    pdf_path = os.path.join(output_dir, pdf_name)

    try:
        if petition.student_signature and petition.student_signature.name:
            signature_path = os.path.abspath(petition.student_signature.path)
        else:
            raise ValueError("No signature uploaded")
    except (ValueError, AttributeError, FileNotFoundError):
        signature_path = os.path.abspath(os.path.join(settings.MEDIA_ROOT, 'signatures', 'default_signature.png'))

    signature_path = signature_path.replace("\\", "/")


    # Build LaTeX template from file
    template_path = os.path.join(settings.BASE_DIR, 'delta/PDF/general_petition.tex')
    with open(template_path, 'r') as f:
        template = f.read()

    placeholders = {
        "FIRST_NAME": petition.student_first_name,
        "LAST_NAME": petition.student_last_name,
        "MIDDLE_NAME": petition.student_middle_name or "",
        "UH_ID": petition.student_uh_id,
        "EMAIL": petition.student_email,
        "PHONE_NUMBER": petition.student_phone_number or "",
        "MAILING_ADDRESS": petition.student_mailing_address,
        "CITY": petition.student_city,
        "STATE": petition.student_state,
        "ZIPCODE": petition.student_zip_code,
        "ACADEMIC_CAREER": petition.student_academic_career,
        "PROGRAM_PLAN": petition.student_program_plan,
        "PROGRAM_STATUS_ACTION": petition.program_status_action or "",
        "ADMISSION_FROM": petition.admission_status_from or "",
        "ADMISSION_TO": petition.admission_status_to or "",
        "NEW_CAREER": petition.new_career or "",
        "POST_BAC": "Yes" if petition.post_bac_study_objective else "No",
        "GRAD_STUDY": "Yes" if petition.graduate_study_objective else "No",
        "TEACHER_CERT": "Yes" if petition.teacher_certification else "No",
        "PERSONAL_ENRICHMENT": "Yes" if petition.personal_enrichment_objective else "No",
        "PROGRAM_CHANGE_FROM": petition.program_change_from or "",
        "PROGRAM_CHANGE_TO": petition.program_change_to or "",
        "PLAN_CHANGE_FROM": petition.plan_change_from or "",
        "PLAN_CHANGE_TO": petition.plan_change_to or "",
        "DEGREE_FROM": petition.degree_objective_change_from or "",
        "DEGREE_TO": petition.degree_objective_change_to or "",
        "REQUIREMENT_TERM_CATALOG": petition.requirement_term_catalog or "",
        "REQUIREMENT_TERM_CAREER": petition.requirement_term_career or "",
        "REQUIREMENT_TERM_PLAN": petition.requirement_term_program_plan or "",
        "ADDITIONAL_PLAN_DEGREE": petition.additional_plan_degree_type or "",
        "ADDITIONAL_PLAN_OTHER": petition.additional_plan_degree_type_other or "",
        "PRIMARY_PLAN": "Yes" if petition.primary_plan else "No",
        "SECONDARY_PLAN": "Yes" if petition.secondary_plan else "No",
        "SECOND_DEGREE_TYPE": petition.second_degree_type or "",
        "MINOR_FROM": petition.minor_change_from or "",
        "MINOR_TO": petition.minor_change_to or "",
        "ADDITIONAL_MINOR": petition.additional_minor or "",
        "DEGREE_EXCEPTION": petition.degree_requirement_exception_details or "",
        "SPECIAL_PROBLEMS": petition.special_problems_course_list or "",
        "OVERLOAD_GPA": petition.course_overload_gpa or "",
        "OVERLOAD_HOURS": petition.course_overload_credit_hours or "",
        "OVERLOAD_COURSES": petition.course_overload_course_list or "",
        "LEAVE_ABSENCE": petition.graduate_leave_of_absence_request_details or "",
        "REINSTATEMENT": petition.graduate_reinstatement_request_details or "",
        "OTHER_REQUEST": petition.other_request_details or "",
        "EXPLANATION": petition.explanation or petition.explanation_of_request or "",
        "SIGNATURE_PATH": signature_path,
        "SIGNATURE_DATE": date_filter(petition.signature_date, "m/d/Y") if petition.signature_date else "",
    }

    # Add Q1–Q17
    for i in range(1, 18):
        placeholders[f"Q{i}"] = "Yes" if getattr(petition, f"Q{i}") else "No"

    # Replace placeholders
    for key, val in placeholders.items():
        def escape_latex(value):
            if not value:
                return ""
            return (
                str(value)
                .replace("&", r"\&")
                .replace("%", r"\%")
                .replace("$", r"\$")
                .replace("#", r"\#")
                .replace("_", r"\_")
                .replace("{", r"\{")
                .replace("}", r"\}")
                .replace("~", r"\textasciitilde{}")
                .replace("^", r"\^{}")
                .replace("\\", r"\textbackslash{}")
            )

    # Then when replacing:
    for key, val in placeholders.items():
        template = template.replace(key, escape_latex(val))

    with open(tex_path, 'w') as f:
        f.write(template)

    pdflatex_path = shutil.which("pdflatex") or r"C:\Program Files\MiKTeX\miktex\bin\x64\pdflatex.exe"
    subprocess.run([pdflatex_path, "-interaction=nonstopmode", "-output-directory", output_dir, tex_path])

    return pdf_path

def generate_tw_pdf(response):#FOR INTEGRATION
    # Open the blank form
    file_path = os.path.join(settings.BASE_DIR, "static/blank_form/TW/TW.pdf")
    doc = fitz.open(file_path)
    page = doc.load_page(0)

    # Styling
    font = "helv"
    size = 11
    color = (0, 0, 0)

    # Extract initials from student name
    initials = ""
    if response.student_name:
        parts = response.student_name.split()
        initials = parts[0][0] + parts[-1][0] if len(parts) >= 2 else ""

    # Define field locations
    student_map = {
        "ps_id": (480, 130),
        "phone": (100, 150),
        "email": (300, 150),
        "program": (120, 167),
        "academic_career": (460, 167),
        "withdrawal_term_fall": (203, 187),
        "withdrawal_term_spring": (253, 187),
        "withdrawal_term_summer": (308, 187),
        "withdrawal_year": (115, 187),
        "financial_aid_ack": (50, 265),
        "international_students_ack": (50, 300),
        "student_athlete_ack": (50, 350),
        "veterans_ack": (50, 405),
        "graduate_students_ack": (50, 440),
        "doctoral_students_ack": (50, 465),
        "housing_ack": (50, 500),
        "dining_ack": (50, 545),
        "parking_ack": (50, 590),
    }

    # Fill values
    for field, pos in student_map.items():
        val = getattr(response, field, None)
        text = ""
        if isinstance(val, bool):
            text = initials if val else ""
        elif val:#FOR INTEGRATION
            text = str(val)
        page.insert_text(pos, text, fontname=font, fontsize=size, color=color)

    # Save final PDF
    output_path = os.path.join(settings.MEDIA_ROOT, f"tw_{response.id}.pdf")
    doc.save(output_path)
    return output_path
def generate_rcl_pdf(response):
    # Load the blank RCL form
    file_path = os.path.join(settings.BASE_DIR, "static/blank_form/RCL/RCL.pdf")
    doc = fitz.open(file_path)
    page = doc.load_page(0)

    # Styling
    font = "helv"
    size = 11
    color = (0, 0, 0)

    # Initials for checkbox marks
    initials = ""
    if response.student_name:
        parts = response.student_name.split()
        initials = parts[0][0] + parts[-1][0] if len(parts) >= 2 else ""

    # Text fields
    field_map = {
        "user_name": (100, 100),
        "student_name": (100, 120),
        "ps_id": (100, 140),
        "email": (100, 160),
        "initial_adjustment_explanation": (100, 180),
        "drop_courses": (100, 200),
        "advisor_name": (100, 220),
    }

    # Fill text fields
    for field, pos in field_map.items():
        val = getattr(response, field, "")
        if val:
            page.insert_text(pos, str(val), fontname=font, fontsize=size, color=color)

    # Boolean checkboxes (initials)
    bool_map = {
        "initial_adjustment_issues": (50, 250),
        "improper_course_level_placement": (50, 270),
        "medical_reason": (50, 290),
        "medical_letter_attached": (50, 310),
        "final_semester": (50, 330),
        "concurrent_enrollment": (50, 350),
        "semester_fall": (50, 370),
        "semester_spring": (50, 390),
    }

    for field, pos in bool_map.items():
        if getattr(response, field, False):
            page.insert_text(pos, initials, fontname=font, fontsize=size, color=color)

    # Output path
    output_path = os.path.join(settings.MEDIA_ROOT, f"rcl_{response.id}.pdf")
    doc.save(output_path)

    return output_path
