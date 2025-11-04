/**
 * Cursor DOM 操作封装
 * 
 * 这个模块封装了所有与 Cursor UI 交互的 DOM 操作。
 * 当 Cursor 版本更新导致 UI 变化时，只需修改这个文件。
 * 
 * @version 1.0
 * @date 2025-11-03
 */

/**
 * 操作结果统一格式
 * @typedef {Object} OperationResult
 * @property {boolean} success - 操作是否成功
 * @property {*} [data] - 成功时返回的数据
 * @property {string} [error] - 失败时的错误信息
 * @property {string} [message] - 附加信息
 */

/**
 * Composer 操作类
 * 封装所有与 AI Composer 相关的 DOM 操作
 */
class ComposerOperations {
    /**
     * 构造函数
     */
    constructor() {
        // Composer 相关的选择器（Cursor 版本更新时可能需要修改）
        this.selectors = {
            input: '.aislash-editor-input',           // 输入框
            submitButton: 'button[type="submit"]',     // 提交按钮
            composer: '.composer',                     // Composer 容器
            statusIndicator: '.composer-status',       // 状态指示器（如果有）
            thinkingIndicator: '.thinking-indicator',  // 思考中指示器
        };
    }

    /**
     * 查找输入框元素
     * @returns {OperationResult}
     */
    findInputElement() {
        try {
            const input = document.querySelector(this.selectors.input);
            
            if (!input) {
                return {
                    success: false,
                    error: '输入框未找到',
                    message: `选择器 "${this.selectors.input}" 未匹配到元素`
                };
            }
            
            return {
                success: true,
                data: input
            };
        } catch (error) {
            return {
                success: false,
                error: error.message
            };
        }
    }

    /**
     * 清空输入框内容
     * @returns {OperationResult}
     */
    clearInput() {
        try {
            const inputResult = this.findInputElement();
            if (!inputResult.success) {
                return inputResult;
            }
            
            const input = inputResult.data;
            
            // 聚焦
            input.focus();
            
            // 选中所有内容
            const sel = window.getSelection();
            const range = document.createRange();
            range.selectNodeContents(input);
            sel.removeAllRanges();
            sel.addRange(range);
            
            // 删除
            document.execCommand('delete', false, null);
            
            return {
                success: true,
                message: '输入框已清空'
            };
        } catch (error) {
            return {
                success: false,
                error: error.message
            };
        }
    }

    /**
     * 输入文本到 Composer
     * @param {string} text - 要输入的文本
     * @param {boolean} clearFirst - 是否先清空（默认 true）
     * @returns {OperationResult}
     */
    inputText(text, clearFirst = true) {
        try {
            const inputResult = this.findInputElement();
            if (!inputResult.success) {
                return inputResult;
            }
            
            const input = inputResult.data;
            
            // 聚焦
            input.focus();
            
            // 如果需要先清空
            if (clearFirst) {
                const clearResult = this.clearInput();
                if (!clearResult.success) {
                    return clearResult;
                }
            }
            
            // 插入文字（使用 execCommand 支持 Lexical 编辑器）
            const success = document.execCommand('insertText', false, text);
            
            if (!success) {
                return {
                    success: false,
                    error: 'execCommand 执行失败',
                    message: '可能是浏览器不支持或编辑器状态异常'
                };
            }
            
            // 触发 input 事件（让 Lexical 编辑器知道内容变化）
            input.dispatchEvent(new InputEvent('input', { 
                bubbles: true, 
                cancelable: true 
            }));
            
            return {
                success: true,
                message: `成功输入 ${text.length} 个字符`,
                data: {
                    length: text.length,
                    text: text.substring(0, 50) + (text.length > 50 ? '...' : '')
                }
            };
        } catch (error) {
            return {
                success: false,
                error: error.message
            };
        }
    }

    /**
     * 追加文本（不清空现有内容）
     * @param {string} text - 要追加的文本
     * @returns {OperationResult}
     */
    appendText(text) {
        return this.inputText(text, false);
    }

    /**
     * 获取输入框当前内容
     * @returns {OperationResult}
     */
    getInputContent() {
        try {
            const inputResult = this.findInputElement();
            if (!inputResult.success) {
                return inputResult;
            }
            
            const input = inputResult.data;
            const innerText = input.innerText || '';
            const textContent = input.textContent || '';
            
            return {
                success: true,
                data: {
                    innerText: innerText,
                    textContent: textContent,
                    length: innerText.length,
                    isEmpty: innerText.trim().length === 0
                }
            };
        } catch (error) {
            return {
                success: false,
                error: error.message
            };
        }
    }

    /**
     * 检测 Composer 状态
     * @returns {OperationResult}
     */
    detectStatus() {
        try {
            // 尝试检测各种状态指示器
            const hasThinkingIndicator = document.querySelector(this.selectors.thinkingIndicator) !== null;
            const hasComposer = document.querySelector(this.selectors.composer) !== null;
            
            // TODO: 需要分析实际的 Cursor UI 来完善这个检测
            // 目前返回基本状态
            let status = 'unknown';
            
            if (hasThinkingIndicator) {
                status = 'thinking';
            } else if (hasComposer) {
                status = 'idle';
            }
            
            return {
                success: true,
                data: {
                    status: status,
                    hasThinkingIndicator: hasThinkingIndicator,
                    hasComposer: hasComposer
                }
            };
        } catch (error) {
            return {
                success: false,
                error: error.message
            };
        }
    }

