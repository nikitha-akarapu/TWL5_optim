import asyncio
import os
import sys
import json
import pandas as pd
import subprocess
from datetime import datetime
from playwright.async_api import async_playwright
from google import genai
from google.genai import types
from dotenv import load_dotenv
from bs4 import BeautifulSoup

# Load environment variables from .env file
load_dotenv()

EXCEL_FILE = "Employee_Creation_Test_Cases.xlsx"
TESTS_DIR = "tests"

async def generate_test_cases(client, feature_prompt: str, html_content: str, email: str, password: str):
    print(f"Generating manual test cases for '{feature_prompt}' using Gemini AI...")
    prompt = f"""
You are an expert QA Engineer.
Below is the HTML snippet of the '{feature_prompt}' form from a web application.
The application credentials are Email: {email} and Password: {password}. Use these if applicable.
Analyze the form fields, their types, required attributes, and overall structure.
Generate a comprehensive list of manual test cases for the {feature_prompt} feature.
Include positive flows, negative flows (missing mandatory fields, invalid data like wrong email/phone formats, text in number fields), and edge cases.

Return ONLY a valid JSON object with a single key "test_cases" which contains an array of objects.
Each object must have the following string properties:
- "Test Case ID" (e.g., "TC-001")
- "Description"
- "Pre-conditions"
- "Test Steps"
- "Expected Result"
- "automation_status"
- "Execution Status"
- "Execution Timestamp"
- "Remarks"

Form HTML Content:
{html_content}
"""

    response = await client.aio.models.generate_content(
        model='gemini-2.5-flash',
        contents=prompt,
        config=types.GenerateContentConfig(
            system_instruction="You are a helpful QA assistant that outputs strict JSON.",
            response_mime_type="application/json",
        )
    )
    
    result_text = response.text
    try:
        data = json.loads(result_text)
        return data.get("test_cases", [])
    except json.JSONDecodeError:
        print("Error parsing the JSON from Gemini.")
        return []

def extract_locators_from_html(html_content: str):
    """Parses HTML and returns a map of interactive elements to their best Playwright locators."""
    print("Extracting exact locators from DOM...")
    soup = BeautifulSoup(html_content, 'html.parser')
    locators = []
    
    elements = soup.find_all(['input', 'button', 'select', 'textarea', 'a'])
    
    for el in elements:
        tag_name = el.name
        el_type = el.get('type', '')
        
        # Determine the best way to describe this element to the AI
        description = tag_name
        if el_type: description += f" type='{el_type}'"
        
        # Extract potential locators in order of preference
        locator_str = ""
        if el.get('id'):
            locator_str = f"page.locator(\"#{el.get('id')}\")"
            description += f" (ID: {el.get('id')})"
        elif el.get('name'):
            locator_str = f"page.locator(\"[name='{el.get('name')}']\")"
            description += f" (Name: {el.get('name')})"
        elif el.get('data-testid'):
            locator_str = f"page.get_by_test_id(\"{el.get('data-testid')}\")"
            description += f" (TestID: {el.get('data-testid')})"
        elif el.get('placeholder'):
            locator_str = f"page.get_by_placeholder(\"{el.get('placeholder')}\")"
            description += f" (Placeholder: {el.get('placeholder')})"
        elif el.get('aria-label'):
            locator_str = f"page.get_by_label(\"{el.get('aria-label')}\")"
            description += f" (Aria-Label: {el.get('aria-label')})"
        elif el.text and el.text.strip():
            # Useful for buttons and links
            clean_text = el.text.strip()[:30] # Limit length
            locator_str = f"page.get_by_text(\"{clean_text}\")"
            description += f" (Text: {clean_text})"
        
        if locator_str:
            locators.append(f"- Element: {description} -> Recommended Locator: {locator_str}")
            
    return "\n".join(locators) if locators else "No interactive elements found."


async def generate_playwright_script(client, feature_prompt: str, test_case_row: dict, email: str, password: str, html_content: str, locator_map: str):
    prompt = f"""
You are an expert Automation QA Engineer. 
Below is a manual test case and the relevant HTML snippet for a '{feature_prompt}' feature on a web application (https://dev.urbuddi.com/).
Your task is to write a standalone Python Playwright test script for this specific manual test case.

Test Case Details:
- Test Case ID: {test_case_row.get('Test Case ID', '')}
- Description: {test_case_row.get('Description', '')}
- Pre-conditions: {test_case_row.get('Pre-conditions', '')}
- Test Steps: {test_case_row.get('Test Steps', '')}
- Expected Result: {test_case_row.get('Expected Result', '')}

Form HTML Content:
{html_content}

Extracted Available Exact Locators:
{locator_map}

Login Credentials to use in the script:
Email: {email}
Password: {password}

Requirements:
1. Use Playwright's async API (`async_playwright`) and always launch the browser in headed mode: `await p.chromium.launch(headless=False)`.
2. The code should be fully self-contained and runnable, including an `async def test_...()` or a generic `async def main()` executing the test.
3. Automatically perform login using the credentials provided above prior to executing the test steps. For the login page specifically, verify if `page.locator("#userEmail")` and `page.locator("#userPassword")` (or similar ID based locators) exist in the 'Extracted Available Exact Locators'. If they do not appear in the extracted map, refer to the best locator available for those fields.
4. Add appropriate assertions (`assert` or `expect` from `playwright.async_api`).
5. Include clear comments explaining the steps.
6. CAREFULLY analyze the 'Extracted Available Exact Locators' map provided above. You MUST USE the 'Recommended Locator' from this map for every interactive element required to execute the test steps. DO NOT invent or guess locators. If an element is absolutely required but not in the map, fallback to CSS selectors using the 'Form HTML Content'.

Output ONLY the full Python script without any markdown brackets, explanations, or backticks. Start directly with imports.
"""

    try:
        response = await client.aio.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt,
        )
        
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

