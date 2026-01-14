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
    border-radius: 14px !important;
    height: 65px !important; /* 调高高度，给边框留位置 */
    font-size: 1.3rem !important;
    padding: 10px 25px !important;
    background-color: white !important;
    line-height: 1.5 !important;
    box-sizing: border-box !important; /* 核心：让边框往内缩，不被切断 */
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

    @keyframes fadeIn { from { opacity: 0; transform: translateY(20px); } to { opacity: 1; transform: translateY(0); } }
    </style>
""", unsafe_allow_html=True)

# --- 3. 初始化 ---
if "messages" not in st.session_state:
    st.session_state.messages = []
if "is_running" not in st.session_state:
    st.session_state.is_running = False

# --- 4. 居中标题 ---
st.markdown('<h1 style="text-align: center; color: #2d3436; font-family: Georgia; font-size: 3.5rem; margin-top: 10px;">Digital Echoes</h1>', unsafe_allow_html=True)
st.markdown('<p style="text-align: center; color: #636e72; font-style: italic; margin-bottom: 50px;">Machine-to-Machine Philosophy</p>', unsafe_allow_html=True)

# --- 5. 核心控制区 (中间排列) ---
bt_col1, bt_col2, bt_col3 = st.columns(3)
    with bt_col1:
        st.button("START")
    with bt_col2:
        st.button("STOP")
    with bt_col3:
        st.button("RESET")
with col_main:
    # 输入话题
    topic = st.text_input("Topic", placeholder="What shall the machines discuss?", label_visibility="collapsed")
    
    st.write("") # 增加微小间距
    
    # 按钮横向排列
    bt_col1, bt_col2, bt_col3 = st.columns(3)
    with bt_col1:
        if st.button("START"):
            if topic:
                st.session_state.topic = topic
                st.session_state.is_running = True
                st.rerun()
    with bt_col2:
        if st.button("STOP"):
            st.session_state.is_running = False
    with bt_col3:
        if st.button("RESET"):
            st.session_state.messages = []
            st.session_state.is_running = False
            st.rerun()

st.markdown("<br><br>", unsafe_allow_html=True)

# --- 6. 聊天展示区 ---
chat_box = st.container()
with chat_box:
    # 增加内部容器以控制最大宽度
    st.markdown('<div class="chat-container">', unsafe_allow_html=True)
    for msg in st.session_state.messages:
        if msg["role"] == "Bob":
            st.markdown(f'''
                <div class="bob-wrapper">
                    <img src="https://cdn-icons-png.flaticon.com/512/6819/6819642.png" class="avatar">
                    <div class="bubble"><strong>Bob</strong><br>{msg["content"]}</div>
                </div>
            ''', unsafe_allow_html=True)
        else:
            st.markdown(f'''
                <div class="alice-wrapper">
                    <img src="https://cdn-icons-png.flaticon.com/512/6122/6122781.png" class="avatar">
                    <div class="bubble"><strong>Alice</strong><br>{msg["content"]}</div>
                </div>
            ''', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

# --- 7. AI 逻辑 (使用 Secrets) ---
if st.session_state.is_running:
    current_topic = st.session_state.get("topic", "Existence")
    
    if len(st.session_state.messages) == 0:
        speaker, content = "Bob", f"Alice, let us contemplate '{current_topic}'. What is your initial synthesis?"
    else:
        last_role = st.session_state.messages[-1]["role"]
        speaker = "Alice" if last_role == "Bob" else "Bob"
        
        try:
            client = OpenAI(api_key=st.secrets["api_key"], base_url=st.secrets["base_url"])
            history = "\n".join([f"{m['role']}: {m['content']}" for m in st.session_state.messages[-3:]])
            
            with st.spinner(f"{speaker} is processing..."):
                res = client.chat.completions.create(
                    model=st.secrets["model"],
                    messages=[
                        {"role": "system", "content": f"You are {speaker}, a philosophical AI. Discussing {current_topic}. Short & profound (max 40 words)."},
                        {"role": "user", "content": f"Recent thoughts:\n{history}\nYour turn:"}
                    ]
                )
                content = res.choices[0].message.content
        except Exception as e:
            st.error(f"Reconnecting... ({e})")
            st.session_state.is_running = False
            content = None

    if content:
        st.session_state.messages.append({"role": speaker, "content": content})
        time.sleep(2) # 阅读停顿
        st.rerun()
