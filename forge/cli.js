#!/usr/bin/env node

/**
 * Forge CLI - 認知ハイパーバイザー・プロンプトシステム
 * 
 * 使用方法:
 *   node cli.js [command] [options]
 * 
 * コマンド:
 *   list              - 利用可能なモジュール一覧を表示
 *   load <module>     - モジュールを読み込み表示
 *   search <keyword>  - キーワードでモジュールを検索
 *   tree              - ディレクトリ構造を表示
 */

const fs = require('fs');
const path = require('path');
const readline = require('readline');

// カラー出力用
const colors = {
  reset: '\x1b[0m',
  bright: '\x1b[1m',
  dim: '\x1b[2m',
  cyan: '\x1b[36m',
  green: '\x1b[32m',
  yellow: '\x1b[33m',
  red: '\x1b[31m',
  magenta: '\x1b[35m'
};

// ベースディレクトリ
const BASE_DIR = __dirname;

// ディレクトリマッピング
const DIRECTORIES = {
  find: path.join(BASE_DIR, 'modules', 'find'),
  expand: path.join(BASE_DIR, 'modules', 'think', 'expand'),
  focus: path.join(BASE_DIR, 'modules', 'think', 'focus'),
  prepare: path.join(BASE_DIR, 'modules', 'act', 'prepare'),
  create: path.join(BASE_DIR, 'modules', 'act', 'create'),
  reflect: path.join(BASE_DIR, 'modules', 'reflect'),
  protocols: path.join(BASE_DIR, 'protocols'),
  knowledge: path.join(BASE_DIR, 'knowledge'),
  helpers: path.join(BASE_DIR, 'helpers')
};

// カテゴリ表示名
const CATEGORY_NAMES = {
  find: '🔎 見つける (Find)',
  expand: '🧠📊 考える/広げる (Think/Expand)',
  focus: '🧠🎯 考える/絞る (Think/Focus)',
  prepare: '⚡🔧 働きかける/固める (Act/Prepare)',
  create: '⚡✨ 働きかける/生み出す (Act/Create)',
  reflect: '🔄 振り返る (Reflect)',
  protocols: '🛡️ プロトコル (Protocols)',
  knowledge: '📚 知識ベース (Knowledge)',
  helpers: '🔧 ヘルパー (Helpers)'
};

/**
 * ディレクトリ内のモジュールを取得
 */
function getModulesInDirectory(dirPath) {
  if (!fs.existsSync(dirPath)) {
    return [];
  }
  return fs.readdirSync(dirPath)
    .filter(file => file.endsWith('.md'))
    .map(file => ({
      name: file.replace('.md', ''),
      path: path.join(dirPath, file)
    }));
}

/**
 * 全モジュールを取得
 */
function getAllModules() {
  const modules = {};
  for (const [category, dirPath] of Object.entries(DIRECTORIES)) {
    modules[category] = getModulesInDirectory(dirPath);
  }
  return modules;
}

/**
 * モジュール一覧を表示
 */
function listModules(category = null) {
  const modules = getAllModules();
  
  console.log(`\n${colors.bright}${colors.cyan}🔥 Forge - モジュール一覧${colors.reset}\n`);
  
  for (const [cat, mods] of Object.entries(modules)) {
    if (category && cat !== category) continue;
    if (mods.length === 0) continue;
    
    console.log(`${colors.yellow}${CATEGORY_NAMES[cat]}${colors.reset} (${mods.length})`);
    mods.forEach(mod => {
      console.log(`  ${colors.dim}•${colors.reset} ${mod.name}`);
    });
    console.log();
  }
}

/**
 * モジュールを読み込み
 */
function loadModule(moduleName) {
  const modules = getAllModules();
  
  // 全カテゴリから検索
  for (const [category, mods] of Object.entries(modules)) {
    const found = mods.find(m => 
      m.name.toLowerCase().includes(moduleName.toLowerCase())
    );
    if (found) {
      console.log(`\n${colors.bright}${colors.green}📄 ${found.name}${colors.reset}`);
      console.log(`${colors.dim}カテゴリ: ${CATEGORY_NAMES[category]}${colors.reset}`);
      console.log(`${colors.dim}${'─'.repeat(60)}${colors.reset}\n`);
      
      const content = fs.readFileSync(found.path, 'utf-8');
      console.log(content);
      return true;
    }
  }
  
  console.log(`${colors.red}エラー: モジュール "${moduleName}" が見つかりません${colors.reset}`);
  return false;
}

