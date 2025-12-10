# 🎀 ChatTTS 音色设置指南

## ✅ 当前配置

**已固定为：seed=1234 (甜美萝莉音)**

- 音色特点：甜美可爱、音调较高
- 适合：二次元角色、萝莉角色
- 配置文件：`bridge/tts_config.json`

## 📝 配置详情

```json
{
  "engine": "chattts",
  "chattts": {
    "model_path": "/Users/user/Documents/tts/chattts/models/ChatTTS",
    "device": "auto",
    "temperature": 0.3,
    "seed": 1234,
    "output_dir": "tts_output",
    "_comment_seed": "固定音色种子：1234=甜美萝莉音"
  }
}
```

## 🎤 可选音色列表

经过测试，以下音色都适合二次元角色：

| Seed | 类型 | 特点 | 推荐场景 |
|------|------|------|----------|
| **1234** | ⭐ 甜美萝莉 | 音调高、可爱 | 幼女、萝莉角色 |
| 2468 | 活泼元气 | 充满活力、欢快 | 元气少女 |
| 3456 | 软萌治愈 | 温柔、治愈系 | 温柔姐姐、治愈系 |
| 5678 | 清纯自然 | 自然清新 | 邻家女孩 |
| 7890 | 元气少女 | 活泼开朗 | 运动系少女 |
| 9999 | 可爱系 | 俏皮可爱 | 调皮小妹 |
| 11111 | 温柔系 | 温婉柔和 | 大和抚子 |

## 🔧 如何切换音色

### 方法 1: 手动修改配置文件

1. 编辑 `bridge/tts_config.json`
2. 修改 `seed` 值（如改为 3456）
3. 重启服务器：

```bash
cd bridge
# 停止旧服务器
kill $(ps aux | grep websocket_server | grep -v grep | awk '{print $2}')

# 启动新服务器
./start_with_chattts.sh
```

### 方法 2: 使用测试脚本寻找新音色

```bash
cd bridge
source /Users/user/Documents/tts/chattts/venv/bin/activate
python find_cute_voice.py
```

然后试听生成的音频，选择你喜欢的 seed。

## 🎧 试听音色

所有测试音色都保存在：`bridge/tts_output/voice_test/`

试听命令：

```bash
# 试听 seed=1234 (当前使用)
afplay bridge/tts_output/voice_test/voice_seed_1234.wav

# 试听其他音色
afplay bridge/tts_output/voice_test/voice_seed_2468.wav
afplay bridge/tts_output/voice_test/voice_seed_3456.wav
afplay bridge/tts_output/voice_test/voice_seed_7890.wav
```

## 🌟 推荐音色组合

### 萝莉角色
- **首选**: seed=1234 (甜美萝莉)
- 备选: seed=9999 (可爱系)

### 元气少女
- **首选**: seed=2468 (活泼元气)
- 备选: seed=7890 (元气少女)

### 温柔姐姐
- **首选**: seed=3456 (软萌治愈)
- 备选: seed=11111 (温柔系)

## 🎨 高级调整

### 调整温度参数

`temperature` 控制语音变化程度：

```json
{
  "temperature": 0.3  // 默认值
  // 0.1-0.2: 更稳定，变化少
  // 0.3-0.4: 平衡（推荐）
  // 0.5-0.7: 更有变化，更生动
}
```

### 情感标签

在文本中可以添加情感标签：

```
"哈哈[laugh]，太好玩了！"          # 添加笑声
"嗯...[uv_break]我想想"           # 添加停顿
"太[speed_7]激动了[laugh]！"     # 快速 + 笑声
```

## 📊 测试结果

已验证所有音色在多次生成中保持一致：

- ✅ 音色稳定性：完全一致
- ✅ 甜美度：非常高（seed=1234）
- ✅ 萝莉感：强烈
- ✅ 自然度：优秀

## 🔄 快速切换脚本

如果需要经常切换音色，可以创建快速切换脚本：

```bash
# 创建切换脚本
cat > bridge/switch_voice.sh << 'EOF'
#!/bin/bash
SEED=$1
if [ -z "$SEED" ]; then
    echo "用法: ./switch_voice.sh <seed>"
    echo "例如: ./switch_voice.sh 1234"
    exit 1
fi

# 更新配置
sed -i '' "s/\"seed\": [0-9]*/\"seed\": $SEED/" bridge/tts_config.json
echo "✅ 已切换到 seed=$SEED"
echo "   重启服务器生效: cd bridge && ./start_with_chattts.sh"
EOF

chmod +x bridge/switch_voice.sh

# 使用方法
./switch_voice.sh 3456  # 切换到 seed=3456
```

## 💡 提示

1. **首次使用**: 建议使用 seed=1234，这是最经典的萝莉音
2. **测试新音色**: 使用 `find_cute_voice.py` 生成样本再选择
3. **保持一致**: 固定 seed 后，每次生成都是同样的音色
4. **微调效果**: 可以调整 temperature 参数获得不同变化程度

## 📚 相关文档

- [CHATTTS_USAGE.md](CHATTTS_USAGE.md) - 完整使用指南
- [CHATTTS_TEST_RESULT.md](../CHATTTS_TEST_RESULT.md) - 测试报告
- [TTS_README.md](../TTS_README.md) - 快速参考

---

**当前音色**: seed=1234 (甜美萝莉音) 🎀
**状态**: ✅ 已固定
**更新时间**: 2024年12月7日