    /**
     * 模拟点击提交按钮
     * @returns {OperationResult}
     */
    clickSubmit() {
        try {
            const button = document.querySelector(this.selectors.submitButton);
            
            if (!button) {
                return {
                    success: false,
                    error: '提交按钮未找到',
                    message: `选择器 "${this.selectors.submitButton}" 未匹配到元素`
                };
            }
            
            // 检查按钮是否可点击
            if (button.disabled) {
                return {
                    success: false,
                    error: '提交按钮被禁用',
                    message: '可能输入框为空或 AI 正在处理'
                };
            }
            
            // 点击按钮
            button.click();
            
            return {
                success: true,
                message: '提交按钮已点击'
            };
        } catch (error) {
            return {
                success: false,
                error: error.message
            };
        }
    }

    /**
     * 等待输入框可用
     * @param {number} timeout - 超时时间（毫秒）
     * @returns {Promise<OperationResult>}
     */
    async waitForInput(timeout = 5000) {
        const startTime = Date.now();
        
        while (Date.now() - startTime < timeout) {
            const result = this.findInputElement();
            if (result.success) {
                return result;
            }
            
            // 等待 100ms 后重试
            await new Promise(resolve => setTimeout(resolve, 100));
        }
        
        return {
            success: false,
            error: '等待输入框超时',
            message: `在 ${timeout}ms 内未找到输入框`
        };
    }
}


/**
 * Editor 操作类（预留）
 * 封装所有与代码编辑器相关的 DOM 操作
 */
class EditorOperations {
    constructor() {
        this.selectors = {
            editor: '.monaco-editor',
            activeEditor: '.editor.active',
            lineNumber: '.line-numbers',
        };
    }

    /**
     * 获取当前文件内容
     * @returns {OperationResult}
     */
    getCurrentFileContent() {
        // TODO: 实现获取编辑器内容
        return {
            success: false,
            error: '尚未实现',
            message: '需要使用 VSCode API 获取编辑器内容'
        };
    }

    /**
     * 在指定位置插入文本
     * @param {number} line - 行号
     * @param {number} column - 列号
     * @param {string} text - 要插入的文本
     * @returns {OperationResult}
     */
    insertTextAt(line, column, text) {
        // TODO: 实现
        return {
            success: false,
            error: '尚未实现'
        };
    }
}


/**
 * Terminal 操作类（预留）
 * 封装所有与终端相关的 DOM 操作
 */
class TerminalOperations {
    constructor() {
        this.selectors = {
            terminal: '.terminal',
            terminalInput: '.terminal-input',
        };
    }

    /**
     * 在终端执行命令
     * @param {string} command - 要执行的命令
     * @returns {OperationResult}
     */
    executeCommand(command) {
        // TODO: 实现
        return {
            success: false,
            error: '尚未实现'
        };
    }

    /**
     * 获取终端输出
     * @returns {OperationResult}
     */
    getOutput() {
        // TODO: 实现
        return {
            success: false,
            error: '尚未实现'
        };
    }
}


/**
 * Cursor DOM 操作管理器
 * 统一管理所有操作类
 */
class CursorDOMManager {
    constructor() {
        this.composer = new ComposerOperations();
        this.editor = new EditorOperations();
        this.terminal = new TerminalOperations();
    }

    /**
     * 获取管理器版本信息
     * @returns {Object}
     */
    getVersion() {
        return {
            version: '1.0',
            date: '2025-11-03',
            operations: {
                composer: 'implemented',
                editor: 'planned',
                terminal: 'planned'
            }
        };
    }

    /**
     * 测试所有选择器是否有效
     * @returns {Object}
     */
    testSelectors() {
        const results = {
            composer: {},
            editor: {},
            terminal: {}
        };

        // 测试 Composer 选择器
        for (const [key, selector] of Object.entries(this.composer.selectors)) {
            const element = document.querySelector(selector);
            results.composer[key] = {
                selector: selector,
                found: element !== null,
                element: element
            };
        }

        // 测试 Editor 选择器
        for (const [key, selector] of Object.entries(this.editor.selectors)) {
            const element = document.querySelector(selector);
            results.editor[key] = {
                selector: selector,
                found: element !== null,
                element: element
            };
        }

        // 测试 Terminal 选择器
        for (const [key, selector] of Object.entries(this.terminal.selectors)) {
            const element = document.querySelector(selector);
            results.terminal[key] = {
                selector: selector,
                found: element !== null,
                element: element
            };
        }

        return results;
    }
}


// 导出（如果在 Node.js 环境）
if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        CursorDOMManager,
        ComposerOperations,
        EditorOperations,
        TerminalOperations
    };
}

// 在浏览器环境中创建全局实例
if (typeof window !== 'undefined') {
    window.CursorDOM = new CursorDOMManager();
}

