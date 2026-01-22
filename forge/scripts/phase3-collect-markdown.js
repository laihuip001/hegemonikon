/**
 * AIDB Markdown収集スクリプト (Hardened)
 * 
 * 改善点:
 * - 差分収集モード（既存URLスキップ）
 * - Exponential Backoff
 * - セッション検証
 * - 3段階フォールバック
 * - 詳細ログ
 */

const puppeteer = require('puppeteer');
const TurndownService = require('turndown');
const { Readability } = require('@mozilla/readability');
const { JSDOM } = require('jsdom');
const fs = require('fs');
const path = require('path');
const crypto = require('crypto');

const CONFIG = {
  indexDir: 'Raw/aidb/_index',
  urlListFile: 'url_list_retry.txt',
  manifestFile: 'manifest_retry.jsonl',
  logFile: 'capture_log.csv',
  cookieFile: 'cookies.json',
  outputBaseDir: 'Raw/aidb',
  
  // レート制限対策
  baseDelay: 1000,
  maxRetries: 3,
  backoffMultiplier: 2,
  
  // バッチ処理
  batchSize: 10,
  batchDelay: 5000,
  
  // 進捗保存間隔
  saveInterval: 5
};

const turndownService = new TurndownService({
  headingStyle: 'atx',
  codeBlockStyle: 'fenced'
});

// ========================================
// ユーティリティ関数
// ========================================

function sleep(ms) {
  return new Promise(resolve => setTimeout(resolve, ms));
}

