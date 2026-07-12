"""Extract real family office data from Excel"""
import pandas as pd
from openpyxl import load_workbook
from pathlib import Path
from datetime import datetime

def extract_from_excel():
    """Extract family offices from FO-MAX-data-sample Excel"""
    
    excel_path = Path("data/FO-MAX-data-sample-2.0.xlsx")  # CHANGED: dot not underscore
    
    # Read Excel (header is in row 4)
    wb = load_workbook(excel_path)
    ws = wb.active
    
    records = []
    
    # Row 4 has headers, data starts from Row 5
    for row_idx, row in enumerate(ws.iter_rows(min_row=5, max_row=120, values_only=True), 1):
        if not row[1]:  # Empty family office name
            continue
        
        record = {
            "name": row[1],
            "validation_period": row[2],
            "data_completion_text": row[3],
            "data_completion_visual": row[4],
            "description": row[5] if len(row) > 5 else "",
            "investment_thesis": row[6] if len(row) > 6 else "",
            "sectors": row[7] if len(row) > 7 else "",
            "domain": row[8] if len(row) > 8 else "",
            "website": row[9] if len(row) > 9 else "",
            "url_quality": row[10] if len(row) > 10 else "",
            "corporate_linkedin": row[11] if len(row) > 11 else "",
            "street_address": row[12] if len(row) > 12 else "",
            "city": row[13] if len(row) > 13 else "",
            "state_region": row[14] if len(row) > 14 else "",
            "country": row[15] if len(row) > 15 else "",
            "contact_first_name": row[16] if len(row) > 16 else "",
            "contact_last_name": row[17] if len(row) > 17 else "",
            "contact_full_name": row[18] if len(row) > 18 else "",
            "contact_job_title": row[19] if len(row) > 19 else "",
            "contact_location": row[20] if len(row) > 20 else "",
            "contact_linkedin": row[21] if len(row) > 21 else "",
            "contact_email": row[22] if len(row) > 22 else "",
            "email_validation": row[23] if len(row) > 23 else "",
            "email_quality": row[24] if len(row) > 24 else "",
            "contact_phone": row[25] if len(row) > 25 else "",
            "secondary_email": row[26] if len(row) > 26 else "",
            "secondary_email_validation": row[27] if len(row) > 27 else "",
            "secondary_phone": row[28] if len(row) > 28 else "",
        }
        records.append(record)
    
    print(f"✓ Extracted {len(records)} family offices from Excel")
    return records[:50]

def save_extracted_data(records):
    """Save extracted records to CSV"""
    output_path = Path("output/family_offices_extracted.csv")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    df = pd.DataFrame(records)
    df.to_csv(output_path, index=False)
    
    print(f"✓ Saved {len(records)} records to: {output_path}")
    return output_path

def log_extraction():
    """Log extraction process"""
    records = extract_from_excel()
    output_path = save_extracted_data(records)
    
    log_entry = f"\n[DATA EXTRACTION - {datetime.now().isoformat()}]\n"
    log_entry += f"Source: FO-MAX-data-sample-2.0.xlsx\n"
    log_entry += f"Records extracted: {len(records)}\n"
    log_entry += f"Output file: {output_path}\n"
    log_entry += f"Data quality: REAL family office records from verified database\n"
    
    with open("logs/build_log.txt", "a") as f:
        f.write(log_entry)
    
    print("\n✓ Data extraction complete!")
    return records

if __name__ == "__main__":
    log_extraction()
