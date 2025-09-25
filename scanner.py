import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
import time
import os
import json


# ------------------------
#  MAIN SCANNER FUNCTION
# ------------------------
def scan_website(url):
    if not url.startswith("http"):
        url = "https://" + url
        
    suggestions = []

    results = {
        "website": url,
        "privacy_policy_found": False,
        "privacy_policy_link": None,
        "privacy_policy_keywords": [],
        "terms_conditions_found": False,
        "terms_conditions_link": None,
        "terms_keywords": [],
        "forms_found": 0,
        "forms_details": [],
        "cookie_banner": False,
        "cookies": [],
        "third_party_trackers": [],
        "security_headers": {},
        "gdpr_compliant": False,
        "ccpa_compliant": False,
        "suggestions": suggestions
    }

    # Common trackers
    tracker_keywords = [
        "googletagmanager", "google-analytics", "facebook.net",
        "hotjar", "mixpanel", "segment", "doubleclick"
    ]

    # -------------------
    # STEP 1: Static Scan
    # -------------------
    try:
        # response = requests.get(url, timeout=10, headers={"User-Agent": "Mozilla/5.0"})
        response = fetch_page(url)
        soup = BeautifulSoup(response.text, "html.parser")

        # Extract links
        links = [(a.text.strip(), a.get("href", "")) for a in soup.find_all("a") if a.get("href")]

        # Privacy Policy check
        for text, link in links:
            if any(k in text.lower() or k in link.lower() for k in ["privacy", "policy", "data policy"]):
                results["privacy_policy_found"] = True
                results["privacy_policy_link"] = link
                results["privacy_policy_keywords"] = analyze_policy_page(url, link)
                break

        # Terms & Conditions check
        for text, link in links:
            if any(k in text.lower() or k in link.lower() for k in ["terms", "conditions", "legal"]):
                results["terms_conditions_found"] = True
                results["terms_conditions_link"] = link
                results["terms_keywords"] = analyze_policy_page(url, link)
                break

        # Forms check
        forms = soup.find_all("form")
        results["forms_found"] = len(forms)
        for form in forms:
            inputs = [inp.get("type", "text") for inp in form.find_all("input")]
            results["forms_details"].append({
        "action": form.get("action") if form.get("action") else "N/A",
        "method": form.get("method").upper() if form.get("method") else "GET",
        "inputs": inputs,
        "has_password": "password" in inputs,
        "has_email": "email" in inputs,
        "has_checkbox": "checkbox" in inputs
    })

        # Tracker detection
        scripts = [s.get("src", "").lower() for s in soup.find_all("script") if s.get("src")]
        trackers = [s for s in scripts if any(t in s for t in tracker_keywords)]
        results["third_party_trackers"] = trackers

        # Security headers
        results["security_headers"] = analyze_security_headers(response.headers)

    except Exception as e:
        results["suggestions"].append(f"Error fetching page: {e}")

    # -------------------
    # STEP 2: Dynamic Scan (Selenium)
    # -------------------
    try:
        chrome_path = os.path.join("drivers", "chromedriver.exe")
        service = Service(chrome_path)
        options = webdriver.ChromeOptions()
        options.add_argument("--headless")
        driver = webdriver.Chrome(service=service, options=options)

        driver.get(url)
        time.sleep(3)

        page_source = driver.page_source.lower()

        # Cookie banner
        # if any(k in page_source for k in ["cookie", "consent", "gdpr", "accept cookies"]):
        #     results["cookie_banner"] = True
        #     results["gdpr_compliant"] = True
        if check_cookie_banner(page_source):
           results["cookie_banner"] = True

        # CCPA
        if "do not sell" in page_source or "ccpa" in page_source:
            results["ccpa_compliant"] = True

        # Cookies
        for cookie in driver.get_cookies():
            results["cookies"].append({
                "name": cookie.get("name"),
                "domain": cookie.get("domain"),
                "secure": cookie.get("secure"),
                "httpOnly": cookie.get("httpOnly"),
                "expiry": cookie.get("expiry")
            })
        # 🔑 Fetch real browser response headers
        headers = get_security_headers_selenium(driver, url)
        if headers:
            results["security_headers"] = headers
        driver.quit()

    except Exception as e:
        results["suggestions"].append(f"Selenium error: {e}")
    
    # -------------------
    # Compliance Analysis (NEW)
    # -------------------
    results = analyze_compliance(results)

    # -------------------
    # STEP 3: Suggestions
    # -------------------
    # Privacy Policy
    if results["privacy_policy_found"]:
     suggestions.append("✅ Privacy Policy found and accessible")
    else:
     suggestions.append("🔴 Privacy Policy not found – add one to improve compliance")

# Terms & Conditions
    if results["terms_conditions_found"]:
     suggestions.append("✅ Terms & Conditions page found")
    else:
     suggestions.append("🔴 Terms & Conditions missing – add one for transparency")

