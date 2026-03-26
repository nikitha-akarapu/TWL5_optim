import asyncio
import os
import sys
import json
import pandas as pd
import subprocess
from datetime import datetime
from playwright.async_api import async_playwright
from groq import AsyncGroq
from dotenv import load_dotenv
from bs4 import BeautifulSoup

# Load environment variables from .env file
load_dotenv()

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EXCEL_FILE = os.path.join(BASE_DIR, "test_data", "Employee_Creation_Test_Cases.xlsx")
TESTS_DIR = os.path.join(BASE_DIR, "tests")

async def generate_test_cases(client, feature_prompt: str, dom_json_str: str, email: str, password: str):
    print(f"Generating manual test cases for '{feature_prompt}' using Groq AI...")
    prompt = f"""
You are an expert QA Engineer.
Below is the JSON representation of the DOM for the '{feature_prompt}' form from a web application.
The application credentials are Email: {email} and Password: {password}. Use these if applicable.
Analyze the form fields, their types, required attributes, and overall structure based on the provided JSON elements.
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

Form JSON DOM Representation:
{dom_json_str}
"""

    response = await client.chat.completions.create(
        model='llama-3.3-70b-versatile',
        messages=[
            {"role": "system", "content": "You are a helpful QA assistant that outputs strict JSON."},
            {"role": "user", "content": prompt}
        ],
        response_format={"type": "json_object"}
    )
    
    result_text = response.choices[0].message.content
    try:
        data = json.loads(result_text)
        return data.get("test_cases", [])
    except json.JSONDecodeError:
        print("Error parsing the JSON from Groq.")
        return []

def extract_locators_from_html(html_content: str):
    """Parses HTML and returns a map of interactive elements to their best Playwright locators."""
    print("Extracting exact locators from DOM...")
    soup = BeautifulSoup(html_content, 'html.parser')
    locators = []
    
    # Include standard form elements and custom elements with ARIA roles
    elements = soup.find_all(['input', 'button', 'select', 'textarea', 'a', 'mat-select', 'mat-checkbox', 'mat-radio-button'])
    roles_to_find = ["button", "combobox", "menuitem", "tab", "option", "checkbox", "radio", "listbox", "textbox", "switch"]
    elements.extend(soup.find_all(attrs={"role": roles_to_find}))
    
    # Use a set to prevent duplicates, but Tag isn't hashable, so checking id/memory address or converting to string
    seen = set()
    unique_elements = []
    for el in elements:
        if id(el) not in seen:
            seen.add(id(el))
            unique_elements.append(el)
            
    for el in unique_elements:
        tag_name = el.name
        el_type = el.get('type', '')
        
        description = f"<{tag_name}>"
        if el_type: description += f" type='{el_type}'"
        if el.get('role'): description += f" role='{el.get('role')}'"
        if el.get('value'): description += f" value='{el.get('value')}'"
        
        options = []
        
        # Test IDs are the most stable
        if el.get('data-testid'):
            options.append(f"page.get_by_test_id(\"{el.get('data-testid')}\")")
        elif el.get('data-test-id'):
            options.append(f"page.get_by_test_id(\"{el.get('data-test-id')}\")")
            
        # User-facing locators
        if el.get('aria-label'):
            options.append(f"page.get_by_label(\"{el.get('aria-label')}\")")
            
        if el.get('placeholder'):
            options.append(f"page.get_by_placeholder(\"{el.get('placeholder')}\")")
            
        if el.text and el.text.strip():
            clean_text = el.text.strip().replace('"', '\\"')
            if len(clean_text) < 30:
                options.append(f"page.get_by_text(\"{clean_text}\")")
                
        # Less robust locators
        if el.get('name'):
            options.append(f"page.locator(\"*[name='{el.get('name')}']\")")
            
        if el.get('id'):
            el_id = el.get('id')
            # Avoid using IDs that look dynamic (containing digits)
            if not any(char.isdigit() for char in el_id):
                options.append(f"page.locator(\"#{el_id}\")")
        
        if options:
            locators.append(f"- Element: {description} (ID: {el.get('id', 'None')}, Name: {el.get('name', 'None')}, Placeholder: {el.get('placeholder', 'None')})\n  Options: {', '.join(options)}")
            
    return "\n".join(locators) if locators else "No interactive elements found."