/**
 * モジュールを検索
 */
function searchModules(keyword) {
  const modules = getAllModules();
  const results = [];
  
  for (const [category, mods] of Object.entries(modules)) {
    for (const mod of mods) {
      if (mod.name.toLowerCase().includes(keyword.toLowerCase())) {
        results.push({ ...mod, category });
        continue;
      }
      
      // ファイル内容も検索
      try {
        const content = fs.readFileSync(mod.path, 'utf-8');
        if (content.toLowerCase().includes(keyword.toLowerCase())) {
          results.push({ ...mod, category });
        }
      } catch (e) {}
    }
  }
  
  console.log(`\n${colors.bright}${colors.cyan}🔍 検索結果: "${keyword}"${colors.reset}`);
  console.log(`${colors.dim}${results.length} 件見つかりました${colors.reset}\n`);
  
  results.forEach(r => {
    console.log(`  ${colors.yellow}${CATEGORY_NAMES[r.category]}${colors.reset}`);
    console.log(`    ${colors.dim}•${colors.reset} ${r.name}`);
  });
}

/**
 * ディレクトリツリーを表示
 */
function showTree() {
  console.log(`\n${colors.bright}${colors.cyan}🔥 Forge - ディレクトリ構造${colors.reset}\n`);
  const modules = getAllModules();
  
  const tree = `
Forge/
├── 📄 README.md
├── 📄 The Cognitive Hypervisor Architecture.md
│
├── modules/
│   ├── find/                  (${modules.find.length} files)
│   ├── think/
│   │   ├── expand/            (${modules.expand.length} files)
│   │   └── focus/             (${modules.focus.length} files)
│   ├── act/
│   │   ├── prepare/           (${modules.prepare.length} files)
│   │   └── create/            (${modules.create.length} files)
│   └── reflect/               (${modules.reflect.length} files)
│
├── protocols/                 (${modules.protocols.length} files)
├── knowledge/                 (${modules.knowledge.length} files)
└── helpers/                   (${modules.helpers.length} files)
`;
  
  console.log(tree);
}

/**
 * ヘルプを表示
 */
function showHelp() {
  console.log(`
${colors.bright}${colors.cyan}🔥 Forge CLI - 認知ハイパーバイザー・プロンプトシステム${colors.reset}

${colors.yellow}使用方法:${colors.reset}
  node cli.js <command> [options]

${colors.yellow}コマンド:${colors.reset}
  ${colors.green}list${colors.reset} [category]     モジュール一覧を表示
                       カテゴリ: find, expand, focus, prepare, create, reflect, protocols, knowledge, helpers
  
  ${colors.green}load${colors.reset} <module>       モジュールを読み込み表示
                       例: node cli.js load "決断を下す"
  
  ${colors.green}search${colors.reset} <keyword>    キーワードでモジュールを検索
                       例: node cli.js search "TDD"
  
  ${colors.green}tree${colors.reset}                ディレクトリ構造を表示
  
  ${colors.green}help${colors.reset}                このヘルプを表示

${colors.yellow}例:${colors.reset}
  node cli.js list
  node cli.js list protocols
  node cli.js load "Module 04"
  node cli.js search "推論"
`);
}

/**
 * メイン
 */
function main() {
  const args = process.argv.slice(2);
  const command = args[0];
  const param = args.slice(1).join(' ');
  
  switch (command) {
    case 'list':
      listModules(param || null);
      break;
    case 'load':
      if (!param) {
        console.log(`${colors.red}エラー: モジュール名を指定してください${colors.reset}`);
        return;
      }
      loadModule(param);
      break;
    case 'search':
      if (!param) {
        console.log(`${colors.red}エラー: 検索キーワードを指定してください${colors.reset}`);
        return;
      }
      searchModules(param);
      break;
    case 'tree':
      showTree();
      break;
    case 'help':
    case '--help':
    case '-h':
    default:
      showHelp();
      break;
  }
}

main();