def execute_generated_tests(df: pd.DataFrame):
    print("Executing Generated Tests...")
    
    # Ensure required columns exist
    for col in ["Execution Status", "Execution Timestamp", "Remarks"]:
        if col not in df.columns:
            df[col] = ""
            
    for index, row in df.iterrows():
        tc_id = row.get("Test Case ID")
        if pd.isna(tc_id):
            continue
            
        tc_id_clean = str(tc_id).strip()
        tc_id_formatted = tc_id_clean.replace("-", "_").replace(" ", "_")
        
        test_script_name = f"test_{tc_id_formatted}.py"
        test_script_path = os.path.join(TESTS_DIR, test_script_name)
        
        if not os.path.exists(test_script_path):
            print(f"Skipping {tc_id_clean}: Script {test_script_path} not found.")
            df.at[index, "Execution Status"] = "Script Missing"
            continue
            
        print(f"Running {test_script_path}...")
        try:
            result = subprocess.run(
                [sys.executable, test_script_path],
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
            df.at[index, "Execution Timestamp"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            df.at[index, "Execution Status"] = "Failed (Timeout)"
            df.at[index, "Remarks"] = "Test execution timed out after 300 seconds."
        except Exception as e:
            print(f"  -> {tc_id_clean} ERROR: {e}")
            df.at[index, "Execution Timestamp"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            df.at[index, "Execution Status"] = "Error"
            df.at[index, "Remarks"] = str(e)
            
    return df

async def main():
    if not os.getenv("GEMINI_API_KEY"):
        print("ERROR: Please set the GEMINI_API_KEY environment variable in .env before running.")
        return

    admin_email = os.getenv("ADMIN_EMAIL", "")
    admin_password = os.getenv("ADMIN_PASSWORD", "")

    if not admin_email or not admin_password:
        print("WARNING: ADMIN_EMAIL or ADMIN_PASSWORD not found in .env.")
        print("The generated automation scripts might not be able to log in successfully.")
        response = input("Do you want to continue anyway? (y/n): ")
        if response.lower() != 'y':
            return

    client = genai.Client()

    feature_prompt = input("Enter feature Prompt to test (e.g. Leave Application): ")
    if not feature_prompt:
        print("Feature prompt cannot be empty. Exiting.")
        return

    print("Launching browser for manual navigation to the target page...")
    async with async_playwright() as p:
        # Launch in headed mode so you can interact with the page (e.g., login)
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context()
        page = await context.new_page()

        target_url = "https://dev.urbuddi.com/"
        print(f"Navigating to {target_url}...")
        await page.goto(target_url)

        print("-" * 60)
        print("Action Required: The browser is now open.")
        print("1. Please log in to urBuddi if required.")
        print(f"2. Navigate to the '{feature_prompt}' page/form.")
        print(f"3. Once the '{feature_prompt}' form is fully visible on the screen, press ENTER here.")
        print("-" * 60)

        # Wait for user to be ready
        input(f"Press ENTER when you are on the '{feature_prompt}' page...")

        print("Extracting page structure...")
        html_content = await page.evaluate('''() => {
            // Remove scripts and SVGs to save tokens
            document.querySelectorAll("script, svg, style").forEach(el => el.remove());
            return document.body.innerHTML;
        }''')

        # Limit HTML size if it's exceptionally large
        if len(html_content) > 30000:
            html_content = html_content[:30000] + "\n...[truncated]"
            
        locator_map = extract_locators_from_html(html_content)
        
        await browser.close()
        
    print(f"Step 1: Generating Test Cases for {feature_prompt}...")
    test_cases_list = await generate_test_cases(client, feature_prompt, html_content, admin_email, admin_password)

    if not test_cases_list:
        print("No test cases generated. Exiting.")
        return
        
    df = pd.DataFrame(test_cases_list)
    print(f"Found {len(df)} test cases.")

    # Step 2: Generate Playwright scripts
    print(f"Step 2: Generating Automation Scripts for {feature_prompt}...")
    os.makedirs(TESTS_DIR, exist_ok=True)
    
    if "automation_status" not in df.columns:
        df["automation_status"] = "Pending"
        
    for index, row in df.iterrows():
        print(f"[{index+1}/{len(df)}] Generating script for {row.get('Test Case ID', 'Unknown')}...")
        
        script_code = await generate_playwright_script(client, feature_prompt, dict(row), admin_email, admin_password, html_content, locator_map)
        
        if script_code:
            safe_id = str(row.get('Test Case ID', 'Test')).replace(' ', '_').replace('-', '_')
            file_path = os.path.join(TESTS_DIR, f"test_{safe_id}.py")
            
            try:
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(script_code)
                print(f"  -> Saved to {file_path}")
                df.at[index, "automation_status"] = "Generated"
            except Exception as e:
                print(f"  -> Error saving file {file_path}: {e}")
                df.at[index, "automation_status"] = f"Failed to save: {str(e)}"
        else:
            df.at[index, "automation_status"] = "Failed Generation"
            
        await asyncio.sleep(2) # Prevent Gemini rate-limiting

    # Step 3: Execute tests
    print(f"Step 3: Running Automation Scripts...")
    df = execute_generated_tests(df)
    
    # Step 4: Save to Excel
    print(f"Step 4: Saving updated test cases & execution results to Excel...")
    try:
        df.to_excel(EXCEL_FILE, index=False)
        print(f"Success! Final data saved to {EXCEL_FILE}")
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
        
    print("Agent Execution Finished.")


if __name__ == "__main__":
    asyncio.run(main())
