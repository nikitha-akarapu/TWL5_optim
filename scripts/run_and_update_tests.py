import pandas as pd
import subprocess
import os
import sys
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EXCEL_FILE = os.path.join(BASE_DIR, "test_data", "Employee_Creation_Test_Cases.xlsx")
TESTS_DIR = os.path.join(BASE_DIR, "tests")

import glob

def main():
    # Delete any existing .png screenshot files from previous runs in root and tests directories
    for pattern in [os.path.join(BASE_DIR, "*.png"), os.path.join(BASE_DIR, "tests", "*.png"), os.path.join(BASE_DIR, "screenshots", "*.png")]:
        for f in glob.glob(pattern):
            try:
                os.remove(f)
            except OSError:
                pass

    if not os.path.exists(EXCEL_FILE):
        print(f"Error: {EXCEL_FILE} not found.")
        sys.exit(1)

    try:
        df = pd.read_excel(EXCEL_FILE)
    except Exception as e:
        print(f"Error reading {EXCEL_FILE}: {e}")
        sys.exit(1)

    # Ensure required columns exist
    for col in ["Execution Status", "Execution Timestamp", "Remarks"]:
        if col not in df.columns:
            df[col] = ""

    # Iterate through rows
    for index, row in df.iterrows():
        tc_id = row.get("Test Case ID")
        if pd.isna(tc_id):
            continue
            
        tc_id_clean = str(tc_id).strip()
        tc_id_formatted = tc_id_clean.replace("-", "_")
        
        test_script_name = f"test_{tc_id_formatted}.py"
        test_script_path = os.path.join(TESTS_DIR, test_script_name)
        
        if not os.path.exists(test_script_path):
            print(f"Skipping {tc_id_clean}: Script {test_script_path} not found.")
            df.at[index, "Execution Status"] = "Script Missing"
            continue
            
        test_script_path_from_root = os.path.join("tests", test_script_name)
        print(f"Running {test_script_path_from_root} from root directory...")
        try:
            # Run the script and capture output
            result = subprocess.run(
                [sys.executable, test_script_path_from_root],
                cwd=BASE_DIR,
                capture_output=True,
                text=True,
                timeout=300 # 5 minutes max per test
            )
            
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            df.at[index, "Execution Timestamp"] = timestamp
            
            if result.returncode == 0:
                print(f"  -> {tc_id_clean} PASSED")
                df.at[index, "Execution Status"] = "Passed"
                df.at[index, "Remarks"] = ""  # Clear any previous remarks
            else:
                print(f"  -> {tc_id_clean} FAILED")
                df.at[index, "Execution Status"] = "Failed"
                # Combine stderr and stdout for remarks, keeping the last 1500 chars to avoid excel cell limits
                error_output = result.stderr + "\n" + result.stdout
                if len(error_output) > 1500:
                    error_output = error_output[-1500:] 
                df.at[index, "Remarks"] = error_output.strip()
                
        except subprocess.TimeoutExpired:
            print(f"  -> {tc_id_clean} TIMED OUT")
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            df.at[index, "Execution Timestamp"] = timestamp
            df.at[index, "Execution Status"] = "Failed (Timeout)"
            df.at[index, "Remarks"] = "Test execution timed out after 300 seconds."
        except Exception as e:
            print(f"  -> {tc_id_clean} ERROR: {e}")
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            df.at[index, "Execution Timestamp"] = timestamp
            df.at[index, "Execution Status"] = "Error"
            df.at[index, "Remarks"] = str(e)

    # Save the updated DataFrame back to Excel
    print(f"Saving updated test results to {EXCEL_FILE}...")
    try:
        df.to_excel(EXCEL_FILE, index=False)
        print("Done!")
    except PermissionError:
        fallback_file = EXCEL_FILE.replace(".xlsx", "_results.xlsx")
        print(f"Permission denied for {EXCEL_FILE} (it may be open). Saving to {fallback_file} instead.")
        try:
            df.to_excel(fallback_file, index=False)
            print(f"Saved successfully to {fallback_file}")
        except Exception as e2:
            print(f"Failed to save fallback file: {e2}")
    except Exception as e:
        print(f"Error saving updated file: {e}")

if __name__ == "__main__":
    main()
