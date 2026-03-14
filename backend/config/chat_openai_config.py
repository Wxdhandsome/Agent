# ========================================
# ChatOpenAI 统一配置
# 在此修改或通过环境变量覆盖，可统一替换项目中所有 API Key 和 Base URL
# ========================================

import os

# 兼容环境变量：未设置时使用下方默认值
CHAT_OPENAI_BASE_URL = os.getenv(
    "CHAT_OPENAI_BASE_URL",
    "http://1.194.201.134:50178/v1",
)
CHAT_OPENAI_API_KEY = os.getenv(
    "CHAT_OPENAI_API_KEY",
    "kJ94sWuDogW49zapnePumpVRQgFcz2O1jb3S7C35ZoHp8HRnVdz1CryyyZftsEmFHFKS4egaoY1Jyvvi",
)

# 可选：默认模型与温度（代码审查等场景使用）
CHAT_OPENAI_DEFAULT_MODEL = os.getenv("CHAT_OPENAI_DEFAULT_MODEL", "Qwen3-32B-FP8")
CHAT_OPENAI_DEFAULT_TEMPERATURE = float(os.getenv("CHAT_OPENAI_DEFAULT_TEMPERATURE", "0.3"))