function sanitizeFilename(str) {
  return str
    .replace(/[\x00-\x1F\x7F]/g, '')
    .replace(/[<>:"/\\|?*]/g, '')
    .replace(/\s+/g, '-')
    .substring(0, 80);
}

function getOutputPath(capturedAt) {
  const year = capturedAt.substring(0, 4);
  const month = capturedAt.substring(5, 7);
  return path.join(CONFIG.outputBaseDir, year, month);
}

// ========================================
// 差分収集: 既存URL読み込み
// ========================================

function loadExistingUrls() {
  const manifestPath = path.join(CONFIG.indexDir, CONFIG.manifestFile);
  const existingUrls = new Set();
  
  if (fs.existsSync(manifestPath)) {
    const lines = fs.readFileSync(manifestPath, 'utf-8').split('\n').filter(Boolean);
    lines.forEach(line => {
      try {
        const entry = JSON.parse(line);
        if (entry.url && entry.status === 'success') {
          existingUrls.add(entry.url);
        }
      } catch (e) {
        // 無視
      }
    });
    console.log(`📋 既存成功URL: ${existingUrls.size}件（スキップ対象）`);
  }
  
  return existingUrls;
}

// ========================================
// セッション検証
// ========================================

async function validateSession(page) {
  console.log('🔐 セッション検証中...');
  
  try {
    // プレミアム記事にアクセスして認証状態を確認
    await page.goto('https://ai-data-base.com/archives', { 
      waitUntil: 'networkidle2', 
      timeout: 30000 
    });
    
    // ログイン状態の確認（サイト固有のセレクタに調整が必要な場合あり）
    const isLoggedIn = await page.evaluate(() => {
      // 一般的なログイン状態の確認方法
      return document.cookie.includes('session') || 
             document.querySelector('.logout, .user-menu, .premium-badge') !== null;
    });
    
    if (isLoggedIn) {
      console.log('✅ セッション有効');
      return true;
    } else {
      console.log('⚠️ セッション無効またはログアウト状態');
      return false;
    }
  } catch (error) {
    console.error(`❌ セッション検証エラー: ${error.message}`);
    return false;
  }
}

// ========================================
// Exponential Backoff付きリトライ
// ========================================

async function fetchWithRetry(page, url, retries = CONFIG.maxRetries) {
  for (let attempt = 1; attempt <= retries; attempt++) {
    try {
      const response = await page.goto(url, { 
        waitUntil: 'networkidle2', 
        timeout: 30000 
      });
      
      const status = response?.status() || 0;
      
      if (status === 429 || status === 503) {
        throw new Error(`Rate limited (${status})`);
      }
      
      if (status >= 400) {
        throw new Error(`HTTP ${status}`);
      }
      
      await sleep(CONFIG.baseDelay);
      return true;
      
    } catch (error) {
      const delay = CONFIG.baseDelay * Math.pow(CONFIG.backoffMultiplier, attempt);
      console.log(`  ⚠️ Attempt ${attempt}/${retries} 失敗: ${error.message}`);
      
      if (attempt < retries) {
        console.log(`  ⏳ ${delay/1000}秒待機後リトライ...`);
        await sleep(delay);
      } else {
        throw error;
      }
    }
  }
}

// ========================================
// コンテンツ変換（3段階フォールバック）
// ========================================

async function convertToMarkdown(page, url) {
  const html = await page.content();
  
  // 手段1: Readability + Turndown
  try {
    const dom = new JSDOM(html, { url });
    const reader = new Readability(dom.window.document);
    const article = reader.parse();
    
    if (article && article.content && article.content.length > 500) {
      return {
        markdown: turndownService.turndown(article.content),
        method: 'Readability+Turndown',
        title: article.title || null
      };
    }
  } catch (e) {
    console.log(`    Readability失敗: ${e.message}`);
  }
  
  // 手段2: 本文セレクタ直接 + Turndown
  try {
    const mainContent = await page.$eval(
      'article, .post-content, .entry-content, main, .content',
      el => el.innerHTML
    );
    
    if (mainContent && mainContent.length > 500) {
      return {
        markdown: turndownService.turndown(mainContent),
        method: 'Selector+Turndown',
        title: null
      };
    }
  } catch (e) {
    console.log(`    セレクタ抽出失敗: ${e.message}`);
  }
  
  // 手段3: 全HTML変換
  try {
    return {
      markdown: turndownService.turndown(html),
      method: 'FullHTML+Turndown',
      title: null
    };
  } catch (e) {
    // 手段4: HTMLバックアップ
    return {
      html: html,
      method: 'HTMLBackup',
      title: null
    };
  }
}

// ========================================
// 単一URL処理
// ========================================

async function processUrl(page, url, index, total) {
  console.log(`[${index}/${total}] ${url}`);
  
  const capturedAt = new Date().toISOString();
  const result = {
    url,
    capturedAt,
    status: 'pending'
  };
  
  try {
    await fetchWithRetry(page, url);
    
    // メタデータ取得
    const metadata = await page.evaluate(() => ({
      title: document.querySelector('h1, .post-title, .entry-title')?.textContent.trim() || 'Untitled',
      category: document.querySelector('.category, .post-category, .tag')?.textContent.trim() || 'unknown',
      isPremium: document.querySelector('.premium, .lock, .members-only') !== null,
      publishDate: document.querySelector('time')?.getAttribute('datetime') || null
    }));
    
    // 変換
    const converted = await convertToMarkdown(page, url);
    
    // ファイル名生成
    const slug = url.split('/').filter(Boolean).pop() || `article-${index}`;
    const safeTitle = sanitizeFilename(converted.title || metadata.title);
    const fileName = `${capturedAt.split('T')[0]}__${slug}__${safeTitle}`;
    
    // 保存
    const outputDir = getOutputPath(capturedAt);
    fs.mkdirSync(outputDir, { recursive: true });
    
    if (converted.html) {
      // HTMLバックアップ
      const htmlPath = path.join(outputDir, `${fileName}.html`);
      fs.writeFileSync(htmlPath, converted.html);
      result.file = htmlPath;
    } else {
      // Markdown保存
      const hash = crypto.createHash('sha256').update(converted.markdown).digest('hex').substring(0, 16);
      
      const frontmatter = `---
source_url: ${url}
captured_at: ${capturedAt}
title: "${(converted.title || metadata.title).replace(/"/g, '\\"')}"
category: "${metadata.category}"
is_premium: ${metadata.isPremium}
publish_date: ${metadata.publishDate}
conversion_method: ${converted.method}
file_hash: ${hash}
---

`;
      
      const mdPath = path.join(outputDir, `${fileName}.md`);
      fs.writeFileSync(mdPath, frontmatter + converted.markdown);
      result.file = mdPath;
      result.hash = hash;
    }
    
    result.status = 'success';
    result.method = converted.method;
    result.title = converted.title || metadata.title;
    result.isPremium = metadata.isPremium;
    
    console.log(`  ✅ ${result.method}`);
    
  } catch (error) {
    result.status = 'failed';
    result.error = error.message;
    console.log(`  ❌ ${error.message}`);
  }
  
  return result;
}

// ========================================
// メイン処理
// ========================================

async function main() {
  console.log('🚀 AIDB Markdown収集開始');
  console.log('=' .repeat(60));
  
  const startTime = Date.now();
  
  // URL読み込み
  const urlListPath = path.join(CONFIG.indexDir, CONFIG.urlListFile);
  if (!fs.existsSync(urlListPath)) {
    console.error(`❌ URLリストが見つかりません: ${urlListPath}`);
    console.error('   先に phase2-collect-urls.js を実行してください。');
    process.exit(1);
  }
  
  const allUrls = fs.readFileSync(urlListPath, 'utf-8')
    .split('\n')
    .map(url => url.trim())
    .filter(url => url.length > 0);
  
  console.log(`📋 総URL数: ${allUrls.length}件`);
  
  // 差分収集: 既存URLをスキップ
  const existingUrls = loadExistingUrls();
  const pendingUrls = allUrls.filter(url => !existingUrls.has(url));
  
  console.log(`🎯 収集対象: ${pendingUrls.length}件（${allUrls.length - pendingUrls.length}件スキップ）`);
  
  if (pendingUrls.length === 0) {
    console.log('✅ 全URL収集済み。終了します。');
    return;
  }
  
  // ブラウザ起動
  const browser = await puppeteer.launch({ 
    headless: true,
    args: ['--no-sandbox', '--disable-setuid-sandbox']
  });
  
  const page = await browser.newPage();
  await page.setUserAgent('Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36');
  
  // Cookie読み込み
  const cookiePath = path.join(CONFIG.indexDir, CONFIG.cookieFile);
  if (fs.existsSync(cookiePath)) {
    try {
      const cookies = JSON.parse(fs.readFileSync(cookiePath, 'utf-8'));
      await page.setCookie(...cookies);
      console.log('🍪 Cookie読み込み完了');
    } catch (e) {
      console.warn(`⚠️ Cookie読み込み失敗: ${e.message}`);
    }
  } else {
    console.warn('⚠️ Cookie未設定。プレミアム記事は取得できない可能性があります。');
  }
  
  // セッション検証
  const sessionValid = await validateSession(page);
  if (!sessionValid) {
    console.warn('⚠️ 認証なしで続行します。プレミアム記事は制限される可能性があります。');
  }
  
  // 出力ストリーム
  const manifestPath = path.join(CONFIG.indexDir, CONFIG.manifestFile);
  const logPath = path.join(CONFIG.indexDir, CONFIG.logFile);
  
  const manifestStream = fs.createWriteStream(manifestPath, { flags: 'a' });
  const logStream = fs.createWriteStream(logPath, { flags: 'a' });
  
  // ログヘッダー（新規の場合のみ）
  if (!fs.existsSync(logPath) || fs.statSync(logPath).size === 0) {
    logStream.write('url,status,captured_at,method,error\n');
  }
  
  // 処理
  let successCount = 0;
  let failCount = 0;
  
  for (let i = 0; i < pendingUrls.length; i++) {
    const result = await processUrl(page, pendingUrls[i], i + 1, pendingUrls.length);
    
    // Manifest記録
    if (result.status === 'success') {
      manifestStream.write(JSON.stringify(result) + '\n');
      successCount++;
    } else {
      failCount++;
    }
    
    // Log記録
    const logLine = [
      result.url,
      result.status,
      result.capturedAt,
      result.method || '',
      (result.error || '').replace(/,/g, ';')
    ].join(',');
    logStream.write(logLine + '\n');
    
    // 進捗表示
    if ((i + 1) % CONFIG.saveInterval === 0) {
      console.log(`\n📊 進捗: ${i + 1}/${pendingUrls.length} (成功: ${successCount}, 失敗: ${failCount})`);
    }
    
    // バッチ間待機
    if ((i + 1) % CONFIG.batchSize === 0 && i + 1 < pendingUrls.length) {
      console.log(`\n⏳ バッチ待機 (${CONFIG.batchDelay/1000}秒)...`);
      await sleep(CONFIG.batchDelay);
    }
  }
  
  manifestStream.end();
  logStream.end();
  await browser.close();
  
  // 最終レポート
  const duration = Math.round((Date.now() - startTime) / 1000);
  const successRate = ((successCount / pendingUrls.length) * 100).toFixed(1);
  
  console.log('\n' + '=' .repeat(60));
  console.log('📊 収集完了レポート');
  console.log('=' .repeat(60));
  console.log(`対象URL: ${pendingUrls.length}件`);
  console.log(`成功: ${successCount}件`);
  console.log(`失敗: ${failCount}件`);
  console.log(`成功率: ${successRate}%`);
  console.log(`所要時間: ${Math.floor(duration/60)}分${duration%60}秒`);
  
  if (parseFloat(successRate) < 70) {
    console.log('\n⚠️ 成功率が70%を下回っています。再実行を推奨します。');
  }
}

main()
  .then(() => {
    console.log('\n✅ 完了');
    process.exit(0);
  })
  .catch(error => {
    console.error(`\n❌ 致命的エラー: ${error.message}`);
    process.exit(1);
  });
