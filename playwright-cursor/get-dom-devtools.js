// ============================================================================
// Cursor DOM 结构获取脚本
// 使用方法:
// 1. 在 Cursor 中按 Cmd+Shift+I (macOS) 或 Ctrl+Shift+I (Windows) 打开 DevTools
// 2. 切换到 Console 标签
// 3. 复制并粘贴整个脚本
// 4. 按 Enter 运行
// 5. 结果会保存到 console，可以右键 → Save as... 保存
// ============================================================================

console.log('🔍 开始获取 Cursor DOM 结构...');
console.log('');

// 递归获取元素结构
function getElementStructure(element, depth = 0, maxDepth = 3) {
    if (depth > maxDepth || !element) {
        return null;
    }
    
    const info = {
        tag: element.tagName ? element.tagName.toLowerCase() : element.nodeName,
        id: element.id || null,
        classes: []
    };
    
    // 获取类名
    if (element.className && typeof element.className === 'string') {
        info.classes = element.className.split(' ').filter(c => c.trim()).slice(0, 5);
    }
    
    // 获取关键属性
    const keyAttrs = ['placeholder', 'aria-label', 'role', 'type', 'name'];
    const attrs = {};
    keyAttrs.forEach(attr => {
        if (element.hasAttribute && element.hasAttribute(attr)) {
            attrs[attr] = element.getAttribute(attr);
        }
    });
    if (Object.keys(attrs).length > 0) {
        info.attributes = attrs;
    }
    
    // 递归子元素（限制数量）
    if (element.children && depth < maxDepth) {
        const childCount = Math.min(element.children.length, 20);
        if (childCount > 0) {
            info.children = [];
            for (let i = 0; i < childCount; i++) {
                const child = getElementStructure(element.children[i], depth + 1, maxDepth);
                if (child) {
                    info.children.push(child);
                }
            }
            if (element.children.length > childCount) {
                info.childrenNote = `还有 ${element.children.length - childCount} 个子元素未显示`;
            }
        }
    }
    
    return info;
}

// 获取关键元素信息
function findKeyElements() {
    const result = {
        textareas: [],
        inputs: [],
        buttons: [],
        aiRelated: [],
        editorElements: []
    };
    
    // 查找所有 textarea
    console.log('📝 查找 textareas...');
    const textareas = document.querySelectorAll('textarea');
    textareas.forEach((ta, i) => {
        if (i < 20) {
            const rect = ta.getBoundingClientRect();
            result.textareas.push({
                index: i,
                id: ta.id || null,
                placeholder: ta.placeholder || '',
                value: ta.value ? `${ta.value.substring(0, 50)}...` : '',
                visible: ta.offsetParent !== null,
                focused: document.activeElement === ta,
                classes: ta.className,
                position: {
                    top: Math.round(rect.top),
                    left: Math.round(rect.left),
                    width: Math.round(rect.width),
                    height: Math.round(rect.height)
                }
            });
        }
    });
    console.log(`   找到 ${textareas.length} 个 textareas`);
    
    // 查找所有 input
    console.log('📝 查找 inputs...');
    const inputs = document.querySelectorAll('input');
    inputs.forEach((inp, i) => {
        if (i < 20) {
            result.inputs.push({
                index: i,
                id: inp.id || null,
                type: inp.type,
                placeholder: inp.placeholder || '',
                value: inp.value ? `${inp.value.substring(0, 50)}...` : '',
                visible: inp.offsetParent !== null,
                classes: inp.className
            });
        }
    });
    console.log(`   找到 ${inputs.length} 个 inputs`);
    
    // 查找按钮
    console.log('📝 查找 buttons...');
    const buttons = document.querySelectorAll('button');
    buttons.forEach((btn, i) => {
        if (i < 30) {
            const text = btn.textContent ? btn.textContent.trim() : '';
            const ariaLabel = btn.getAttribute('aria-label');
            if (text || ariaLabel) {
                result.buttons.push({
                    index: i,
                    text: text.substring(0, 50),
                    ariaLabel: ariaLabel,
                    visible: btn.offsetParent !== null,
                    classes: btn.className.split(' ').slice(0, 5)
                });
            }
        }
    });
    console.log(`   找到 ${buttons.length} 个 buttons`);
    
    // 查找 AI 相关元素
    console.log('📝 查找 AI 相关元素...');
    const aiSelectors = [
        '[class*="ai"]',
        '[class*="chat"]',
        '[class*="assistant"]',
        '[class*="copilot"]',
        '[aria-label*="AI"]',
        '[aria-label*="Chat"]',
        '[data-testid*="ai"]',
        '[data-testid*="chat"]'
    ];
    
    aiSelectors.forEach(selector => {
        try {
            const elements = document.querySelectorAll(selector);
            if (elements.length > 0) {
                elements.forEach((elem, i) => {
                    if (i < 5 && result.aiRelated.length < 30) {
                        result.aiRelated.push({
                            selector: selector,
                            tag: elem.tagName.toLowerCase(),
                            id: elem.id || null,
                            classes: elem.className ? elem.className.split(' ').slice(0, 5) : [],
                            text: elem.textContent ? elem.textContent.trim().substring(0, 100) : '',
                            visible: elem.offsetParent !== null
                        });
                    }
                });
            }
        } catch (e) {
            // 忽略无效选择器
        }
    });
    console.log(`   找到 ${result.aiRelated.length} 个 AI 相关元素`);
    
    // 查找编辑器相关元素
    console.log('📝 查找编辑器元素...');
    const editorSelectors = [
        '.monaco-editor',
        '[class*="editor"]',
        '[class*="monaco"]'
    ];
    
    editorSelectors.forEach(selector => {
        try {
            const elements = document.querySelectorAll(selector);
            if (elements.length > 0 && result.editorElements.length < 10) {
                elements.forEach((elem, i) => {
                    if (i < 3) {
                        result.editorElements.push({
                            selector: selector,
                            classes: elem.className ? elem.className.split(' ').slice(0, 10) : [],
                            visible: elem.offsetParent !== null
                        });
                    }
                });
            }
        } catch (e) {}
    });
    console.log(`   找到 ${result.editorElements.length} 个编辑器元素`);
    
    return result;
}

