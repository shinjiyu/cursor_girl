#!/bin/bash
# VRM 动画下载助手脚本
# 用途：帮助用户从 Mixamo 下载并转换动画文件

set -e

BLUE='\033[0;34m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

PROJECT_ROOT="/Users/user/Documents/ cursorgirl"
ANIMATIONS_DIR="$PROJECT_ROOT/aituber-kit/public/animations"
DOWNLOADS_DIR="$HOME/Downloads"

echo -e "${BLUE}╔════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║   VRM 动画下载助手 v1.0               ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════╝${NC}"
echo ""

# 检查目录
if [ ! -d "$ANIMATIONS_DIR" ]; then
    echo -e "${YELLOW}📁 创建动画目录...${NC}"
    mkdir -p "$ANIMATIONS_DIR"
fi

echo -e "${GREEN}✅ 动画目录：${NC}$ANIMATIONS_DIR"
echo ""

# 显示推荐下载列表
echo -e "${BLUE}📋 推荐下载的 Mixamo 动画：${NC}"
echo ""
echo "┌────┬─────────────────┬──────────────────┬──────────┐"
echo "│ No │ 动画名称        │ Mixamo 搜索      │ 优先级   │"
echo "├────┼─────────────────┼──────────────────┼──────────┤"
echo "│ 1  │ 挥手打招呼      │ Waving           │ ⭐⭐⭐⭐⭐ │"
echo "│ 2  │ 鞠躬            │ Bowing           │ ⭐⭐⭐⭐⭐ │"
echo "│ 3  │ 点头同意        │ Yes              │ ⭐⭐⭐⭐⭐ │"
echo "│ 4  │ 摇头否定        │ No               │ ⭐⭐⭐⭐   │"
echo "│ 5  │ 思考动作        │ Thinking         │ ⭐⭐⭐⭐⭐ │"
echo "│ 6  │ 庆祝胜利        │ Victory          │ ⭐⭐⭐⭐   │"
echo "│ 7  │ 鼓掌            │ Clapping         │ ⭐⭐⭐⭐   │"
echo "│ 8  │ 指向前方        │ Pointing         │ ⭐⭐⭐     │"
echo "│ 9  │ 交叉双臂        │ Arms Crossed     │ ⭐⭐⭐     │"
echo "│ 10 │ 讲话手势        │ Talking          │ ⭐⭐⭐⭐   │"
echo "└────┴─────────────────┴──────────────────┴──────────┘"
echo ""

# 显示操作步骤
echo -e "${YELLOW}🔧 操作步骤：${NC}"
echo ""
echo "步骤 1️⃣  - 访问 Mixamo 网站"
echo "        打开: https://www.mixamo.com/"
echo "        (可能需要 Adobe 账号登录，免费注册)"
echo ""
echo "步骤 2️⃣  - 搜索并预览动画"
echo "        在搜索框输入上表中的关键词"
echo "        点击动画预览效果"
echo "        选择满意的动画"
echo ""
echo "步骤 3️⃣  - 下载设置"
echo "        点击 'Download' 按钮"
echo "        Format: FBX for Unity (.fbx)"
echo "        Skin: Without Skin"
echo "        Frames per second: 30"
echo "        点击 'Download'"
echo ""
echo "步骤 4️⃣  - 转换为 VRMA 格式"
echo "        打开: https://3dretarget.com/zh"
echo "        选择 'Mixamo FBX 转 VRMA'"
echo "        上传刚下载的 FBX 文件"
echo "        下载生成的 .vrma 文件"
echo ""
echo "步骤 5️⃣  - 移动文件到项目"
echo "        将 .vrma 文件重命名（如 wave.vrma）"
echo "        移动到: $ANIMATIONS_DIR"
echo ""

# 检查下载目录中的 FBX 文件
echo -e "${BLUE}📥 检查 Downloads 目录中的 FBX 文件...${NC}"
if ls "$DOWNLOADS_DIR"/*.fbx 1> /dev/null 2>&1; then
    echo -e "${GREEN}找到以下 FBX 文件：${NC}"
    ls -lh "$DOWNLOADS_DIR"/*.fbx | awk '{print "  - " $9 " (" $5 ")"}'
    echo ""
    read -p "是否要将这些文件移动到临时目录？(y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        mkdir -p "$PROJECT_ROOT/temp_fbx_animations"
        mv "$DOWNLOADS_DIR"/*.fbx "$PROJECT_ROOT/temp_fbx_animations/"
        echo -e "${GREEN}✅ 已移动到：${NC}$PROJECT_ROOT/temp_fbx_animations/"
        echo -e "${YELLOW}请使用 3dRetarget 转换这些文件${NC}"
    fi
else
    echo -e "${YELLOW}未找到 FBX 文件${NC}"
fi
echo ""

# 列出当前已有的动画
echo -e "${BLUE}📂 当前已有的动画文件：${NC}"
if ls "$ANIMATIONS_DIR"/*.vrma 1> /dev/null 2>&1; then
    ls -lh "$ANIMATIONS_DIR"/*.vrma | awk '{print "  ✅ " $9 " (" $5 ")"}'
else
    echo -e "${YELLOW}  暂无动画文件${NC}"
fi
echo ""

# 显示配置示例
echo -e "${BLUE}🔧 配置代码示例：${NC}"
echo ""
echo "将以下代码添加到 animationController.ts 的 preloadAnimations() 方法中："
echo ""
echo -e "${GREEN}async preloadAnimations() {${NC}"
echo -e "${GREEN}  const animations = [${NC}"
echo -e "${GREEN}    { name: 'idle', url: '/animations/idle_loop.vrma' },${NC}"
echo -e "${GREEN}    { name: 'wave', url: '/animations/wave.vrma' },${NC}"
echo -e "${GREEN}    { name: 'bow', url: '/animations/bow.vrma' },${NC}"
echo -e "${GREEN}    { name: 'nod', url: '/animations/nod.vrma' },${NC}"
echo -e "${GREEN}    { name: 'think', url: '/animations/think.vrma' },${NC}"
echo -e "${GREEN}    { name: 'celebrate', url: '/animations/celebrate.vrma' },${NC}"
echo -e "${GREEN}  ]${NC}"
echo -e "${GREEN}  // ... 其余代码${NC}"
echo -e "${GREEN}}${NC}"
echo ""

# 显示使用示例
echo -e "${BLUE}💡 使用示例（在 Python 中）：${NC}"
echo ""
echo -e "${GREEN}# 从 Cursor Hook 触发动画${NC}"
echo -e "${GREEN}client.send_aituber_text(${NC}"
echo -e "${GREEN}    text=\"收到！马上处理\",${NC}"
echo -e "${GREEN}    emotion=\"wave\",  # 触发挥手动画${NC}"
echo -e "${GREEN}    conversation_id=conv_id${NC}"
echo -e "${GREEN})${NC}"
echo ""

# 快捷链接
echo -e "${BLUE}🔗 快捷链接：${NC}"
echo "  • Mixamo: https://www.mixamo.com/"
echo "  • 3dRetarget: https://3dretarget.com/zh"
echo "  • VRM 文档: https://vrm.dev/"
echo "  • 项目动画目录: $ANIMATIONS_DIR"
echo ""

echo -e "${GREEN}✅ 完成！如有问题请查看文档：${NC}"
echo "   docs/VRM_ANIMATION_RESOURCES.md"
echo "   docs/VRM_ANIMATION_LEARNING_PATH.md"
echo ""



























