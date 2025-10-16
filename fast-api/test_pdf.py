import requests
import os

# Test both HTML and PDF endpoints
base_url = "http://localhost:8000/employee/101"

print("Testing HTML vs PDF responses...\n")

# Test HTML
print("1. Testing HTML response:")
html_response = requests.get(base_url)
print(f"   Status Code: {html_response.status_code}")
print(f"   Content-Type: {html_response.headers.get('content-type')}")
print(f"   Content Length: {len(html_response.content)} bytes")
print(f"   Contains HTML?: {'<html>' in html_response.text}")

# Save HTML
with open("test_employee.html", "wb") as f:
    f.write(html_response.content)
print("   Saved as: test_employee.html")

print("\n" + "="*50 + "\n")

# Test PDF
print("2. Testing PDF response:")
pdf_response = requests.get(f"{base_url}?format=pdf")
print(f"   Status Code: {pdf_response.status_code}")
print(f"   Content-Type: {pdf_response.headers.get('content-type')}")
print(f"   Content Length: {len(pdf_response.content)} bytes")
print(f"   Content-Disposition: {pdf_response.headers.get('content-disposition')}")
print(f"   Starts with PDF header?: {pdf_response.content.startswith(b'%PDF')}")

# Save PDF
with open("test_employee.pdf", "wb") as f:
    f.write(pdf_response.content)
print("   Saved as: test_employee.pdf")

print("\n" + "="*50)
print("✅ Check the generated files:")
print("   - test_employee.html (open in browser)")
print("   - test_employee.pdf (open in PDF viewer)")
print("="*50)