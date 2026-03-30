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
        
        # Navigate to the URL
        await page.goto("https://dev.urbuddi.com/")
        
        # Enter email and password
        await page.locator("#email").fill("srikanth123@optimworks.com")
        await page.locator("#password").fill("Srikanth@123")
        
        # Click the login button
        await page.locator("#login").click()
        
        # Wait for the dashboard to load
        await page.wait_for_selector("text=Dashboard")
        
        # Click on the Leave Management link
        await page.get_by_text("Leave Management").click()
        
        # Wait for the Leave Management page to load
        await page.wait_for_selector("text=Leave Overview")
        
        # Click on the Apply Leave button
        await page.get_by_text("Apply Leave").click()
        
        # Wait for the Leave Application form to load
        await page.wait_for_selector("text=Leave Application")
        
        # Fill in the leave application form
        await page.locator("*[name='fromDate']").fill("2024-09-16")
        await page.locator("*[name='toDate']").fill("2024-09-16")
        await page.locator("*[name='subject']").fill("Leave Application")
        await page.locator("*[name='reason']").fill("Taking a day off for personal reasons")
        await page.locator("#leave").click()
        
        # Submit the leave application
        await page.get_by_text("Submit").click()
        
        # Assert that the leave application was submitted successfully
        assert await page.wait_for_selector("text=Leave Application submitted successfully")
        
        # Close the browser
        await browser.close()

asyncio.run(main())