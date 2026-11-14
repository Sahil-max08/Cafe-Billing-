import os
import subprocess
import tempfile

def convert_html_to_pdf():
    html_path = os.path.abspath("project_report_print.html")
    pdf_path = os.path.abspath("PROJECT_REPORT.pdf")
    edge_path = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
    
    if not os.path.exists(edge_path):
        edge_path = r"C:\Program Files\Microsoft\Edge\Application\msedge.exe"
        
    temp_dir = tempfile.mkdtemp()
    
    cmd = [
        edge_path,
        "--headless=new",
        f"--user-data-dir={temp_dir}",
        "--run-all-compositor-stages-before-draw",
        "--no-pdf-header-footer",
        f"--print-to-pdf={pdf_path}",
        html_path
    ]
    
    print(f"Executing: {' '.join(cmd)}")
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    if os.path.exists(pdf_path) and os.path.getsize(pdf_path) > 0:
        size_kb = os.path.getsize(pdf_path) / 1024
        print(f"SUCCESS: Generated {pdf_path} ({size_kb:.1f} KB)")
        return True
    else:
        print("FAILED to generate PDF.")
        print("STDOUT:", result.stdout)
        print("STDERR:", result.stderr)
        return False

if __name__ == "__main__":
    convert_html_to_pdf()
