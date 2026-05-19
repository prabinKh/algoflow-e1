import { test, expect } from '@playwright/test';

test('Verify Add Product Sync Flow', async ({ page }) => {
  // 1. Navigate to Add Product page
  console.log('Navigating to Add Product page...');
  await page.goto('http://localhost:3000/admin/products/add');

  // 2. Fill form
  console.log('Filling form...');
  await page.fill('input[placeholder*="name"]', 'Playwright Sync Test');
  await page.fill('input[placeholder*="slug"]', 'playwright-sync-' + Date.now());
  
  // Set Price with comma
  await page.fill('input[placeholder*="price"]', '2,499.00');
  
  // Set Brand
  await page.fill('input[placeholder*="brand"]', 'Sony');
  
  // Set Description
  await page.fill('textarea', 'End-to-end sync test using Playwright.');

  // 3. Intercept Network Request
  console.log('Setting up network interception...');
  const responsePromise = page.waitForResponse(response => 
    response.url().includes('/api/admin/products/') && response.request().method() === 'POST'
  );

  // 4. Submit
  console.log('Clicking Save Product...');
  await page.click('button:has-text("Save Product")');

  // 5. Verify Response
  const response = await responsePromise;
  const status = response.status();
  const body = await response.json();
  
  console.log(`Backend Response Status: ${status}`);
  console.log('Backend Response Body:', JSON.stringify(body, null, 2));

  expect(status).toBe(201);
  console.log('✅ SUCCESS: Product created and sync verified!');
});
