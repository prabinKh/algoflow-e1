import { test, expect } from '@playwright/test';

test.describe('Chat System E2E', () => {
  test('Customer can open chat, send message, and Admin can reply', async ({ browser }) => {
    // 1. Create a customer context (incognito)
    const customerContext = await browser.newContext();
    const customerPage = await customerContext.newPage();

    // Navigate to homepage
    await customerPage.goto('/');

    // Wait for the Chat widget floating button and click it
    // The chat widget has a button with aria-label "Open chat" or similar.
    // Let's find it by looking for the MessageSquare icon button.
    const openChatBtn = customerPage.locator('button.bg-primary.text-primary-foreground').filter({ has: customerPage.locator('svg.lucide-message-square') });
    await expect(openChatBtn).toBeVisible({ timeout: 10000 });
    await openChatBtn.click();

    // Verify chat window opens
    const chatInput = customerPage.getByPlaceholder('Type your message...');
    await expect(chatInput).toBeVisible({ timeout: 10000 });

    // Type a message and send
    await chatInput.fill('Hello, I need help with an order!');
    await chatInput.press('Enter');

    // Verify the message appears in the chat window
    await expect(customerPage.getByText('Hello, I need help with an order!')).toBeVisible({ timeout: 10000 });

    // Verify that the AI responds (since CELERY_TASK_ALWAYS_EAGER=True, it should be fast, but we'll wait)
    // The AI might say "I encountered an error" if no API key is present, which is fine, we just want a response.
    await customerPage.waitForResponse(response => response.url().includes('/api/chat/chat-messages/') && response.status() === 201);
    
    // Wait for the message list to update
    await customerPage.waitForTimeout(2000);

    // 2. Create an admin context
    const adminContext = await browser.newContext();
    const adminPage = await adminContext.newPage();

    // Login as admin
    await adminPage.goto('/login');
    await adminPage.getByPlaceholder('name@company.com').fill('staff1@gmail.com');
    await adminPage.getByPlaceholder('••••••••').fill('password123');
    await adminPage.getByRole('button', { name: 'Sign In' }).click();

    // Wait for redirect to admin dashboard
    await adminPage.waitForURL('**/admin**');

    // Go to admin chat page
    await adminPage.goto('/admin/messages');
    
    // Wait for the chat session list to load
    await expect(adminPage.getByText('Messages')).toBeVisible({ timeout: 10000 });

    // The customer message should appear in the session list
    // Click on the most recent session (it should say "Guest" or contain our message)
    const sessionItem = adminPage.locator('button').filter({ hasText: 'Guest' }).first();
    await expect(sessionItem).toBeVisible();
    await sessionItem.click();

    // Reply as admin
    const adminChatInput = adminPage.getByPlaceholder('Type your message...');
    await adminChatInput.fill('Hello! I am a human staff member helping you.');
    await adminChatInput.press('Enter');

    // 3. Verify customer receives the message
    await expect(customerPage.getByText('Hello! I am a human staff member helping you.')).toBeVisible({ timeout: 10000 });

    await customerContext.close();
    await adminContext.close();
  });
});
