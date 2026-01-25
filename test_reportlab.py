from reportlab.pdfgen import canvas
try:
    c = canvas.Canvas("test.pdf")
    c.drawString(100, 750, "Hello World")
    c.save()
    print("SUCCESS")
except Exception as e:
    print(f"FAILURE: {e}")