# Cookie Banner
    if results["cookie_banner"]:
     suggestions.append("✅ Cookie consent banner detected")
    else:
     suggestions.append("🔴 Implement a Cookie Consent Banner")

# Forms
    if results["forms_found"] > 0:
     suggestions.append(f"✅ {results['forms_found']} forms detected – ensure explicit consent for data collection")
    else:
     suggestions.append("🔴 No forms detected – verify if user input collection is required")

# Security headers
    if results.get("security_headers", {}).get("Strict-Transport-Security"):
     suggestions.append("✅ Strict-Transport-Security header present")
    else:
     suggestions.append("🔴 Add Strict-Transport-Security header")

    if results.get("security_headers", {}).get("Content-Security-Policy"):
     suggestions.append("✅ Content-Security-Policy header present")
    else:
     suggestions.append("🔴 Add Content-Security-Policy header")

# Attach to results
    results["suggestions"] = suggestions

    return results



# ------------------------
#  HELPERS
# ------------------------

def fetch_page(url, retries=3, timeout=20):
    """Fetch webpage with retries and longer timeout"""
    for attempt in range(retries):
        try:
            response = requests.get(
                url,
                timeout=timeout,
                headers={"User-Agent": "Mozilla/5.0"}
            )
            response.raise_for_status()
            return response
        except Exception as e:
            if attempt < retries - 1:
                time.sleep(2)
                continue
            raise e
        
def analyze_policy_page(base_url, link):
    """Fetch a policy/terms page and check for important keywords"""
    keywords = ["data", "personal", "cookies", "rights", "retention", "third parties", "consent"]
    found = []
    try:
        if link.startswith("/"):
            full_link = base_url.rstrip("/") + link
        elif link.startswith("http"):
            full_link = link
        else:
            full_link = base_url.rstrip("/") + "/" + link

        res = requests.get(full_link, timeout=10, headers={"User-Agent": "Mozilla/5.0"})
        text = res.text.lower()
        for k in keywords:
            if k in text:
                found.append(k)
    except:
        pass
    return found


def analyze_security_headers(headers):
    """Check important security headers"""
    required_headers = [
        "Strict-Transport-Security",
        "Content-Security-Policy",
        "X-Frame-Options",
        "X-Content-Type-Options",
        "Referrer-Policy"
    ]
    result = {}
    for h in required_headers:
        result[h] = headers.get(h, None)
    return result

def get_security_headers_selenium(driver, target_url):
    """Extract real response headers from Chrome performance logs"""
    headers = {}
    try:
        logs = driver.get_log("performance")
        for entry in logs:
            msg = json.loads(entry["message"])["message"]
            if msg["method"] == "Network.responseReceived":
                response_url = msg["params"]["response"]["url"]
                if response_url.startswith(target_url):
                    headers = msg["params"]["response"]["headers"]
                    break
    except Exception as e:
        print(f"[DEBUG] Could not fetch headers via Selenium: {e}")
    return headers

def check_cookie_banner(page_source: str) -> bool:
    """Detect cookie banner keywords in page source"""
    keywords = ["cookie", "consent", "gdpr", "accept cookies", "privacy preferences"]
    return any(k in page_source for k in keywords)

def analyze_compliance(results):
    """Smarter compliance logic based on multiple signals"""

    gdpr_signals = []
    ccpa_signals = []

    # ---------------------------
    # GDPR signals
    # ---------------------------
    if results.get("cookie_banner"):
        gdpr_signals.append("Cookie banner present")

    if results.get("privacy_policy_found"):
        gdpr_signals.append("Privacy Policy present")

    if results.get("forms_found", 0) > 0:
        for form in results["forms_details"]:
            if form.get("has_checkbox"):
                gdpr_signals.append("Form with consent checkbox detected")
                break

    if results.get("security_headers", {}).get("Content-Security-Policy"):
        gdpr_signals.append("Content-Security-Policy header present")

    if results.get("security_headers", {}).get("Strict-Transport-Security"):
        gdpr_signals.append("Strict-Transport-Security header present")

    # ---------------------------
    # CCPA signals
    # ---------------------------
    if "do not sell" in str(results.get("privacy_policy_keywords", [])).lower():
        ccpa_signals.append("'Do Not Sell' clause in Privacy Policy")

    if results.get("cookie_banner"):
        ccpa_signals.append("Cookie banner detected")

    if results.get("privacy_policy_link") and "us" in (results["privacy_policy_link"] or "").lower():
        ccpa_signals.append("US-specific Privacy Policy link")

    # ---------------------------
    # Final decision
    # ---------------------------
    results["gdpr_compliant"] = "Likely Compliant" if len(gdpr_signals) >= 3 else "Not Compliant"
    results["ccpa_compliant"] = "Likely Compliant" if len(ccpa_signals) >= 2 else "Not Compliant"

    # Store details for transparency
    results["gdpr_signals"] = gdpr_signals
    results["ccpa_signals"] = ccpa_signals

    return results

