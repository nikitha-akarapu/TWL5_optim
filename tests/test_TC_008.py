import asyncio
from playwright.async_api import async_playwright

async def main():
    async with async_playwright() as p:
        # Launch the browser in headed mode
        browser = await p.chromium.launch(headless=False)
        # Create a new browser context
        context = await browser.new_context()
        # Create a new page
        page = await context.new_page()
        # Navigate to the login page
        await page.goto("https://dev.urbuddi.com/")

        # Perform login
        # Get the email input field
        email_input = page.locator("#mat-input-0")
        # Get the password input field
        password_input = page.locator("#mat-input-1")
        # Get the login button
        login_button = page.locator("text=Login")
        # Fill in the email and password
        await email_input.fill("srikanth123@optimworks.com")
        await password_input.fill("Srikanth@123")
        # Click the login button
        await login_button.click()

        # Navigate to the leave management module
        # Get the leave management link
        leave_management_link = page.get_by_text("Leave Management")
        # Click the leave management link
        await leave_management_link.click()

        # Apply for multiple leaves concurrently
        # Get the apply leave button
        apply_leave_button = page.get_by_text("Apply Leave")
        # Click the apply leave button
        await apply_leave_button.click()

        # Fill in the leave application form
        # Get the from date input field
        from_date_input = page.locator("#fromDate")
        # Get the to date input field
        to_date_input = page.locator("#toDate")
        # Get the lead select field
        lead_select = page.locator("*[name='lead']")
        # Get the subject input field
        subject_input = page.locator("*[name='subject']")
        # Get the reason textarea field
        reason_textarea = page.locator("*[name='reason']")
        # Get the request type radio buttons
        leave_radio = page.locator("#leave")
        work_from_home_radio = page.locator("#workFromHome")
        # Get the submit button
        submit_button = page.get_by_text("Submit")

        # Fill in the form fields
        await from_date_input.fill("2024-09-16")
        await to_date_input.fill("2024-09-16")
        await subject_input.fill("Leave Application")
        await reason_textarea.fill("Taking a day off for personal reasons")
        await leave_radio.click()

        # Submit the form
        await submit_button.click()

        # Repeat the process to apply for multiple leaves
        for _ in range(2):
            # Click the apply leave button
            await apply_leave_button.click()

            # Fill in the leave application form
            # Get the from date input field
            from_date_input = page.locator("#fromDate")
            # Get the to date input field
            to_date_input = page.locator("#toDate")
            # Get the lead select field
            lead_select = page.locator("*[name='lead']")
            # Get the subject input field
            subject_input = page.locator("*[name='subject']")
            # Get the reason textarea field
            reason_textarea = page.locator("*[name='reason']")
            # Get the request type radio buttons
            leave_radio = page.locator("#leave")
            work_from_home_radio = page.locator("#workFromHome")
            # Get the submit button
            submit_button = page.get_by_text("Submit")

            # Fill in the form fields
            await from_date_input.fill("2024-09-17")
            await to_date_input.fill("2024-09-17")
            await subject_input.fill("Leave Application")
            await reason_textarea.fill("Taking a day off for personal reasons")
            await leave_radio.click()

            # Submit the form
            await submit_button.click()

        # Assert that the leave applications were successful
        assert await page.get_by_text("Leave Overview").is_visible()
        assert await page.get_by_text("Your History").is_visible()

        # Close the browser
        await browser.close()

# Run the main function
asyncio.run(main())