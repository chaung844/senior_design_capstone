Analyze the bank statement image and extract **ALL transactions** as a YAML array of objects. **Do not skip any transaction rows** (including headers, footers, or empty rows). Only extract data rows with transaction details.

**Extract these fields for EVERY transaction row (in this order):**
- `posting_date`: Date when transaction posted to account (YYYY-MM-DD). If ambiguous, use original format (e.g., "Oct 5, 2023" → "2023-10-05").
- `transaction_date`: Date transaction occurred (YYYY-MM-DD). Same format rules as `posting_date`.
- `description`: **Exact** text from the description column (e.g., "STARBUCKS 12345 NYC" → keep as-is).
- `reference`: **Exact** reference ID (e.g., "REF: TXN-789" → "TXN-789", **not** "REF: TXN-789").
- `mcc`: **4-digit numeric code only** (e.g., "5812", **not** "5812 - Coffee Shop"). If missing, output `""`.
- `charge`: **Numeric value with sign** (e.g., `"-15.99"` for debit, `"100.00"` for credit). **Never** omit sign or format as currency.

**Output rules (ABSOLUTE):**
1. **ONLY** output a valid YAML array. **NO** explanations, headers, or extra text.
2. **NO** missing transactions (include all rows with data).
3. If a field is missing in a row, output `""` (empty string) for that field.
4. **NEVER** interpret values (e.g., `description: "Starbucks"` → **keep as "STARBUCKS"`**).
5. **NEVER** convert `mcc` to text or add extra fields.

**Example output (DO NOT INCLUDE IN OUTPUT):**
```yaml
- posting_date: "2023-10-05"
  transaction_date: "2023-10-03"
  description: "STARBUCKS 12345 NYC"
  reference: "TXN-7890"
  mcc: "5812"
  charge: "-15.99"
- posting_date: "2023-10-06"
  transaction_date: "2023-10-06"
  description: "PAYMENT RECEIVED"
  reference: "INV-2023"
  mcc: ""
  charge: "100.00"
```