#!/usr/bin/env node
/**
 * 测试 Cursor 的可用命令和 API
 * 在 Cursor 的开发者控制台中运行此脚本
 * 
 * 使用方法：
 * 1. 在 Cursor 中按 Cmd+Shift+P (macOS) 或 Ctrl+Shift+P (Windows)
 * 2. 输入 "Developer: Toggle Developer Tools"
 * 3. 在控制台中粘贴并运行此脚本
 */

console.log('='.repeat(70));
console.log('  🔍 Cursor Commands and API Explorer');
console.log('='.repeat(70));
console.log();

// 测试 1: 获取所有已注册的命令
console.log('📋 1. Registered Commands:');
console.log('-'.repeat(70));

// 注意：这段代码需要在 Cursor 的开发者工具中运行
const exploreCommands = `
(async function() {
    try {
        // 获取所有命令
        const commands = await vscode.commands.getCommands();
        
        // 筛选 Cursor 相关的命令
        const cursorCommands = commands.filter(cmd => 
            cmd.includes('cursor') || 
            cmd.includes('ai') || 
            cmd.includes('chat') ||
            cmd.includes('copilot')
        );
        
        console.log('Total commands:', commands.length);
        console.log('Cursor-related commands:', cursorCommands.length);
        console.log();
        
        console.log('🤖 Cursor/AI Related Commands:');
        cursorCommands.forEach(cmd => console.log('  -', cmd));
        
        return { total: commands.length, cursorCommands };
    } catch (error) {
        console.error('Error:', error);
        return null;
    }
})();
`;

console.log('复制以下代码到 Cursor 开发者工具控制台：');
console.log();
console.log(exploreCommands);
console.log();

// 测试 2: 检查 VSCode API 扩展
console.log('📋 2. VSCode API Extensions:');
console.log('-'.repeat(70));

const exploreAPI = `
(async function() {
    console.log('🔍 Exploring VSCode API...');
    console.log();
    
    // 检查 vscode 对象的属性
    const vscodeProps = Object.keys(vscode).sort();
    console.log('VSCode API namespaces:', vscodeProps);
    console.log();
    
    // 检查是否有 Cursor 特有的 API
    const hasCursorAPI = vscodeProps.some(prop => prop.toLowerCase().includes('cursor'));
    console.log('Has Cursor-specific API:', hasCursorAPI);
    
    // 检查 commands
    if (vscode.commands) {
        console.log('\\n📝 Commands API available:', !!vscode.commands);
    }
    
    // 检查 window
    if (vscode.window) {
        console.log('🪟 Window API available:', !!vscode.window);
        console.log('   - activeTextEditor:', !!vscode.window.activeTextEditor);
        console.log('   - visibleTextEditors:', vscode.window.visibleTextEditors?.length || 0);
    }
    
    return { vscodeProps, hasCursorAPI };
})();
`;

console.log('复制以下代码到 Cursor 开发者工具控制台：');
console.log();
console.log(exploreAPI);
console.log();

// 测试 3: 尝试执行 Cursor 命令
console.log('📋 3. Test Cursor Commands:');
console.log('-'.repeat(70));

const testCommands = `
(async function() {
    console.log('🧪 Testing Cursor Commands...');
    console.log();
    
    // 尝试一些可能的命令名称
    const possibleCommands = [
        'cursor.chat',
        'cursor.ai.chat',
        'cursor.ai.generate',
        'cursor.openChat',
        'cursor.aiChat.open',
        'workbench.action.chat.open',
        'workbench.action.ai.open',
        'editor.action.inlineSuggest.trigger'
    ];
    
    const results = {};
    
    for (const cmd of possibleCommands) {
        try {
            console.log(\`Testing: \${cmd}\`);
            await vscode.commands.executeCommand(cmd);
            results[cmd] = '✅ Success';
            console.log(\`  ✅ Command exists and executed\`);
        } catch (error) {
            results[cmd] = \`❌ \${error.message}\`;
            console.log(\`  ❌ \${error.message}\`);
        }
    }
    
    console.log();
    console.log('📊 Results:');
    console.table(results);
    
    return results;
})();
`;

console.log('复制以下代码到 Cursor 开发者工具控制台：');
console.log();
console.log(testCommands);
console.log();

console.log('='.repeat(70));
console.log('📝 Instructions:');
console.log('='.repeat(70));
console.log();
console.log('1. 在 Cursor 中打开开发者工具：');
console.log('   macOS: Cmd+Shift+P → "Developer: Toggle Developer Tools"');
console.log('   Windows: Ctrl+Shift+P → "Developer: Toggle Developer Tools"');
console.log();
console.log('2. 在控制台中依次复制运行上面的三段代码');
console.log();
console.log('3. 将结果保存下来，我们可以分析 Cursor 的 API 结构');
console.log();
console.log('='.repeat(70));

