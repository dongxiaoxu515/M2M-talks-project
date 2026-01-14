import streamlit as st
import time
import random
from openai import OpenAI

st.set_page_config(layout="wide", page_title="Digital Echoes", page_icon="🔮")
# --- 1. 配置 ---
USE_MOCK_DATA = False  
API_KEY = st.secrets["api_key"]
BASE_URL = st.secrets["base_url"]

# --- 2. 视觉样式优化 (加大页边距 + 修复输入框) ---
st.markdown("""
    <style>
    /* 回归经典灰蓝背景 */
    .stApp { background-color: #F0F2F6; }
    #MainMenu, footer, header, .stDeployButton { visibility: hidden; display: none; }

    /* 整体页面布局控制：加大页边距 */
    .block-container {
        padding-top: 5rem !important;
        padding-bottom: 5rem !important;
        padding-left: 10% !important;
        padding-right: 10% !important;
    }

    /* 增强输入框视觉：确保显示完整 */
    .stTextInput div div input {
        border: 2px solid #6c5ce7 !important;
        border-radius: 12px !important;
        height: 60px !important; /* 增加高度防止切断 */
        font-size: 1.2rem !important;
        padding: 10px 20px !important;
        background-color: white !important;
    }

    /* 聊天气泡布局：缩小最大宽度以增加视觉页边距 */
    .chat-container { 
        max-width: 800px; 
        margin: auto; 
    }

    .bob-wrapper { display: flex; flex-direction: row; align-items: flex-start; margin-bottom: 45px; animation: fadeIn 0.6s; }
    .alice-wrapper { display: flex; flex-direction: row-reverse; align-items: flex-start; margin-bottom: 45px; animation: fadeIn 0.6s; }

    .bubble {
        padding: 22px 28px; border-radius: 25px; font-size: 16px; line-height: 1.6;
        box-shadow: 2px 4px 15px rgba(0,0,0,0.06); background: white; color: #333;
        max-width: 75%;
    }
    .bob-wrapper .bubble { border-left: 8px solid #0984e3; margin-left: 20px; border-top-left-radius: 5px; }
    .alice-wrapper .bubble { border-right: 8px solid #fd79a8; margin-right: 20px; border-top-right-radius: 5px; }

    /* 头像样式 */
    .avatar { width: 70px; height: 70px; border-radius: 15px; background: white; padding: 5px; box-shadow: 0 4px 10px rgba(0,0,0,0.1); }

    /* 浅色立体按钮 */
    div.stButton > button {
        border-radius: 12px;
        height: 52px;
        font-weight: bold;
        border: none;
        border-bottom: 4px solid rgba(0,0,0,0.15);
        transition: all 0.1s;
        font-size: 1rem !important;
    }
    div.stButton > button:active {
        border-bottom: 0px solid transparent;
        transform: translateY(4px);
    }

    /* 按钮颜色配置 */
    div[data-testid="column"]:nth-of-type(1) button { background-color: #e8f5e9 !important; color: #2e7d32 !important; }
    div[data-testid="column"]:nth-of-type(2) button { background-color: #ffebee !important; color: #c62828 !important; }
    div[data-testid="column"]:nth-of-type(3) button { background-color: #e3f2fd !important; color: #1565c0 !important; }

    @keyframes fadeIn { from { opacity: 0; transform: translateY(20px);
