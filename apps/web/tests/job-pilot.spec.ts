import { expect, test } from '@playwright/test'

test('complete local-first seeker flow', async ({ page }) => {
  const consoleErrors: string[] = []
  const failedApiResponses: string[] = []
  page.on('console', (message) => {
    if (message.type() === 'error') consoleErrors.push(message.text())
  })
  page.on('response', (response) => {
    if (response.url().includes('/api/') && response.status() >= 400) {
      failedApiResponses.push(`${response.status()} ${response.url()}`)
    }
  })

  await page.goto('/')
  await expect(page.getByRole('heading', { name: 'Job Pilot' })).toBeVisible()
  await expect(page.getByRole('link', { name: 'Start setup' })).toBeVisible()

  await page.goto('/jobs')
  await expect(page).toHaveURL(/\/onboarding$/)

  await page.getByLabel('Full name').fill('E2E Developer')
  await page.getByLabel('Current title').fill('Backend Engineer')
  await page.getByLabel('Skills notes (optional)').fill('Python, FastAPI, TypeScript, SQL')
  await page.getByRole('button', { name: 'Continue' }).click()

  const resume = [
    'E2E Developer',
    'Backend Engineer',
    ...Array(12).fill(
      'Built Python FastAPI SQL services, TypeScript applications, tests, and production APIs.',
    ),
  ].join('\n')
  await page.getByLabel('Resume file').setInputFiles({
    name: 'resume.txt',
    mimeType: 'text/plain',
    buffer: Buffer.from(resume),
  })
  await expect(page.getByText('Resume loaded successfully.')).toBeVisible()
  await page.getByRole('button', { name: 'Finish setup' }).click()
  await expect(page).toHaveURL(/\/jobs$/)

  await expect(page.getByRole('heading', { name: 'Suggested jobs' })).toBeVisible()
  await expect(page.getByText('Ranked for you from your resume and Memory.')).toBeVisible()
  await expect(page.locator('.list li')).toHaveCount(3)

  await page.getByRole('button', { name: 'Paste a job you found' }).click()
  const manualJd =
    'Platform engineer for Python FastAPI and SQL services in Tel Aviv. Build reliable APIs and automated tests.'
  await page.getByLabel('Job description').fill(manualJd)
  await page.getByRole('button', { name: 'Add to list' }).click()
  await expect(page.locator('.list li')).toHaveCount(4)

  await page.locator('.list li').first().getByRole('link', { name: 'Tailor CV' }).click()
  await expect(page).toHaveURL(/\/tailor\?jobId=\d+$/)
  await expect(page.getByLabel('Job description (required)')).not.toHaveValue('')
  await page.getByRole('button', { name: 'Generate' }).click()
  await expect(page.getByLabel('Editable CV')).toContainText('E2E Developer')

  const downloadPromise = page.waitForEvent('download')
  await page.getByRole('link', { name: 'Download DOCX' }).click()
  const download = await downloadPromise
  expect(download.suggestedFilename()).toMatch(/job-pilot-cv-\d+\.docx/)

  await page.goto('/alerts')
  await expect(page.getByRole('heading', { name: 'Alerts' })).toBeVisible()
  await page.getByRole('button', { name: 'Add demo alert' }).click()
  await expect(page.getByText('Demo: new matching role · new')).toBeVisible()
  await page.getByRole('button', { name: 'Mark read' }).click()
  await expect(page.getByText('Demo: new matching role · new')).toHaveCount(0)

  await page.setViewportSize({ width: 390, height: 844 })
  await page.goto('/')
  await expect(page.getByRole('heading', { name: 'Job Pilot' })).toBeVisible()
  const hasHorizontalOverflow = await page.evaluate(
    () => document.documentElement.scrollWidth > window.innerWidth,
  )
  expect(hasHorizontalOverflow).toBe(false)

  expect(consoleErrors).toEqual([])
  expect(failedApiResponses).toEqual([])
})
