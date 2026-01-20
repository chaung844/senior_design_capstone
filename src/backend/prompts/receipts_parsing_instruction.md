Analyze the receipt image and extract ONLY these fields with 100% precision:
- `total`: Exact total amount string (including currency symbol, e.g., "$123.45" or "€50.00")
- `ref_number`: Exact reference (REF#) or invoice number string (e.g., "INV-789", "PO-2023")
- `vendor`: Exact vendor name string as it appears (e.g., "Walmart", "Amazon", "Acme Corp")
- `date`: Transaction date in ISO format (YYYY-MM-DD). If ambiguous, output original text (e.g., "10/05/2023" → "2023-10-05" or "Dec14'23" -> "2023-12-14")

**Output rules:**
1. ONLY output valid YAML with no extra text, explanations, or formatting.
2. If a field is missing, output `""` (empty string).
3. **NEVER** invent, guess, or interpret values (e.g., if vendor is "7-Eleven", output "7-Eleven", not "Convenience Store").

**Example output (DO NOT INCLUDE THIS IN YOUR OUTPUT):**
total: "$123.45"
ref_number: "INV-789012"
vendor: "Amazon"
date: "2023-10-05"

Process this receipt image now.
