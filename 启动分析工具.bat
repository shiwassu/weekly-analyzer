@echo off
chcp 65001 >nul
title 周数据分析工具
echo ========================================
echo       周数据分析工具 启动器
echo ========================================
echo.

cd /d "%~dp0"

:: 检查是否已有Streamlit进程在运行
tasklist /FI "IMAGENAME eq streamlit.exe" 2>NUL | find /I /N "streamlit.exe">NUL
if "%ERRORLEVEL%"=="0" (
    echo [提示] 检测到Streamlit服务已在运行
    echo [提示] 正在打开浏览器...
    start http://localhost:8501
    echo.
    echo 按任意键退出...
    pause >nul
    exit
)

echo [1/3] 正在启动Streamlit服务...
echo.

:: 延迟3秒后打开浏览器
start "" cmd /c "timeout /t 4 /nobreak >nul && start http://localhost:8501"

echo [2/3] 等待服务启动...
echo [3/3] 浏览器将在4秒后自动打开
echo.
echo ----------------------------------------
echo  访问地址: http://localhost:8501
echo  关闭此窗口将停止服务
echo ----------------------------------------
echo.

:: 启动Streamlit（headless模式跳过邮箱提示）
streamlit run app.py --server.headless true

pause