// 获取 Monaco Editor 信息
function getMonacoInfo() {
    console.log('📝 检查 Monaco Editor...');
    
    if (!window.monaco || !window.monaco.editor) {
        console.log('   ⚠️  Monaco Editor API 不可用');
        return null;
    }
    
    const editors = window.monaco.editor.getEditors();
    console.log(`   找到 ${editors.length} 个编辑器实例`);
    
    if (editors.length === 0) {
        return { count: 0 };
    }
    
    const editor = editors[0];
    const model = editor.getModel();
    
    return {
        count: editors.length,
        currentEditor: {
            language: model.getLanguageId(),
            lineCount: model.getLineCount(),
            valueLength: model.getValue().length,
            firstLine: model.getLineContent(1).substring(0, 100),
            uri: model.uri.toString()
        }
    };
}

// 主函数
function analyzeCursorDOM() {
    const result = {
        timestamp: new Date().toISOString(),
        pageInfo: {
            title: document.title,
            url: window.location.href,
            userAgent: navigator.userAgent
        },
        summary: {
            totalElements: document.querySelectorAll('*').length,
            divs: document.querySelectorAll('div').length,
            textareas: document.querySelectorAll('textarea').length,
            inputs: document.querySelectorAll('input').length,
            buttons: document.querySelectorAll('button').length,
            imgs: document.querySelectorAll('img').length
        },
        keyElements: null,
        monacoEditor: null,
        bodyStructure: null
    };
    
    console.log('');
    console.log('=' .repeat(80));
    console.log('  📊 Cursor DOM 分析');
    console.log('=' .repeat(80));
    console.log('');
    
    console.log('📄 页面信息:');
    console.log('   标题:', result.pageInfo.title);
    console.log('   URL:', result.pageInfo.url);
    console.log('');
    
    console.log('📈 元素统计:');
    console.log('   总元素数:', result.summary.totalElements);
    console.log('   DIV:', result.summary.divs);
    console.log('   TEXTAREA:', result.summary.textareas);
    console.log('   INPUT:', result.summary.inputs);
    console.log('   BUTTON:', result.summary.buttons);
    console.log('');
    
    // 获取关键元素
    result.keyElements = findKeyElements();
    console.log('');
    
    // 获取 Monaco 信息
    result.monacoEditor = getMonacoInfo();
    console.log('');
    
    // 获取 body 结构
    console.log('📝 获取 body 结构（深度3）...');
    result.bodyStructure = getElementStructure(document.body, 0, 3);
    console.log('   ✅ 完成');
    console.log('');
    
    console.log('=' .repeat(80));
    console.log('  ✅ 分析完成！');
    console.log('=' .repeat(80));
    console.log('');
    console.log('📝 结果已保存到变量 cursorDomData');
    console.log('📝 你可以:');
    console.log('   1. 在 Console 中输入 cursorDomData 查看完整数据');
    console.log('   2. 右键点击结果 → Copy object');
    console.log('   3. 或者运行: copy(cursorDomData) 复制到剪贴板');
    console.log('   4. 或者运行: JSON.stringify(cursorDomData, null, 2) 查看格式化的 JSON');
    console.log('');
    
    return result;
}

// 运行分析
const cursorDomData = analyzeCursorDOM();

// 打印关键发现
console.log('🔍 关键发现:');
console.log('');

if (cursorDomData.keyElements.textareas.length > 0) {
    console.log(`✅ 找到 ${cursorDomData.keyElements.textareas.length} 个 textareas:`);
    cursorDomData.keyElements.textareas.forEach(ta => {
        const visible = ta.visible ? '✅' : '❌';
        console.log(`   ${visible} [${ta.index}] "${ta.placeholder.substring(0, 60)}"`);
    });
    console.log('');
}

if (cursorDomData.monacoEditor && cursorDomData.monacoEditor.count > 0) {
    console.log('✅ Monaco Editor:');
    const monaco = cursorDomData.monacoEditor.currentEditor;
    console.log('   语言:', monaco.language);
    console.log('   行数:', monaco.lineCount);
    console.log('   字符数:', monaco.valueLength);
    console.log('');
}

if (cursorDomData.keyElements.aiRelated.length > 0) {
    console.log(`✅ 找到 ${cursorDomData.keyElements.aiRelated.length} 个 AI 相关元素`);
    console.log('');
}

console.log('💡 要复制完整数据到剪贴板，运行:');
console.log('   copy(cursorDomData)');
console.log('');

