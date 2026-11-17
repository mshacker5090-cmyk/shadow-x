
from flask import Flask, request, render_template_string
import re
import os
import dns.resolver
import phonenumbers
from phonenumbers import PhoneNumberFormat
from markupsafe import escape

app = Flask(__name__)

HTML = """
<!DOCTYPE html>
<html>
<head>
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>SHADOW X</title>
<style>
* {box-sizing:border-box}
body {
    margin:0;
    padding:20px;
    background:#080b14;
    color:#00e5ff;
    font-family:Arial,sans-serif;
}
.container {
    max-width:650px;
    margin:30px auto;
    padding:24px;
    background:#111827;
    border:1px solid #00e5ff;
    border-radius:15px;
}
h1 {text-align:center;font-size:32px}
.creator {text-align:center;color:#aaa}
input {
    width:100%;
    padding:14px;
    margin:10px 0;
    background:#080b14;
    border:1px solid #00e5ff;
    border-radius:8px;
    color:white;
}
button {
    width:100%;
    padding:14px;
    background:#00e5ff;
    border:0;
    border-radius:8px;
    font-weight:bold;
    font-size:16px;
}
.result {
    background:#080b14;
    padding:14px;
    margin-top:12px;
    border-radius:8px;
    overflow-wrap:anywhere;
}
a {color:#00e5ff}
small {color:#aaa}
</style>
</head>
<body>
<div class="container">
<h1>SHADOW X</h1>
<p class="creator">AUTOMATED PUBLIC INTELLIGENCE</p>
<p class="creator">Created by Mohit Sharma</p>

<form method="POST">
<input name="email" type="email"
placeholder="Enter your email address">
<input name="phone"
placeholder="Enter your phone number (+91...)">
<button type="submit">START SCAN</button>
</form>

{% if report %}
<h3>SCAN REPORT</h3>
{% for item in report %}
<div class="result">{{ item|safe }}</div>
{% endfor %}
{% endif %}

<p><small>Only your own or authorized information.
No private account access.</small></p>
</div>
</body>
</html>
"""

def email_scan(email):
    report = []

    if not re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", email):
        return ["Invalid email format"]

    report.append("Email format: Valid")

    domain = email.rsplit("@", 1)[1].lower()
    report.append("Domain: " + str(escape(domain)))

    try:
        records = dns.resolver.resolve(domain, "MX")
        mx = [str(r.exchange).rstrip(".") for r in records]
        report.append("MX Records: " + str(escape(", ".join(mx))))
    except Exception:
        report.append("MX Records: Unavailable")

    report.append(
        "Account ownership: Cannot be confirmed from email syntax."
    )
    return report


def phone_scan(phone):
    report = []

    try:
        number = phonenumbers.parse(phone, None)

        if phonenumbers.is_valid_number(number):
            report.append("Phone format: Valid")
            report.append(
                "Country: " +
                str(escape(phonenumbers.region_code_for_number(number)))
            )
            report.append(
                "International: " +
                str(escape(phonenumbers.format_number(
                    number, PhoneNumberFormat.INTERNATIONAL
                )))
            )
            report.append(
                '<a href="https://www.truecaller.com/" target="_blank">'
                'Open official Truecaller</a>'
            )
            report.append(
                "Caller name requires authorized Truecaller access."
            )
        else:
            report.append("Phone number: Invalid")

    except Exception:
        report.append("Phone number: Invalid format")

    return report


@app.route("/", methods=["GET", "POST"])
def home():
    report = []

    if request.method == "POST":
        email = request.form.get("email", "").strip()
        phone = request.form.get("phone", "").strip()

        if email:
            report.extend(email_scan(email))

        if phone:
            report.extend(phone_scan(phone))

        if not email and not phone:
            report.append("Enter an email or phone number.")

    return render_template_string(HTML, report=report)


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
