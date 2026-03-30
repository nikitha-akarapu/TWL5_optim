import asyncio
from playwright.async_api import async_playwright

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()
        
        # Navigate to the web application
        await page.goto("https://dev.urbuddi.com/")
        
        # Perform login
        await page.get_by_text("Dashboard")
        await page.locator("#fromDate")
        await page.locator("#toDate")
        
        # Enter email
        email_input = page.locator("#email")
        await email_input.fill("srikanth123@optimworks.com")
        
        # Enter password
        password_input = page.locator("#password")
        await password_input.fill("Srikanth@123")
        
        # Click login button
        login_button = page.locator("#login")
        await login_button.click()
        
        # Navigate to Leave Management module
        leave_management_link = page.get_by_text("Leave Management")
        await leave_management_link.click()
        
        # Apply for leave on non-working days
        apply_leave_button = page.get_by_text("Apply Leave")
        await apply_leave_button.click()
        
        # Fill leave application form
        from_date_input = page.locator("#fromDate")
        await from_date_input.fill("2024-09-21")
        to_date_input = page.locator("#toDate")
        await to_date_input.fill("2024-09-21")
        reason_input = page.locator("*[name='reason']")
        await reason_input.fill("Taking a day off for personal reasons")
        request_type_input = page.locator("#leave")
        await request_type_input.click()
        
        # Submit leave application
        submit_button = page.get_by_text("Submit")
        await submit_button.click()
        
        # Verify leave application was successful
        assert await page.get_by_text("Leave application submitted successfully")
        
        # Close the browser
        await browser.close()

asyncio.run(main())