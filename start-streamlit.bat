@echo off
chcp 65001 >nul
echo ========================================
echo LangFlow 工作流对话系统启动中...
echo ========================================
echo.

cd /d "%~dp0"

echo 正在检查依赖...
if not exist ".venv\Scripts\activate.bat" (
    echo 虚拟环境不存在，请先运行项目初始化
    pause
    exit /b 1
)

call .venv\Scripts\activate.bat

echo.
echo 启动 Streamlit 对话系统...
echo.
streamlit run streamlit_app.py --server.port 8501

pause
