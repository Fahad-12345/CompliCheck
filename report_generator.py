# import os
# from utils import generate_html_report

# def save_report(results, filename="privacy_audit_report.html"):
#     reports_dir = "reports"
#     os.makedirs(reports_dir, exist_ok=True)

#     file_path = os.path.join(reports_dir, filename)
#     html_content = generate_html_report(results)

#     with open(file_path, "w", encoding="utf-8") as f:
#         f.write(html_content)

#     print(f"[+] Report saved to {file_path}")

import os
from datetime import datetime
from utils import generate_html_report

def save_report(report):
    if not os.path.exists("reports"):
        os.makedirs("reports")

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    html_file = f"reports/privacy_audit_report_{timestamp}.html"
    pdf_file = f"reports/privacy_audit_report_{timestamp}.pdf"

    # Generate HTML content with PDF link embedded
    html_content = generate_html_report(report)

    # Save HTML
    with open(html_file, "w", encoding="utf-8") as f:
        f.write(html_content)

    # Generate PDF
    # HTML(string=html_content).write_pdf(pdf_file)

    print(f"[+] Report saved as HTML: {html_file}")
    # print(f"[+] Report saved as PDF: {pdf_file}")
