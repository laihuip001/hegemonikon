/**
 * AIDB URL収集スクリプト (Enhanced)
 *
 * 改善点:
 * - 総件数カウント機能
 * - 重複URL除去
 * - 進捗レポート
 * - エラーハンドリング強化
 */

const puppeteer = require("puppeteer");
const fs = require("fs");
const path = require("path");

const CONFIG = {
  outputDir: "Raw/aidb/_index",
  outputFile: "url_list.txt",
  reportFile: "collection_report.json",
  categories: [
    "https://ai-data-base.com/archives",
    "https://ai-data-base.com/archives/category/deep-dive",
    "https://ai-data-base.com/archives/category/weekly-papers",
  ],
  // レート制限対策
  delayBetweenPages: 1000,
  maxRetries: 3,
};

async function sleep(ms) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

async function collectURLsFromCategory(page, categoryUrl, allUrls, report) {
  console.log(`\n📂 カテゴリ収集開始: ${categoryUrl}`);
  report.categories[categoryUrl] = { pages: 0, urls: 0, errors: [] };

  let pageNum = 1;
  let retryCount = 0;

  try {
    await page.goto(categoryUrl, { waitUntil: "networkidle2", timeout: 30000 });
  } catch (error) {
    console.error(`  ❌ カテゴリアクセス失敗: ${error.message}`);
    report.categories[categoryUrl].errors.push(error.message);
    return;
  }

  while (true) {
    try {
      // 記事リンク収集
      const links = await page.$$eval('a[href*="/articles/"]', (els) =>
        els.map((e) => e.href).filter((url) => url.includes("/articles/")),
      );

      const beforeCount = allUrls.size;
      links.forEach((url) => {
        // URL正規化（末尾スラッシュ統一、クエリ除去）
        const normalizedUrl = url.split("?")[0].replace(/\/$/, "");
        allUrls.add(normalizedUrl);
      });
      const newCount = allUrls.size - beforeCount;

      console.log(
        `  📄 Page ${pageNum}: ${links.length}件発見, ${newCount}件追加 (累計: ${allUrls.size})`,
      );
      report.categories[categoryUrl].pages++;
      report.categories[categoryUrl].urls += newCount;

      // 次ページボタン検索
      const nextButton = await page.$(
        'a[rel="next"], .next, .pagination a:last-child',
      );
      if (!nextButton) {
        console.log(`  ✅ 最終ページ到達`);
        break;
      }

      const isDisabled = await page.evaluate((el) => {
        return (
          el.classList.contains("disabled") ||
          el.getAttribute("aria-disabled") === "true" ||
          el.getAttribute("href") === "#"
        );
      }, nextButton);

      if (isDisabled) {
        console.log(`  ✅ 次ページなし`);
        break;
      }

      await nextButton.click();
      await sleep(CONFIG.delayBetweenPages);
      pageNum++;
      retryCount = 0;
    } catch (error) {
      console.error(`  ⚠️ Page ${pageNum} エラー: ${error.message}`);
      report.categories[categoryUrl].errors.push(
        `Page ${pageNum}: ${error.message}`,
      );

      if (retryCount < CONFIG.maxRetries) {
        retryCount++;
        console.log(`  🔄 リトライ ${retryCount}/${CONFIG.maxRetries}`);
        await sleep(2000 * retryCount); // Exponential backoff
        continue;
      }
      break;
    }
  }
}

async function main() {
  console.log("🚀 AIDB URL収集開始");
  console.log("=".repeat(50));

  const startTime = Date.now();
  const allUrls = new Set();
  const report = {
    startTime: new Date().toISOString(),
    endTime: null,
    totalUrls: 0,
    categories: {},
    errors: [],
  };

  // 出力ディレクトリ確認
  if (!fs.existsSync(CONFIG.outputDir)) {
    fs.mkdirSync(CONFIG.outputDir, { recursive: true });
  }

  const browser = await puppeteer.launch({
    headless: true,
    args: ["--no-sandbox", "--disable-setuid-sandbox"],
  });

  try {
    const page = await browser.newPage();
    await page.setUserAgent(
      "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    );

    for (const categoryUrl of CONFIG.categories) {
      await collectURLsFromCategory(page, categoryUrl, allUrls, report);
      await sleep(2000); // カテゴリ間の待機
    }
  } catch (error) {
    console.error(`❌ 致命的エラー: ${error.message}`);
    report.errors.push(error.message);
  } finally {
    await browser.close();
  }

  // 結果保存
  const urlList = Array.from(allUrls).sort();
  const outputPath = path.join(CONFIG.outputDir, CONFIG.outputFile);
  fs.writeFileSync(outputPath, urlList.join("\n"));

  report.endTime = new Date().toISOString();
  report.totalUrls = urlList.length;
  report.durationSeconds = Math.round((Date.now() - startTime) / 1000);

  const reportPath = path.join(CONFIG.outputDir, CONFIG.reportFile);
  fs.writeFileSync(reportPath, JSON.stringify(report, null, 2));

  // 最終レポート
  console.log("\n" + "=".repeat(50));
  console.log("📊 収集完了レポート");
  console.log("=".repeat(50));
  console.log(`総URL数: ${report.totalUrls}件`);
  console.log(`所要時間: ${report.durationSeconds}秒`);
  console.log(`出力ファイル: ${outputPath}`);
  console.log(`レポート: ${reportPath}`);

  Object.entries(report.categories).forEach(([cat, data]) => {
    console.log(`\n  ${cat}`);
    console.log(`    ページ数: ${data.pages}, URL数: ${data.urls}`);
    if (data.errors.length > 0) {
      console.log(`    エラー: ${data.errors.length}件`);
    }
  });

  return report.totalUrls;
}

main()
  .then((count) => {
    console.log(`\n✅ 完了: ${count}件のURLを収集`);
    process.exit(0);
  })
  .catch((error) => {
    console.error(`\n❌ 失敗: ${error.message}`);
    process.exit(1);
  });
