import base64
import io
import json
import os
import subprocess
import tempfile

import frappe
import qrcode

def _qr_url(text):
    img = qrcode.make(text, box_size=4, border=0)
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return "data:image/png;base64," + base64.b64encode(buf.getvalue()).decode()

def _html_to_pdf(html):
    with tempfile.TemporaryDirectory() as tmp:
        src = os.path.join(tmp, "label.html")
        out = os.path.join(tmp, "label.pdf")
        with open(src, "w", encoding="utf-8") as f:
            f.write(html)
        subprocess.run(
    	     [
        	"wkhtmltopdf",
        	"--page-width", "108mm",
        	"--page-height", "15mm",
        	"--disable-smart-shrinking",
        	"--zoom", "1",
        	"-T", "0", "-B", "0", "-L", "0", "-R", "0",
        	"--enable-local-file-access",
        	"--quiet",
        	src, out,
    	     ],
            check=True,
        )
        with open(out, "rb") as f:
            return f.read()

def _html_to_pdf_a4(html):
    with tempfile.TemporaryDirectory() as tmp:
        src = os.path.join(tmp, "label.html")
        out = os.path.join(tmp, "label.pdf")
        with open(src, "w", encoding="utf-8") as f:
            f.write(html)
        subprocess.run(
            [
                "wkhtmltopdf",
                "--page-size", "A4",
                "-T", "10mm", "-B", "10mm", "-L", "10mm", "-R", "10mm",
                "--disable-smart-shrinking",
                "--zoom", "1",
                "--quiet",
                src, out,
            ],
            check=True,
        )
        with open(out, "rb") as f:
            return f.read()

@frappe.whitelist()
def print_serial_labels_a4(names):
    if isinstance(names, str):
        names = json.loads(names)

    items = []
    for n in names:
        d = frappe.db.get_value(
            "Serial No",
            n,
            ["name", "item_name", "item_code", "posting_date", "creation"],
            as_dict=True,
        )
        if d:
            d["date"] = frappe.utils.format_date(
                d.posting_date or d.creation, "dd-MM-yyyy"
            )
            d["qr"] = _qr_url(d.name)
            items.append(d)

    # 4 kolom x 9 baris per halaman A4 = 36 label per lembar
    per_page = 36
    pages = [items[i:i + per_page] for i in range(0, len(items), per_page)]

    template_path = frappe.get_app_path("serial_label", "templates", "serial_label_a4.html")
    with open(template_path, encoding="utf-8") as f:
        template = f.read()

    html = frappe.render_template(template, {"pages": pages})
    pdf = _html_to_pdf_a4(html)

    frappe.response["type"] = "pdf"
    frappe.response["filename"] = "serial_labels_a4.pdf"
    frappe.response["filecontent"] = pdf

def print_serial_labels(names):
    if isinstance(names, str):
        names = json.loads(names)

    items = []
    for n in names:
        d = frappe.db.get_value(
            "Serial No",
            n,
            ["name", "item_name", "item_code", "posting_date", "creation"],
            as_dict=True,
        )
        if d:
            d["date"] = frappe.utils.format_date(
                d.posting_date or d.creation, "dd-MM-yyyy"
            )
            d["qr"] = _qr_url(d.name)
            items.append(d)

    rows = [items[i:i + 3] for i in range(0, len(items), 3)]

    template_path = frappe.get_app_path("serial_label", "templates", "serial_label.html")
    with open(template_path, encoding="utf-8") as f:
        template = f.read()

    html = frappe.render_template(template, {"rows": rows})
    pdf = _html_to_pdf(html)

    frappe.response["type"] = "pdf"
    frappe.response["filename"] = "serial_labels.pdf"
    frappe.response["filecontent"] = pdf
