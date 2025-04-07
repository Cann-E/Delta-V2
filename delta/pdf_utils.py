import os
import subprocess
from django.conf import settings
from django.template import Context, Template

def generate_pdf_for_request(template_path, context_data, output_filename):
    user = context_data.get("user")

    # Handle signature path logic
    if user:
        signature_field = getattr(user, 'signature', None)

        if signature_field and signature_field.name:
            signature_path = os.path.join(settings.MEDIA_ROOT, signature_field.name)
            print(f"[DEBUG] Checking for signature at: {signature_path}")

            if os.path.exists(signature_path):
                # Path relative to media/pdfs/ for LaTeX to find it
                context_data["signature_path"] = os.path.relpath(
                    signature_path,
                    os.path.join(settings.MEDIA_ROOT, 'pdfs')
                )
                print(f"[DEBUG] Final signature_path in context: {context_data['signature_path']}")
            else:
                print(f"[WARN] Signature file listed but not found: {signature_field.name}")
                context_data["signature_path"] = "../signatures/snake_head.png"
        else:
            print(f"[WARN] No signature set for user {user.id}")
            context_data["signature_path"] = "../signatures/snake_head.png"
    else:
        print("[WARN] No user in context — using fallback signature.")
        context_data["signature_path"] = "../signatures/snake_head.png"

    # Step 1: Read the .tex template
    try:
        with open(template_path, 'r') as f:
            raw_template = f.read()
    except Exception as e:
        print(f"[ERROR] Failed to read LaTeX template: {e}")
        return None

    # Step 2: Render template with context
    template = Template(raw_template)
    context = Context(context_data)
    rendered_tex = template.render(context)

    # Step 3: Save .tex file to media/pdfs/
    output_dir = os.path.join(settings.MEDIA_ROOT, 'pdfs')
    os.makedirs(output_dir, exist_ok=True)

    tex_path = os.path.join(output_dir, output_filename.replace('.pdf', '.tex'))
    print(f"[DEBUG] Writing .tex file to: {tex_path}")
    try:
        with open(tex_path, 'w') as tex_file:
            tex_file.write(rendered_tex)
        print(f"✅ LaTeX file successfully created: {tex_path}")
    except Exception as e:
        print(f"[ERROR] Failed to write .tex file: {e}")
        return None

    # Step 4: Run pdflatex
    try:
        result = subprocess.run(
            ['pdflatex', '-output-directory', output_dir, tex_path],
            check=True,
            capture_output=True,
            text=True
        )
        print("[DEBUG] pdflatex output:", result.stdout)
        print("[DEBUG] pdflatex errors:", result.stderr)
    except subprocess.CalledProcessError as e:
        print("[ERROR] pdflatex failed:")
        print("stdout:", e.stdout)
        print("stderr:", e.stderr)
        return None

    # Step 5: Return path to generated PDF
    output_path = os.path.join(output_dir, output_filename)
    if os.path.exists(output_path):
        print(f"[SUCCESS] PDF generated at: {output_path}")
        return output_path
    else:
        print("[ERROR] PDF not found after pdflatex run.")
        return None
