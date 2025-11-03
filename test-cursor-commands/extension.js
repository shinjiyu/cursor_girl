const vscode = require('vscode');

function activate(context) {
    console.log('🧪 Test Cursor Commands Extension activated!');
    
    // 启动时自动运行一次
    setTimeout(() => {
        listCursorCommands();
    }, 2000);
    
    // 注册命令：列出所有 Cursor 命令
    context.subscriptions.push(
        vscode.commands.registerCommand('test.listCursorCommands', listCursorCommands)
    );
    
    // 注册命令：测试所有 Cursor 命令
    context.subscriptions.push(
        vscode.commands.registerCommand('test.testCursorCommands', testCursorCommands)
    );
}

async function listCursorCommands() {
    console.log('=' .repeat(80));
    console.log('📋 Listing Cursor Commands');
    console.log('=' .repeat(80));
    
    try {
        const allCommands = await vscode.commands.getCommands(true);
        
        const cursorCommands = allCommands.filter(cmd => 
            cmd.includes('cursor') || 
            cmd.includes('aichat') || 
            cmd.includes('composer') ||
            cmd.includes('ai.')
        ).sort();
        
        console.log(`\n找到 ${cursorCommands.length} 个 Cursor 相关命令:\n`);
        cursorCommands.forEach((cmd, i) => {
            console.log(`${i + 1}. ${cmd}`);
        });
        
        console.log('\n' + '=' .repeat(80));
        
        vscode.window.showInformationMessage(
            `找到 ${cursorCommands.length} 个 Cursor 命令，查看 Console 了解详情`
        );
        
        return cursorCommands;
        
    } catch (error) {
        console.error('❌ Error:', error);
        vscode.window.showErrorMessage('Error: ' + error.message);
    }
}

async function testCursorCommands() {
    console.log('=' .repeat(80));
    console.log('🧪 Testing Cursor Commands');
    console.log('=' .repeat(80));
    
    try {
        const allCommands = await vscode.commands.getCommands(true);
        
        const cursorCommands = allCommands.filter(cmd => 
            cmd.includes('cursor') || 
            cmd.includes('aichat') || 
            cmd.includes('composer')
        ).sort();
        
        console.log(`\n测试 ${cursorCommands.length} 个命令...\n`);
        
        const results = [];
        
        for (const cmd of cursorCommands) {
            try {
                console.log(`测试: ${cmd}...`);
                const result = await vscode.commands.executeCommand(cmd);
                
                const resultStr = result !== undefined 
                    ? JSON.stringify(result).substring(0, 100)
                    : 'undefined';
                    
                console.log(`  ✅ 成功! 返回: ${resultStr}`);
                
                results.push({
                    command: cmd,
                    success: true,
                    result: result
                });
                
            } catch (error) {
                console.log(`  ❌ 失败: ${error.message}`);
                
                results.push({
                    command: cmd,
                    success: false,
                    error: error.message
                });
            }
        }
        
        // 生成报告
        console.log('\n' + '=' .repeat(80));
        console.log('📊 测试报告');
        console.log('=' .repeat(80));
        
        const successful = results.filter(r => r.success);
        const failed = results.filter(r => !r.success);
        
        console.log(`\n✅ 成功: ${successful.length}`);
        console.log(`❌ 失败: ${failed.length}\n`);
        
        if (successful.length > 0) {
            console.log('✅ 可用命令:');
            successful.forEach(r => {
                console.log(`  - ${r.command}`);
            });
            console.log('');
        }
        
        if (failed.length > 0) {
            console.log('❌ 不可用命令 (可能需要参数):');
            failed.forEach(r => {
                console.log(`  - ${r.command}`);
                console.log(`    原因: ${r.error}`);
            });
            console.log('');
        }
        
        console.log('=' .repeat(80));
        
        // 显示通知
        vscode.window.showInformationMessage(
            `测试完成! 成功: ${successful.length}, 失败: ${failed.length}`
        );
        
        // 创建结果文件
        const resultText = generateResultText(results);
        const doc = await vscode.workspace.openTextDocument({
            content: resultText,
            language: 'markdown'
        });
        await vscode.window.showTextDocument(doc);
        
        return results;
        
    } catch (error) {
        console.error('❌ Error:', error);
        vscode.window.showErrorMessage('Error: ' + error.message);
    }
}

function generateResultText(results) {
    const successful = results.filter(r => r.success);
    const failed = results.filter(r => !r.success);
    
    let text = '# Cursor Commands Test Results\n\n';
    text += `**Date**: ${new Date().toISOString()}\n\n`;
    text += `**Total**: ${results.length}\n`;
    text += `**Successful**: ${successful.length}\n`;
    text += `**Failed**: ${failed.length}\n\n`;
    
    text += '---\n\n';
    
    if (successful.length > 0) {
        text += '## ✅ Available Commands\n\n';
        successful.forEach(r => {
            text += `### \`${r.command}\`\n\n`;
            if (r.result !== undefined) {
                text += '**Returns**: \n```json\n' + JSON.stringify(r.result, null, 2) + '\n```\n\n';
            } else {
                text += '**Returns**: `undefined`\n\n';
            }
        });
    }
    
    if (failed.length > 0) {
        text += '## ❌ Unavailable Commands\n\n';
        failed.forEach(r => {
            text += `### \`${r.command}\`\n\n`;
            text += `**Error**: ${r.error}\n\n`;
        });
    }
    
    return text;
}

function deactivate() {}

module.exports = {
    activate,
    deactivate
};

