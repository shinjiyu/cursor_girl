#!/usr/bin/env node
/**
 * Cursor DOM Inspector - 使用 Playwright 检查 Cursor 的 DOM 结构
 * Cursor DOM Inspector - Inspect Cursor's DOM structure using Playwright
 */

const { _electron: electron } = require('@playwright/test');
const fs = require('fs');
const path = require('path');

// 输出目录
const OUTPUT_DIR = path.join(__dirname, 'cursor_dom_output');

// 确保输出目录存在
if (!fs.existsSync(OUTPUT_DIR)) {
  fs.mkdirSync(OUTPUT_DIR, { recursive: true });
}

// 生成时间戳
function getTimestamp() {
  const now = new Date();
  return now.toISOString().replace(/[:.]/g, '-').slice(0, -5);
}

// 打印分隔线
function printSeparator(title = '') {
  console.log('='.repeat(70));
  if (title) {
    console.log(`  ${title}`);
    console.log('='.repeat(70));
  }
}

// 主函数
async function main() {
  printSeparator('🔍 Cursor DOM Inspector');
  console.log();

  // Cursor 路径（macOS）
  const cursorPath = '/Applications/Cursor.app/Contents/MacOS/Cursor';
  
  console.log(`📍 Cursor Path: ${cursorPath}`);
  console.log();

  // 检查 Cursor 是否存在
  if (!fs.existsSync(cursorPath)) {
    console.error(`❌ Cursor not found at ${cursorPath}`);
    console.error('💡 Please install Cursor or update the path in the script');
    process.exit(1);
  }

  console.log('🚀 Starting Cursor with Playwright...');

  let electronApp;
  try {
    // 启动 Electron 应用
    console.log('⏳ Launching Electron app...');
    electronApp = await electron.launch({
      executablePath: cursorPath,
      // 可选参数
      // args: []
    });

    // 获取主窗口
    console.log('⏳ Waiting for main window...');
    const page = await electronApp.firstWindow();
    
    // 等待页面加载
    console.log('⏳ Waiting for page to load...');
    await page.waitForLoadState('domcontentloaded', { timeout: 30000 });
    
    console.log('✅ Cursor started successfully!');
    console.log();

    // 等待几秒让 UI 完全加载
    console.log('⏳ Waiting 5 seconds for UI to fully load...');
    await page.waitForTimeout(5000);
    console.log();

    // ==================== 获取页面信息 ====================
    printSeparator('📊 Page Information');
    console.log();

    const title = await page.title();
    const url = page.url();

    console.log(`🏷️  Title: ${title}`);
    console.log(`🔗 URL: ${url}`);
    console.log();

    // ==================== 分析 DOM 结构 ====================
    printSeparator('🔍 DOM Structure Analysis');
    console.log();

    const analysis = await page.evaluate(() => {
      // 统计各种元素
      const stats = {
        total_elements: document.querySelectorAll('*').length,
        divs: document.querySelectorAll('div').length,
        buttons: document.querySelectorAll('button').length,
        inputs: document.querySelectorAll('input').length,
        textareas: document.querySelectorAll('textarea').length,
        images: document.querySelectorAll('img').length,
        links: document.querySelectorAll('a').length,
        forms: document.querySelectorAll('form').length,
        iframes: document.querySelectorAll('iframe').length
      };

      // 获取所有按钮的信息
      const buttons = Array.from(document.querySelectorAll('button')).map(btn => ({
        text: btn.textContent.trim().substring(0, 50),
        aria_label: btn.getAttribute('aria-label'),
        class: btn.className,
        id: btn.id
      }));

      // 获取所有输入框的信息
      const inputs = Array.from(document.querySelectorAll('input, textarea')).map(inp => ({
        type: inp.type || inp.tagName.toLowerCase(),
        placeholder: inp.placeholder,
        name: inp.name,
        class: inp.className,
        id: inp.id
      }));

      // 获取主要容器的 class 名
      const main_containers = Array.from(document.querySelectorAll('body > *')).map(el => ({
        tag: el.tagName.toLowerCase(),
        class: el.className,
        id: el.id
      }));

      // 查找可能的编辑器元素
      const editors = Array.from(document.querySelectorAll('[class*="editor"], [class*="monaco"]')).map(el => ({
        tag: el.tagName.toLowerCase(),
        class: el.className.substring(0, 100),
        id: el.id
      }));

      // 查找可能的 AI 相关元素
      const ai_elements = Array.from(document.querySelectorAll('[class*="ai"], [class*="chat"], [aria-label*="AI"], [aria-label*="Chat"]')).map(el => ({
        tag: el.tagName.toLowerCase(),
        class: el.className.substring(0, 100),
        id: el.id,
        aria_label: el.getAttribute('aria-label')
      }));

      return {
        stats,
        buttons: buttons.slice(0, 20),
        inputs: inputs.slice(0, 20),
        main_containers,
        editors: editors.slice(0, 10),
        ai_elements: ai_elements.slice(0, 10)
      };
    });

    // 打印统计信息
    console.log('📊 Element Statistics:');
    for (const [key, value] of Object.entries(analysis.stats)) {
      console.log(`   ${key.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}: ${value}`);
    }
    console.log();

    // 打印按钮信息
    if (analysis.buttons.length > 0) {
      console.log('🔘 Buttons (first 20):');
      analysis.buttons.forEach((btn, i) => {
        const label = btn.aria_label || btn.text || btn.class.substring(0, 30);
        console.log(`   ${i + 1}. ${label}`);
      });
      console.log();
    }

    // 打印输入框信息
    if (analysis.inputs.length > 0) {
      console.log('⌨️  Inputs (first 20):');
      analysis.inputs.forEach((inp, i) => {
        const label = inp.placeholder || inp.name || inp.class.substring(0, 30);
        console.log(`   ${i + 1}. [${inp.type}] ${label}`);
      });
      console.log();
    }

    // 打印主容器
    if (analysis.main_containers.length > 0) {
      console.log('📦 Main Containers:');
      analysis.main_containers.forEach((cont, i) => {
        const label = cont.id || cont.class.substring(0, 50);
        console.log(`   ${i + 1}. <${cont.tag}> ${label}`);
      });
      console.log();
    }

    // 打印编辑器元素
    if (analysis.editors.length > 0) {
      console.log('📝 Editor Elements:');
      analysis.editors.forEach((editor, i) => {
        console.log(`   ${i + 1}. <${editor.tag}> ${editor.class}`);
      });
      console.log();
    }

    // 打印 AI 相关元素
    if (analysis.ai_elements.length > 0) {
      console.log('🤖 AI-related Elements:');
      analysis.ai_elements.forEach((ai, i) => {
        const label = ai.aria_label || ai.class;
        console.log(`   ${i + 1}. <${ai.tag}> ${label}`);
      });
      console.log();
    }

    // 保存分析结果到 JSON
    const analysisFile = path.join(OUTPUT_DIR, `cursor_analysis_${getTimestamp()}.json`);
    fs.writeFileSync(analysisFile, JSON.stringify(analysis, null, 2));
    console.log(`✅ Analysis saved to: ${analysisFile}`);
    console.log();

    // ==================== 获取完整 HTML ====================
    printSeparator('📄 Full HTML Content');
    console.log();

    const html = await page.content();
    const htmlFile = path.join(OUTPUT_DIR, `cursor_full_dom_${getTimestamp()}.html`);
    fs.writeFileSync(htmlFile, html);

    console.log(`✅ Full HTML saved to: ${htmlFile}`);
    console.log(`📏 Size: ${html.length.toLocaleString()} characters`);
    console.log();

    // ==================== 获取 DOM 树 ====================
    printSeparator('🌳 DOM Tree (max depth: 4)');
    console.log();

    const tree = await page.evaluate((maxDepth) => {
      function buildTree(element, depth) {
        if (depth > maxDepth || !element) return null;

        const node = {
          tag: element.tagName.toLowerCase(),
          id: element.id || null,
          class: element.className.toString().substring(0, 80) || null,
          text: element.childNodes.length === 1 && element.childNodes[0].nodeType === 3
            ? element.textContent.trim().substring(0, 50)
            : null,
          children_count: element.children.length,
          children: []
        };

        // 只展示前 5 个子元素
        const children = Array.from(element.children).slice(0, 5);
        for (const child of children) {
          const childNode = buildTree(child, depth + 1);
          if (childNode) {
            node.children.push(childNode);
          }
        }

        return node;
      }

      return buildTree(document.body, 0);
    }, 4);

    // 打印树形结构
    function printTree(node, indent = 0) {
      if (!node) return;

      const prefix = '  '.repeat(indent) + '├─ ';
      const tag = node.tag;
      const id_str = node.id ? `#${node.id}` : '';
      const class_str = node.class ? `.${node.class.substring(0, 30)}` : '';
      const text_str = node.text ? ` "${node.text}"` : '';

      console.log(`${prefix}<${tag}>${id_str}${class_str}${text_str}`);

      for (const child of node.children || []) {
        printTree(child, indent + 1);
      }
    }

    printTree(tree);
    console.log();

    // 保存树结构到 JSON
    const treeFile = path.join(OUTPUT_DIR, `cursor_tree_${getTimestamp()}.json`);
    fs.writeFileSync(treeFile, JSON.stringify(tree, null, 2));
    console.log(`✅ DOM tree saved to: ${treeFile}`);
    console.log();

    // ==================== 截图 ====================
    printSeparator('📸 Screenshot');
    console.log();

    const screenshotFile = path.join(OUTPUT_DIR, `cursor_screenshot_${getTimestamp()}.png`);
    await page.screenshot({ path: screenshotFile });
    console.log(`✅ Screenshot saved to: ${screenshotFile}`);
    console.log();

    // ==================== 完成 ====================
    printSeparator('✅ Test completed successfully!');
    console.log();
    console.log(`📁 All outputs saved to: ${OUTPUT_DIR}`);
    console.log();

    // 等待 3 秒后关闭
    console.log('⏳ Closing in 3 seconds...');
    await page.waitForTimeout(3000);

  } catch (error) {
    console.error('❌ Error:', error.message);
    console.error(error.stack);
    process.exit(1);
  } finally {
    // 关闭应用
    if (electronApp) {
      printSeparator('🛑 Stopping');
      console.log();
      await electronApp.close();
      console.log('✅ Cursor closed');
      console.log();
    }
  }
}

// 运行主函数
main().catch(error => {
  console.error('Fatal error:', error);
  process.exit(1);
});

