/**
 * オルテンシア（Ortensia）主题配置
 * 紫色阿贾西亚主题 - 为编程助手定制
 */

export const OrtensiaTheme = {
  // 颜色配置
  colors: {
    // 主色调（紫色）
    primary: '#9D4EDD',
    primaryHover: '#B56AE8',
    primaryPress: '#7B2CBF',
    
    // 辅助色（深紫）
    secondary: '#7B2CBF',
    secondaryHover: '#9D4EDD',
    
    // 强调色（浅紫）
    accent: '#C77DFF',
    accentLight: '#E0AAFF',
    
    // 背景色
    background: {
      main: '#240046',
      dark: '#10002B',
      light: '#3C096C',
      overlay: 'rgba(36, 0, 70, 0.95)',
    },
    
    // 文字色
    text: {
      primary: '#E0AAFF',
      secondary: '#C77DFF',
      muted: '#9D4EDD',
      white: '#FFFFFF',
    },
    
    // 状态色
    status: {
      success: '#10B981',  // 绿色 - 成功
      error: '#EF4444',    // 红色 - 错误
      warning: '#F59E0B',  // 橙色 - 警告
      info: '#3B82F6',     // 蓝色 - 信息
    },
  },
  
  // 渐变背景
  gradients: {
    background: 'linear-gradient(135deg, #240046 0%, #10002B 50%, #3C096C 100%)',
    card: 'linear-gradient(135deg, rgba(157, 78, 221, 0.1) 0%, rgba(123, 44, 191, 0.1) 100%)',
    button: 'linear-gradient(135deg, #9D4EDD 0%, #7B2CBF 100%)',
  },
  
  // 阴影
  shadows: {
    small: '0 2px 8px rgba(157, 78, 221, 0.2)',
    medium: '0 4px 16px rgba(157, 78, 221, 0.3)',
    large: '0 8px 32px rgba(157, 78, 221, 0.4)',
    glow: '0 0 20px rgba(157, 78, 221, 0.6)',
  },
  
  // 配置
  config: {
    // 默认模型
    defaultVrmModel: 'ortensia.vrm',
    
    // 角色初始设置
    character: {
      initialEmotion: 'happy',
      scale: 1.0,
      position: { x: 0, y: 0, z: 0 },
    },
    
    // UI 设置
    ui: {
      borderRadius: '16px',
      showYoutubeMode: false,
      showSlideMode: false,
      showRealtimeMode: false,
      compactMode: false,
    },
    
    // 消息设置
    messages: {
      welcomeMessage: '你好！我是オルテンシア，你的编程伴侣 ✨',
      placeholder: '有什么想问的吗？',
    },
  },
}

// 导出 CSS 变量
export const OrtensiaThemeCSS = `
:root {
  /* 主色调 */
  --ortensia-primary: ${OrtensiaTheme.colors.primary};
  --ortensia-primary-hover: ${OrtensiaTheme.colors.primaryHover};
  --ortensia-primary-press: ${OrtensiaTheme.colors.primaryPress};
  
  /* 辅助色 */
  --ortensia-secondary: ${OrtensiaTheme.colors.secondary};
  --ortensia-secondary-hover: ${OrtensiaTheme.colors.secondaryHover};
  
  /* 强调色 */
  --ortensia-accent: ${OrtensiaTheme.colors.accent};
  --ortensia-accent-light: ${OrtensiaTheme.colors.accentLight};
  
  /* 背景色 */
  --ortensia-bg-main: ${OrtensiaTheme.colors.background.main};
  --ortensia-bg-dark: ${OrtensiaTheme.colors.background.dark};
  --ortensia-bg-light: ${OrtensiaTheme.colors.background.light};
  
  /* 文字色 */
  --ortensia-text-primary: ${OrtensiaTheme.colors.text.primary};
  --ortensia-text-secondary: ${OrtensiaTheme.colors.text.secondary};
  
  /* 渐变 */
  --ortensia-gradient-bg: ${OrtensiaTheme.gradients.background};
  --ortensia-gradient-card: ${OrtensiaTheme.gradients.card};
  --ortensia-gradient-button: ${OrtensiaTheme.gradients.button};
}
`

