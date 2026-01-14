import streamlit as st
import time
import random
from openai import OpenAI

st.set_page_config(layout="wide", page_title="Digital Echoes", page_icon="🔮")
# --- 1. 配置 ---
USE_MOCK_DATA = False  
API_KEY = st.secrets["api_key"]
BASE_URL = st.secrets["base_url"]

# --- 2. 视觉样式 (回归图一配色 + 立体按钮 + 居中布局) ---
st.markdown("""
    <style>
    /* 回归图一的经典灰蓝背景 */
    .stApp { background-color: #F0F2F6; }
    #MainMenu, footer, header, .stDeployButton { visibility: hidden; display: none; }

    /* 中间控制区容器 */
    .control-panel {
        background: white;
        padding: 30px;
        border-radius: 20px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.05);
        margin-bottom: 50px;
        border: 1px solid #E0E0E0;
    }

    /* 增强输入框视觉 */
    .stTextInput input {
        border: 2px solid #6c5ce7 !important;
        border-radius: 12px !important;
        height: 50px !important;
        font-size: 1.1rem !important;
        box-shadow: inset 0 2px 4px rgba(0,0,0,0.05) !important;
    }

    /* 聊天气泡布局 */
    .chat-container { max-width: 900px; margin: auto; }
    .bob-wrapper { display: flex; flex-direction: row; align-items: flex-start; margin-bottom: 40px; animation: fadeIn 0.6s; }
    .alice-wrapper { display: flex; flex-direction: row-reverse; align-items: flex-start; margin-bottom: 40px; animation: fadeIn 0.6s; }

    .bubble {
        padding: 20px 25px; border-radius: 25px; font-size: 16px; line-height: 1.6;
        box-shadow: 2px 4px 12px rgba(0,0,0,0.08); background: white; color: #333;
        max-width: 70%;
    }
    .bob-wrapper .bubble { border-left: 8px solid #0984e3; margin-left: 20px; border-top-left-radius: 5px; }
    .alice-wrapper .bubble { border-right: 8px solid #fd79a8; margin-right: 20px; border-top-right-radius: 5px; }

    /* 头像固定 */
    .avatar { width: 75px; height: 75px; border-radius: 15px; background: white; padding: 5px; box-shadow: 0 4px 10px rgba(0,0,0,0.1); }

    /* 浅色立体按钮样式 */
    div.stButton > button {
        border-radius: 12px;
        height: 48px;
        font-weight: bold;
        border: none;
        border-bottom: 4px solid rgba(0,0,0,0.2); /* 底部厚度实现立体感 */
        transition: all 0.1s;
    }
    div.stButton > button:active {
        border-bottom: 0px solid transparent;
        transform: translateY(4px);
    }

    /* 三种按钮的具体颜色 (浅色立体风格) */
    /* Start 绿色 */
    div[data-testid="column"]:nth-of-type(1) button { background-color: #dafff1 !important; color: #1b5e20 !important; }
    /* Stop 红色 */
    div[data-testid="column"]:nth-of-type(2) button { background-color: #ffebee !important; color: #b71c1c !important; }
    /* Reset 蓝色 */
    div[data-testid="column"]:nth-of-type(3) button { background-color: #e3f2fd !important; color: #0d47a1 !important; }

    @keyframes fadeIn { from { opacity: 0; transform: translateY(20px); } to { opacity: 1; transform: translateY(0); } }
    </style>
""", unsafe_allow_html=True)

# --- 3. 初始化 ---
if "messages" not in st.session_state:
    st.session_state.messages = []
if "is_running" not in st.session_state:
    st.session_state.is_running = False

# --- 4. 居中标题 ---
st.markdown('<h1 style="text-align: center; color: #2d3436; font-family: Georgia; font-size: 3.5rem; margin-top: 30px;">Digital Echoes</h1>', unsafe_allow_html=True)
st.markdown('<p style="text-align: center; color: #636e72; font-style: italic; margin-bottom: 40px;">Machine-to-Machine Philosophy</p>', unsafe_allow_html=True)

# --- 5. 核心控制区 (题目下面，中间排列) ---
_, col_main, _ = st.columns([1, 2, 1])
with col_main:
    topic = st.text_input("Topic", placeholder="Enter a topic for the discussion...", label_visibility="collapsed")
    
    # 三个按钮横向排列
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

st.markdown("<br>", unsafe_allow_html=True)

# --- 6. 聊天展示区 ---
chat_box = st.container()
with chat_box:
    for msg in st.session_state.messages:
        if msg["role"] == "Bob":
            # 蓝色机器人 (Bob)
            st.markdown(f'''
                <div class="bob-wrapper">
                    <img src="https://cdn-icons-png.flaticon.com/512/6819/6819642.png" class="avatar">
                    <div class="bubble"><strong>Bob</strong><br>{msg["content"]}</div>
                </div>
            ''', unsafe_allow_html=True)
        else:
            # 粉色机器人 (Alice)
            st.markdown(f'''
                <div class="alice-wrapper">
                    <img src="https://cdn-icons-png.flaticon.com/512/6122/6122781.png" class="avatar">
                    <div class="bubble"><strong>Alice</strong><br>{msg["content"]}</div>
                </div>
            ''', unsafe_allow_html=True)

# --- 7. AI 逻辑 ---
if st.session_state.is_running:
    current_topic = st.session_state.get("topic", "Art and Life")
    
    if len(st.session_state.messages) == 0:
        speaker, content = "Bob", f"Hello Alice, let's explore the topic of '{current_topic}'. What's your opening thought?"
    else:
        last_role = st.session_state.messages[-1]["role"]
        speaker = "Alice" if last_role == "Bob" else "Bob"
        
        try:
            client = OpenAI(api_key=st.secrets["api_key"], base_url=st.secrets["base_url"])
            history = "\n".join([f"{m['role']}: {m['content']}" for m in st.session_state.messages[-3:]])
            
            with st.spinner(f"{speaker} is formulating thoughts..."):
                res = client.chat.completions.create(
                    model=st.secrets["model"],
                    messages=[
                        {"role": "system", "content": f"You are {speaker}, an intelligent machine. Discussing {current_topic} with another AI. Be philosophical and brief (under 45 words)."},
                        {"role": "user", "content": f"History:\n{history}\nNext:"}
                    ]
                )
                content = res.choices[0].message.content
        except Exception as e:
            st.error(f"Waiting for connection... ({e})")
            st.session_state.is_running = False
            content = None

    if content:
        st.session_state.messages.append({"role": speaker, "content": content})
        time.sleep(2) # 留出阅读时间
        st.rerun()
