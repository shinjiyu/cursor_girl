/**
 * Cursor 语义操作封装
 * 
 * 提供高层次的语义接口，封装完整的业务操作流程。
 * 例如："给 Agent 输入指令并执行" 这样的完整操作。
 * 
 * @version 1.0
 * @date 2025-11-03
 */

/**
 * Composer Agent 语义操作类
 * 提供与 Cursor AI Agent 交互的高层次接口
 */
class ComposerAgentOperations {
    constructor() {
        // 配置参数
        this.config = {
            submitDelay: 500,           // 输入后等待多久再提交（ms）
            pollInterval: 1000,         // 状态轮询间隔（ms）
            maxWaitTime: 300000,        // 最大等待时间（5分钟）
            submitMethod: 'enter'       // 提交方式: 'enter' 或 'button'
        };
        
        // 选择器
        this.selectors = {
            input: '.aislash-editor-input',
            submitButton: 'button[type="submit"]',
            thinkingIndicator: '.cursor-thinking, .agent-working, [data-status="thinking"]',
            completedIndicator: '.agent-completed, [data-status="completed"]',
            errorIndicator: '.agent-error, [data-status="error"]',
            stopButton: '.stop-generation-button, [aria-label="Stop generating"]'
        };
    }

    /**
     * 核心语义操作：输入指令并执行
     * 
     * 这是最重要的高层次接口，封装了完整的交互流程：
     * 1. 输入提示词
     * 2. 提交执行
     * 3. 等待完成
     * 4. 返回结果
     * 
     * @param {string} prompt - 提示词
     * @param {Object} options - 选项
     * @param {boolean} options.waitForCompletion - 是否等待执行完成（默认 false）
     * @param {number} options.timeout - 超时时间（ms，默认 300000）
     * @param {boolean} options.clearFirst - 是否先清空输入框（默认 true）
     * @returns {Promise<Object>} 执行结果
     */
    async executePrompt(prompt, options = {}) {
        const {
            waitForCompletion = false,
            timeout = this.config.maxWaitTime,
            clearFirst = true
        } = options;

        const result = {
            success: false,
            phase: 'init',
            prompt: prompt,
            timestamp: Date.now()
        };

        try {
            // 阶段 1: 输入提示词
            result.phase = 'input';
            const inputResult = await this._inputPrompt(prompt, clearFirst);
            
            if (!inputResult.success) {
                result.error = `输入失败: ${inputResult.error}`;
                return result;
            }

            result.inputCompleted = true;

            // 阶段 2: 提交执行
            result.phase = 'submit';
            const submitResult = await this._submitPrompt();
            
            if (!submitResult.success) {
                result.error = `提交失败: ${submitResult.error}`;
                return result;
            }

            result.submitCompleted = true;
            result.submitTime = Date.now();

            // 如果不需要等待完成，立即返回成功
            if (!waitForCompletion) {
                result.success = true;
                result.phase = 'submitted';
                result.message = '提示词已提交，未等待完成';
                return result;
            }

            // 阶段 3: 等待执行完成
            result.phase = 'executing';
            const executionResult = await this._waitForCompletion(timeout);
            
            if (!executionResult.success) {
                result.error = `执行超时或失败: ${executionResult.error}`;
                result.executionTime = Date.now() - result.submitTime;
                return result;
            }

            // 执行完成
            result.success = true;
            result.phase = 'completed';
            result.executionTime = Date.now() - result.submitTime;
            result.status = executionResult.status;
            result.message = '提示词执行完成';

            return result;

        } catch (error) {
            result.error = `异常: ${error.message}`;
            result.exception = error.toString();
            return result;
        }
    }

