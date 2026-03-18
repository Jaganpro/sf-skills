#!/usr/bin/env node
/**
 * Salesforce-aware DOM scraper for sf-docs.
 *
 * Reimplements the useful retrieval techniques for Salesforce docs without
 * coupling them to SQLite or a specific storage backend. Output is JSON so the
 * caller can persist raw results locally for later normalization and retrieval.
 *
 * Techniques:
 * - JS rendering with Playwright
 * - deep Shadow DOM traversal
 * - legacy Salesforce docs containers (`doc-content-layout`, `doc-xml-content`)
 * - modern article/main extraction
 * - iframe extraction for older docs
 * - help.salesforce.com longform detection
 */

function parseArgs(argv) {
  const args = { url: null, timeout: 45000 }
  for (let i = 2; i < argv.length; i++) {
    const a = argv[i]
    if (a === '--url') args.url = argv[++i]
    else if (a === '--timeout') args.timeout = Number(argv[++i])
  }
  if (!args.url) throw new Error('--url is required')
  return args
}

function normalizeText(text) {
  return String(text || '')
    .replace(/\u00a0/g, ' ')
    .replace(/\r/g, '')
    .replace(/\n{3,}/g, '\n\n')
    .trim()
}

async function loadPlaywright() {
  const mod = await import('playwright')
  return mod.chromium
}

async function main() {
  const args = parseArgs(process.argv)
  const chromium = await loadPlaywright()
  const browser = await chromium.launch({ headless: true })
  const page = await browser.newPage({
    userAgent: 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
    viewport: { width: 1440, height: 1024 },
  })

  try {
    const response = await page.goto(args.url, { waitUntil: 'networkidle', timeout: args.timeout })
    const httpStatus = response ? response.status() : null
    await page.waitForTimeout(2000)

    const extracted = await page.evaluate(() => {
      const childLinks = new Set()
      const rootsToProcess = [document]

      while (rootsToProcess.length > 0) {
        const current = rootsToProcess.pop()
        if (!current?.querySelectorAll) continue

        const anchors = current.querySelectorAll('a')
        anchors.forEach(a => {
          if (a.href && !a.href.startsWith('javascript:') && !a.href.startsWith('mailto:')) {
            childLinks.add(a.href)
          }
        })

        const all = current.querySelectorAll('*')
        for (let i = 0; i < all.length; i++) {
          if (all[i].shadowRoot) rootsToProcess.push(all[i].shadowRoot)
        }
      }

      const title = document.querySelector('title')?.innerText || document.title || 'Untitled'
      const helpArticleId = new URL(window.location.href).searchParams.get('id') || null

      function getNodeText(node) {
        return node?.innerText?.trim() || ''
      }

      let extractedText = ''
      let strategy = 'body'

      // 1. Classic article/main content first.
      const article = document.querySelector('article')
      const main = document.querySelector('main')
      if (getNodeText(article).length > 500) {
        extractedText = getNodeText(article)
        strategy = 'article'
      } else if (getNodeText(main).length > 500) {
        extractedText = getNodeText(main)
        strategy = 'main'
      }

      // 2. help.salesforce.com longform content found through shadow DOM traversal.
      if (!extractedText) {
        const searchRoots = [document]
        while (searchRoots.length > 0 && !extractedText) {
          const current = searchRoots.pop()
          if (!current?.querySelectorAll) continue
          const found = current.querySelector('.slds-text-longform')
          if (getNodeText(found).length > 250) {
            extractedText = getNodeText(found)
            strategy = 'help-shadow-longform'
            break
          }
          const all = current.querySelectorAll('*')
          for (let i = 0; i < all.length; i++) {
            if (all[i].shadowRoot) searchRoots.push(all[i].shadowRoot)
          }
        }
      }

      // 3. Legacy doc-content-layout shadow slot extraction.
      if (!extractedText) {
        const docLayout = document.querySelector('doc-content-layout')
        if (docLayout?.shadowRoot) {
          const slot = docLayout.shadowRoot.querySelector('.content-body slot')
          if (slot?.assignedElements) {
            const assigned = slot.assignedElements()
            const text = assigned.map(el => getNodeText(el)).join('\n\n').trim()
            if (text.length > 250) {
              extractedText = text
              strategy = 'doc-content-layout'
            }
          }
        }
      }

      // 4. Legacy doc-xml-content/doc-content shadow root extraction.
      if (!extractedText) {
        const docXmlContent = document.querySelector('doc-xml-content')
        if (docXmlContent?.shadowRoot) {
          const docContent = docXmlContent.shadowRoot.querySelector('doc-content')
          if (docContent?.shadowRoot) {
            const text = getNodeText(docContent.shadowRoot)
            if (text.length > 250) {
              extractedText = text
              strategy = 'doc-xml-content'
            }
          }
        }
      }

      // 5. Modern doc-amf-reference markdown-content extraction.
      if (!extractedText) {
        const docRef = document.querySelector('doc-amf-reference')
        const markdownContent = docRef?.querySelector?.('.markdown-content')
        if (getNodeText(markdownContent).length > 250) {
          extractedText = getNodeText(markdownContent)
          strategy = 'doc-amf-reference'
        }
      }

      // 6. Iframe fallback for older/embedded docs.
      if (!extractedText) {
        const iframe = document.querySelector('iframe')
        const iframeDoc = iframe?.contentDocument
        const iframeText = iframeDoc?.body?.innerText?.trim() || ''
        if (iframeText.length > 250) {
          extractedText = iframeText
          strategy = 'iframe'
        }
      }

      // 7. Final body fallback.
      if (!extractedText) {
        extractedText = document.body?.innerText || ''
        strategy = 'body'
      }

      const lowered = extractedText.toLowerCase()
      const likelyShell = [
        'enable javascript',
        'sorry to interrupt',
        'sign in',
        'cookie preferences',
        'skip to main content',
        "we looked high and low",
        "couldn't find that page",
        'salesforce help | article',
        '404 error',
      ].some(token => lowered.includes(token) || title.toLowerCase().includes(token))

      return {
        url: window.location.href,
        title,
        helpArticleId,
        strategy,
        likelyShell,
        text: extractedText,
        childLinks: Array.from(childLinks).slice(0, 200),
      }
    })

    process.stdout.write(JSON.stringify({
      ok: true,
      httpStatus,
      ...extracted,
      text: normalizeText(extracted.text),
    }, null, 2))
  } catch (error) {
    process.stdout.write(JSON.stringify({
      ok: false,
      url: args.url,
      error: String(error?.message || error),
    }, null, 2))
    process.exitCode = 1
  } finally {
    await page.close().catch(() => {})
    await browser.close().catch(() => {})
  }
}

main().catch(err => {
  console.error(JSON.stringify({ ok: false, error: String(err?.message || err) }, null, 2))
  process.exit(1)
})
