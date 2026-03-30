import asyncio
from playwright.async_api import async_playwright

async def main():
    async with async_playwright() as p:
        # Launch the browser in headed mode
        browser = await p.chromium.launch(headless=False)
        # Create a new context
        context = await browser.new_context()
        # Create a new page
        page = await context.new_page()
        
        # Navigate to the login page
        await page.goto("https://dev.urbuddi.com/")
        
        # Enter the email
        await page.fill("input[type='email']", "srikanth123@optimworks.com")
        
        # Enter the password
        await page.fill("input[type='password']", "Srikanth@123")
        
        # Click the login button
        await page.click("text='Login'")
        
        # Wait for the dashboard to load
        await page.wait_for_selector("text='Dashboard'")
        
        # Navigate to the leave management module
        await page.click("text='Leave Management'")
        
        # Wait for the leave management page to load
        await page.wait_for_selector("text='Leave Overview'")
        
        # Apply the leave
        await page.click("text='Apply Leave'")
        
        # Wait for the apply leave page to load
        await page.wait_for_selector("text='Leave Application'")
        
        # Fill in the leave application form
        await page.fill("#fromDate", "2024-09-16")
        await page.fill("#toDate", "2024-09-16")
        await page.select_option("select", "mounikareddy@gmail.com")
        await page.fill("input[name='subject']", "Leave Application")
        await page.fill("textarea[name='reason']", "Taking a day off for personal reasons")
        await page.check("input[name='requestType']", "leave")
        
        # Submit the leave application
        await page.click("text='Submit'")
        
        # Wait for the leave application to be submitted
        await page.wait_for_selector("text='Requests'")
        
        # Assert that the leave application was submitted successfully
        assert await page.is_visible("text='Requests'")

asyncio.run(main())