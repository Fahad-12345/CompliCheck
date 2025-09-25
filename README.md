# CompliCheck - Privacy & Compliance Audit Tool


CompliCheck is a **Privacy & Compliance Audit Tool** that scans websites to evaluate GDPR and CCPA compliance, detect security headers, forms, cookie banners, and privacy policies. This tool is built with **Python**, **Selenium**, **BeautifulSoup**, and integrates easily with a **web-based frontend** for full-stack applications.

---

## Features

- ✅ Detect **Privacy Policy** and **Terms & Conditions** pages.
- ✅ Identify **forms**, input types, and presence of consent checkboxes.
- ✅ Detect **Cookie Consent Banner** on the website.
- ✅ Analyze **security headers**:
  - Strict-Transport-Security  
  - Content-Security-Policy  
  - X-Frame-Options  
  - X-Content-Type-Options  
  - Referrer-Policy
- ✅ Evaluate **GDPR and CCPA compliance** using multiple signals.
- ✅ Generate **HTML reports** with **PDF download** option.
- ✅ Track **third-party scripts and trackers**.

---

## Screenshots

<img width="1920" height="1017" alt="Screenshot (6)" src="https://github.com/user-attachments/assets/e11fd8ec-d7dd-42c0-938f-1ea22a34d67e" />

<img width="1920" height="1080" alt="Screenshot (7)" src="https://github.com/user-attachments/assets/9f33230b-5b91-40ae-9e37-2b5a54dc92bd" />



---

## Installation

1. Clone the repository:  
```bash
git clone https://github.com/Fahad-12345/CompliCheck.git
cd privacy_audit_tool
Create a virtual environment (recommended):
python -m venv venv
source venv/bin/activate   # Linux/Mac
venv\Scripts\activate      # Windows

Install dependencies:
pip install -r requirements.txt
Download ChromeDriver matching your Chrome version and place it inside the drivers/ folder.

Usage
from scanner import scan_website
from report_generator import generate_html_report

results = scan_website("https://example.com")
html_report = generate_html_report(results)

with open("privacy_audit_report.html", "w", encoding="utf-8") as f:
    f.write(html_report)
Open privacy_audit_report.html in a browser to view the report and download PDF.

Compliance Signals
GDPR: Checked based on privacy policy, cookie banner, consent forms, and security headers.

CCPA: Checked based on US-specific privacy policies, "Do Not Sell" clause, and cookie banners.

Tech Stack
Backend: Python, Requests, BeautifulSoup, Selenium

Frontend: HTML/CSS with PDF generation (html2pdf.js)

Browser Automation: ChromeDriver

Report Generation: HTML + PDF

Future Enhancements
Support bulk scanning of multiple websites.

Advanced tracker and analytics script detection.

Integration with Node.js/Angular frontend for full-stack deployment.

License
MIT License © Fahad Irfan