    /**
     * 语义操作：检查 Agent 是否正在工作
     * @returns {Object}
     */
    isAgentWorking() {
        try {
            const thinkingEl = document.querySelector(this.selectors.thinkingIndicator);
            const stopButton = document.querySelector(this.selectors.stopButton);
            
            const isWorking = (thinkingEl !== null) || (stopButton !== null && !stopButton.disabled);
            
            return {
                success: true,
                isWorking: isWorking,
                indicators: {
                    thinkingIndicator: thinkingEl !== null,
                    stopButton: stopButton !== null
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
     * 语义操作：停止 Agent 执行
     * @returns {Object}
     */
    stopExecution() {
        try {
            const stopButton = document.querySelector(this.selectors.stopButton);
            
            if (!stopButton) {
                return {
                    success: false,
                    error: '未找到停止按钮',
                    message: 'Agent 可能未在执行'
                };
            }

            if (stopButton.disabled) {
                return {
                    success: false,
                    error: '停止按钮被禁用',
                    message: 'Agent 可能已经停止'
                };
            }

            stopButton.click();

            return {
                success: true,
                message: '已发送停止指令'
            };
        } catch (error) {
            return {
                success: false,
                error: error.message
            };
        }
    }

    /**
     * 语义操作：清空输入并准备新的指令
     * @returns {Object}
     */
    prepareForNewPrompt() {
        try {
            const input = document.querySelector(this.selectors.input);
            
            if (!input) {
                return {
                    success: false,
                    error: '输入框未找到'
                };
            }

            // 聚焦
            input.focus();

            // 清空内容
            const sel = window.getSelection();
            const range = document.createRange();
            range.selectNodeContents(input);
            sel.removeAllRanges();
            sel.addRange(range);
            document.execCommand('delete', false, null);

            return {
                success: true,
                message: '输入框已清空并聚焦'
            };
        } catch (error) {
            return {
                success: false,
                error: error.message
            };
        }
    }

    // ========== 私有辅助方法 ==========

    /**
     * 输入提示词（内部方法）
     * @private
     */
    async _inputPrompt(prompt, clearFirst) {
        try {
            const input = document.querySelector(this.selectors.input);
            
            if (!input) {
                return {
                    success: false,
                    error: '输入框未找到'
                };
            }

            input.focus();

            // 清空
            if (clearFirst) {
                const sel = window.getSelection();
                const range = document.createRange();
                range.selectNodeContents(input);
                sel.removeAllRanges();
                sel.addRange(range);
                document.execCommand('delete', false, null);
            }

            // 输入
            const success = document.execCommand('insertText', false, prompt);
            
            if (!success) {
                return {
                    success: false,
                    error: 'execCommand 执行失败'
                };
            }

            // 触发事件
            input.dispatchEvent(new InputEvent('input', { 
                bubbles: true, 
                cancelable: true 
            }));

            return {
                success: true,
                message: `已输入 ${prompt.length} 个字符`
            };
        } catch (error) {
            return {
                success: false,
                error: error.message
            };
        }
    }

    /**
     * 提交提示词（内部方法）
     * @private
     */
    async _submitPrompt() {
        try {
            // 等待一小段时间，确保 UI 更新
            await this._sleep(this.config.submitDelay);

            const input = document.querySelector(this.selectors.input);
            
            if (!input) {
                return {
                    success: false,
                    error: '输入框未找到'
                };
            }

            if (this.config.submitMethod === 'enter') {
                // 方法 1: 模拟按下 Enter 键
                input.focus();
                
                const enterEvent = new KeyboardEvent('keydown', {
                    key: 'Enter',
                    code: 'Enter',
                    keyCode: 13,
                    which: 13,
                    bubbles: true,
                    cancelable: true
                });
                
                input.dispatchEvent(enterEvent);
                
                return {
                    success: true,
                    message: '已发送 Enter 键'
                };
            } else {
                // 方法 2: 点击提交按钮
                const button = document.querySelector(this.selectors.submitButton);
                
                if (!button) {
                    return {
                        success: false,
                        error: '提交按钮未找到'
                    };
                }

                if (button.disabled) {
                    return {
                        success: false,
                        error: '提交按钮被禁用'
                    };
                }

                button.click();

                return {
                    success: true,
                    message: '已点击提交按钮'
                };
            }
        } catch (error) {
            return {
                success: false,
                error: error.message
            };
        }
    }

    /**
     * 等待执行完成（内部方法）
     * @private
     */
    async _waitForCompletion(timeout) {
        const startTime = Date.now();
        let lastStatus = 'unknown';

        while (Date.now() - startTime < timeout) {
            // 检查是否正在工作
            const workingResult = this.isAgentWorking();
            
            if (workingResult.success) {
                if (workingResult.isWorking) {
                    lastStatus = 'working';
                } else {
                    // 不在工作了，可能已完成
                    // 再等待一小段时间确认
                    await this._sleep(1000);
                    
                    const confirmResult = this.isAgentWorking();
                    if (confirmResult.success && !confirmResult.isWorking) {
                        // 确认完成
                        return {
                            success: true,
                            status: 'completed',
                            duration: Date.now() - startTime
                        };
                    }
                }
            }

            // 检查是否有错误指示器
            const errorEl = document.querySelector(this.selectors.errorIndicator);
            if (errorEl) {
                return {
                    success: false,
                    error: 'Agent 执行出错',
                    status: 'error'
                };
            }

            // 等待后重试
            await this._sleep(this.config.pollInterval);
        }

        // 超时
        return {
            success: false,
            error: `等待超时 (${timeout}ms)`,
            lastStatus: lastStatus
        };
    }

    /**
     * 睡眠（内部方法）
     * @private
     */
    _sleep(ms) {
        return new Promise(resolve => setTimeout(resolve, ms));
    }
}


/**
 * Cursor 语义操作管理器
 */
class CursorSemanticManager {
    constructor() {
        this.agent = new ComposerAgentOperations();
    }

    /**
     * 获取版本信息
     */
    getVersion() {
        return {
            version: '1.0',
            date: '2025-11-03',
            operations: {
                agent: 'implemented'
            }
        };
    }
}


// 导出
if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        CursorSemanticManager,
        ComposerAgentOperations
    };
}

// 在浏览器环境中创建全局实例
if (typeof window !== 'undefined') {
    window.CursorSemantic = new CursorSemanticManager();
}