async def generate_playwright_script(client, feature_prompt: str, test_case_row: dict, email: str, password: str, dom_json_str: str, locator_map: str):
    prompt = f"""
You are an expert Automation QA Engineer. 
Below is a manual test case and the relevant JSON DOM representation for a '{feature_prompt}' feature on a web application (https://dev.urbuddi.com/).
Your task is to write a standalone Python Playwright test script for this specific manual test case.

Test Case Details:
- Test Case ID: {test_case_row.get('Test Case ID', '')}
- Description: {test_case_row.get('Description', '')}
- Pre-conditions: {test_case_row.get('Pre-conditions', '')}
- Test Steps: {test_case_row.get('Test Steps', '')}
- Expected Result: {test_case_row.get('Expected Result', '')}

Form JSON DOM Representation:
{dom_json_str}

Extracted Available Exact Locators:
{locator_map}

Login Credentials to use in the script:
Email: {email}
Password: {password}

Requirements:
1. Use Playwright's async API (`async_playwright`) and always launch the browser in headed mode: `await p.chromium.launch(headless=False)`.
2. The code should be fully self-contained and runnable, including an `async def test_...()` or a generic `async def main()` executing the test.
3. Automatically perform login using the credentials provided above prior to executing the test steps. 
4. Add appropriate assertions (`assert` or `expect` from `playwright.async_api`).
5. Include clear comments explaining the steps.
6. CAREFULLY analyze the 'Extracted Available Exact Locators' mapping provided above. You MUST USE one of the exact locators from the 'Options' list for every interactive element required to execute the test steps. Select the most robust locator option available (favoring get_by_test_id, get_by_label, get_by_placeholder, or get_by_text).
7. DO NOT HALLUCINATE OR GUESS LOCATORS. NEVER use a `get_by_placeholder` or `get_by_label` if the placeholder or label text does not exactly appear in the Form JSON DOM Representation or Locator map. If an element is absolutely required but not in the map, fallback to robust Playwright XPath or CSS selectors based purely on the 'Form JSON DOM Representation' provided.

Output ONLY the full Python script without any markdown brackets, explanations, or backticks. Start directly with imports.
"""

    try:
        response = await client.chat.completions.create(
            model='llama-3.3-70b-versatile',
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        
        script_code = response.choices[0].message.content.strip()
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
            
        test_script_path_from_root = os.path.join("tests", test_script_name)
        print(f"Running {test_script_path_from_root} from root directory...")
        try:
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
            df.at[index, "Execution Timestamp"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            df.at[index, "Execution Status"] = "Failed (Timeout)"
            df.at[index, "Remarks"] = "Test execution timed out after 300 seconds."
        except Exception as e:
            print(f"  -> {tc_id_clean} ERROR: {e}")
            df.at[index, "Execution Timestamp"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            df.at[index, "Execution Status"] = "Error"
            df.at[index, "Remarks"] = str(e)
            
    return df

async def autonomous_navigate(client, page, user_prompt: str, admin_email: str, admin_password: str):
    print(f"Starting autonomous navigation for goal: '{user_prompt}'")
    system_instruction = f"""You are an autonomous web browser agent.
Your goal is to satisfy the user's prompt by navigating the web application.
Available credentials if needed: Email: {admin_email}, Password: {admin_password}.

At each step, you will receive the current URL and a simplified text representation of the interactive elements on the page.
Respond ONLY with a valid JSON object matching this schema:
{{
  "action": "click" | "fill" | "done" | "wait",
  "locator": "string. The exact string from the 'Options' list of the targeted element (e.g., page.get_by_placeholder('Email')). Leave empty for 'done' or 'wait'.",
  "text": "string. The text to type if action is 'fill'. Leave empty otherwise.",
  "reasoning": "string. Briefly explain why you chose this action."
}}
If you believe you have successfully reached the target form/page and it is visible, return action "done".
"""

    action_history = []
    
    for step in range(15): # Max 15 steps
        await asyncio.sleep(2) # Wait for animations/network
        try:
            await page.wait_for_load_state("networkidle", timeout=3000)
        except Exception:
            pass
            
        html_content = await page.evaluate('''() => {
            // Sync properties to attributes so they appear in HTML
            document.querySelectorAll('input, select, textarea').forEach(el => {
                if (el.type === 'checkbox' || el.type === 'radio') {
                    if (el.checked) el.setAttribute('checked', 'checked');
                    else el.removeAttribute('checked');
                } else {
                    el.setAttribute('value', el.value || '');
                }
            });
            // Remove scripts and SVGs to save tokens
            document.querySelectorAll("script, svg, style").forEach(el => el.remove());
            return document.body.innerHTML;
        }''')
        
        # Limit HTML size if exceptionally large for parsing
        if len(html_content) > 50000:
            html_content_for_extraction = html_content[:50000]
        else:
            html_content_for_extraction = html_content
            
        locator_map = extract_locators_from_html(html_content_for_extraction)
        
        current_url = page.url
        prompt = f"""
User Goal: {user_prompt}
Current URL: {current_url}

Previous Actions Taken:
{json.dumps(action_history, indent=2)}

Interactive Elements on Current Page:
{locator_map}

What is your next action?
"""
        print(f"  [Auto-Nav Step {step+1}] Analyzing page and asking AI for next move...")
        
        try:
            response = await client.chat.completions.create(
                model='llama-3.3-70b-versatile',
                messages=[
                    {"role": "system", "content": system_instruction},
                    {"role": "user", "content": prompt}
                ],
                response_format={"type": "json_object"}
            )
            
            result_text = response.choices[0].message.content
            data = json.loads(result_text)
            
            action = data.get("action")
            locator_str = data.get("locator")
            text = data.get("text")
            reasoning = data.get("reasoning")
            
            print(f"    -> AI Decision: {action} | Locator: {locator_str} | Text: {text}")
            print(f"       Reasoning: {reasoning}")
            
            action_history.append({
                "step": step + 1,
                "action": action,
                "locator": locator_str,
                "text": text,
                "reasoning": reasoning
            })
            
            if action == "done":
                print("    -> AI determined the target page has been reached.")
                break
            elif action == "wait":
                print("    -> Waiting...")
                await asyncio.sleep(3)
            elif action in ["click", "fill"]:
                if locator_str and locator_str.startswith("page."):
                    target_locator = eval(locator_str)
                    if action == "click":
                        await target_locator.first.click(timeout=5000)
                    else:
                        await target_locator.first.fill(text, timeout=5000)
                else:
                    print(f"    -> WARNING: Invalid locator string from AI: {locator_str}")
            else:
                print(f"    -> WARNING: Unknown action: {action}")
                
        except Exception as e:
            print(f"    -> Error during step execution: {e}")
            await asyncio.sleep(2)
            
    print("Autonomous navigation complete.")

async def main():
    if not os.getenv("GROQ_API_KEY"):
        print("ERROR: Please set the GROQ_API_KEY environment variable in .env before running.")
        return

    admin_email = os.getenv("ADMIN_EMAIL", "")
    admin_password = os.getenv("ADMIN_PASSWORD", "")

    if not admin_email or not admin_password:
        print("WARNING: ADMIN_EMAIL or ADMIN_PASSWORD not found in .env.")
        print("The generated automation scripts might not be able to log in successfully.")
        response = input("Do you want to continue anyway? (y/n): ")
        if response.lower() != 'y':
            return

    client = AsyncGroq(api_key=os.getenv("GROQ_API_KEY"))

    feature_prompt = input("Enter your goal (e.g., 'Login with admin@example.com and password123, then open Leave Application'): ")
    if not feature_prompt:
        print("Goal cannot be empty. Exiting.")
        return

    print("Launching browser for autonomous navigation...")
    async with async_playwright() as p:
        # Launch in headed mode to observe AI actions
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context()
        page = await context.new_page()

        target_url = "https://dev.urbuddi.com/"
        print(f"Navigating to {target_url}...")
        await page.goto(target_url)

        # Autonomous Navigation
        await autonomous_navigate(client, page, feature_prompt, admin_email, admin_password)

        print("Extracting final page structure after navigation...")
        print("Extracting full DOM using index.js...")
        dom_json_str = "{}"
        
        # Ensure test_data directory exists
        test_data_dir = os.path.join(BASE_DIR, "test_data")
        os.makedirs(test_data_dir, exist_ok=True)
        
        dom_export_path = os.path.join(test_data_dir, "latest_dom.json")
        try:
            index_js_path = os.path.join(BASE_DIR, "index.js")
            with open(index_js_path, "r", encoding="utf-8") as f:
                index_js_script = f.read()
                
            dom_json = await page.evaluate(f"({index_js_script})()")
            dom_json_str = json.dumps(dom_json, indent=2)
            
            with open(dom_export_path, "w", encoding="utf-8") as f:
                f.write(dom_json_str)
            print(f"Saved exact DOM to {dom_export_path}")
            
            if len(dom_json_str) > 80000:
                dom_json_str = dom_json_str[:80000] + "\n...[truncated]"
        except Exception as e:
            print(f"Error extracting DOM via index.js: {e}")
            
        # We still need locator_map for Playwright script generation fallback!
        html_content = await page.evaluate("() => document.body.innerHTML")
        locator_map = extract_locators_from_html(html_content)
            
        await browser.close()
        
    print(f"Step 1: Generating Test Cases for {feature_prompt}...")
    test_cases_list = await generate_test_cases(client, feature_prompt, dom_json_str, admin_email, admin_password)

    if not test_cases_list:
        print("No test cases generated. Exiting.")
        return
        
    new_df = pd.DataFrame(test_cases_list)
    print(f"Generated {len(new_df)} new test cases.")

    # Create test_data directory if it doesn't exist
    os.makedirs(os.path.dirname(EXCEL_FILE), exist_ok=True)

    if os.path.exists(EXCEL_FILE):
        try:
            existing_df = pd.read_excel(EXCEL_FILE)
            df = pd.concat([existing_df, new_df], ignore_index=True)
            print(f"Loaded {len(existing_df)} existing test cases.")
        except Exception as e:
            print(f"Warning: Could not read existing excel file {e}. Overwriting.")
            df = new_df
    else:
        df = new_df

    # Step 2: Generate Playwright scripts
    print(f"Step 2: Generating Automation Scripts for {feature_prompt}...")
    os.makedirs(TESTS_DIR, exist_ok=True)
    
    if "automation_status" not in df.columns:
        df["automation_status"] = "Pending"
        
    for index, row in df.iterrows():
        automation_status = row.get("automation_status")
        if automation_status == "Generated":
            print(f"[{index+1}/{len(df)}] Skipping script generation for {row.get('Test Case ID', 'Unknown')} (already generated).")
            continue
            
        print(f"[{index+1}/{len(df)}] Generating script for {row.get('Test Case ID', 'Unknown')}...")
        
        script_code = await generate_playwright_script(client, feature_prompt, dict(row), admin_email, admin_password, dom_json_str, locator_map)
        
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
            
        await asyncio.sleep(2) # Prevent Groq rate-limiting

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
