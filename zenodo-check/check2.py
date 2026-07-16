"""Deeper check on PDF text rendering."""
import os

base = r"D:\ll\knowledge-base\10-security\zenodo-check"

for i, fname in enumerate(["paper1.pdf", "paper2.pdf"]):
    print(f"=== PAPER {i+1} ===")
    with open(os.path.join(base, fname), "rb") as f:
        content = f.read()

    # Check for text streams (compressed PDFs use FlateDecode)
    has_stream = content.count(b"stream") 
    has_endstream = content.count(b"endstream")
    has_flate = b"FlateDecode" in content
    print(f"Stream blocks: {has_stream}, EndStream: {has_endstream}")
    print(f"Compressed (FlateDecode): {has_flate}")
    
    # Check for font references
    fonts = []
    for line in content.split(b'\n'):
        if b'/BaseFont' in line or b'/FontName' in line:
            fonts.append(line.strip()[:100])
    print(f"Font references found: {len(fonts)}")
    for f in fonts[:5]:
        print(f"  {f}")
    
    # Try to find /ToUnicode CMap (for text extraction)
    has_tounicode = b'/ToUnicode' in content
    print(f"Has /ToUnicode CMap: {has_tounicode}")
    
    # Try extracting text with PyPDF2
    try:
        import PyPDF2
        reader = PyPDF2.PdfReader(os.path.join(base, fname))
        print(f"Pages: {len(reader.pages)}")
        for j, page in enumerate(reader.pages):
            text = page.extract_text()
            if text and text.strip():
                preview = text[:200].replace('\n', ' ')
                print(f"  Page {j+1} text: {preview}...")
            else:
                print(f"  Page {j+1}: [no extractable text]")
    except ImportError:
        print("PyPDF2 not installed, trying pdfplumber...")
        try:
            import pdfplumber
            with pdfplumber.open(os.path.join(base, fname)) as pdf:
                print(f"Pages: {len(pdf.pages)}")
                for j, page in enumerate(pdf.pages):
                    text = page.extract_text()
                    if text and text.strip():
                        preview = text[:200].replace('\n', ' ')
                        print(f"  Page {j+1} text: {preview}...")
                    else:
                        print(f"  Page {j+1}: [no extractable text]")
        except ImportError:
            print("No PDF text extraction library available")
    print()
