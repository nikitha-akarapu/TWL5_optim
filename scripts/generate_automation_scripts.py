import asyncio
import os
import json
import pandas as pd
from google import genai
from google.genai import types
from dotenv import load_dotenv

load_dotenv()

async def generate_playwright_script(client, test_case_row):
    prompt = f"""
You are an expert Automation QA Engineer. 
Below is a manual test case for an 'Employee Creation' feature on a web application (https://dev.urbuddi.com/).
Your task is to write a standalone Python Playwright test script for this specific manual test case.

Test Case Details:
- Test Case ID: {test_case_row.get('Test Case ID', '')}
- Description: {test_case_row.get('Description', '')}
- Pre-conditions: {test_case_row.get('Pre-conditions', '')}
- Test Steps: {test_case_row.get('Test Steps', '')}
- Expected Result: {test_case_row.get('Expected Result', '')}

Requirements:
1. Use Playwright's async API (`async_playwright`).
2. The code should be fully self-contained and runnable, including an `async def test_...()` or a generic `async def main()` executing the test.
3. Add appropriate assertions (`assert` or `expect` from `playwright.async_api`).
4. Include clear comments explaining the steps.
5. If the test requires login or specific locators that you are not 100% sure about, use highly probable generic locators (e.g., placeholder, text, or common ids) and leave a comment.

Output ONLY the full Python script without any markdown brackets, explanations, or backticks. Start directly with imports.
"""

    try:
        response = await client.aio.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt,
        )
        
        # Strip trailing/leading markdown if Gemini still adds them
        script_code = response.text.strip()
        if script_code.startswith("```python"):
            script_code = script_code[9:]
        if script_code.startswith("```"):
            script_code = script_code[3:]
        if script_code.endswith("```"):
            script_code = script_code[:-3]
            
        return script_code.strip()

    except Exception as e:
        print(f"Error generating script: {e}")
        return None

async def main():
    if not os.getenv("GEMINI_API_KEY"):
        print("ERROR: Please set the GEMINI_API_KEY environment variable before running.")
        return

    client = genai.Client()
    excel_filename = "../test_data/Employee_Creation_Test_Cases.xlsx"

    print(f"Loading test cases from {excel_filename}...")
    try:
        df = pd.read_excel(excel_filename)
    except FileNotFoundError:
        print(f"Error: {excel_filename} not found.")
        return
    except Exception as e:
        print(f"Error reading Excel file: {e}")
        return

    # Ensure columns exist
    if "automation_status" not in df.columns:
        df["automation_status"] = "Pending"

    tests_dir = "../tests"
    os.makedirs(tests_dir, exist_ok=True)

    print(f"Found {len(df)} test cases. Starting generation...")

    for index, row in df.iterrows():
        # Check if already generated
        if str(row.get("automation_status", "")).strip().lower() == "generated":
            print(f"Skipping {row['Test Case ID']}, already generated.")
            continue

        print(f"[{index+1}/{len(df)}] Generating script for {row.get('Test Case ID', 'Unknown')}...")
        
        script_code = await generate_playwright_script(client, dict(row))
        
        if script_code:
            # Create a valid filename
            safe_id = str(row.get('Test Case ID', 'Test')).replace(' ', '_').replace('-', '_')
            file_path = os.path.join(tests_dir, f"test_{safe_id}.py")
            
            try:
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(script_code)
                print(f"  -> Saved to {file_path}")
                
                # Update status
                df.at[index, "automation_status"] = "Generated"
            except Exception as e:
                print(f"  -> Error saving file {file_path}: {e}")
                df.at[index, "automation_status"] = f"Failed to save: {str(e)}"
        else:
            df.at[index, "automation_status"] = "Failed Generation"
            
        # Optional: Add a small delay to avoid rate limiting
        await asyncio.sleep(2)

    # Save back to Excel
    print(f"Saving updated status back to {excel_filename}...")
    try:
        # Avoid permission error if the file is open
        df.to_excel(excel_filename, index=False)
        print("Success! Excel file updated.")
    except PermissionError:
        print(f"CRITICAL: Permission denied to save {excel_filename}. Please close the Excel file and try again.")
        fallback = "../test_data/Employee_Creation_Test_Cases_Updated.xlsx"
        df.to_excel(fallback, index=False)
        print(f"Saved to fallback file: {fallback}")
    except Exception as e:
        print(f"Failed to update Excel file: {e}")

if __name__ == "__main__":
    asyncio.run(main())
