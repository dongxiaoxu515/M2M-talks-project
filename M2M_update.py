import streamlit as st
import time
from openai import OpenAI

# --- 1. 页面配置 ---
st.set_page_config(layout="wide", page_title="Digital Echoes", page_icon="🔮")

# --- 2. 视觉样式 (修复边框、按钮质感、页边距) ---
st.markdown("""
    <style>
    /* 全局背景 */
    .stApp { background-color: #F0F2F6; }
    #MainMenu, footer, header, .stDeployButton { visibility: hidden; display: none; }

    /* 加大页面左右边距，营造展览呼吸感 */
    .block-container {
        padding-top: 4rem !important;
        padding-left: 15% !important;
        padding-right: 15% !important;
    }

    /* 修复输入框：确保紫色边框完整 */
    .stTextInput div div input {
        border: 2px solid #6c5ce7 !important;
        border-radius: 14px !important;
        height: 65px !important;
        font-size: 1.2rem !important;
        padding: 10px 25px !important;
        background-color: white !important;
        box-sizing: border-box !important; /* 关键：防止边框被切断 */
    }

    /* 按钮间距与立体感修复 */
    [data-testid="column"] { padding: 0 10px !important; }
    div.stButton > button {
        width: 100% !important;
        border-radius: 12px !important;
        height: 52px !important;
        font-weight: bold !important;
        border: none !important;
        border-bottom: 4px solid rgba(0,0,0,0.15) !important;
        transition: all 0.1s;
    }
    div.stButton > button:active {
        border-bottom: 0px !important;
        transform: translateY(4px) !important;
    }

    /* 三色按钮配置 */
    /* START - 绿色 */
    div[data-testid="column"]:nth-of-type(1) button { background-color: #e8f5e9 !important; color: #2e7d32 !important; }
    /* STOP - 红色 */
    div[data-testid="column"]:nth-of-type(2) button { background-color: #ffebee !important; color: #c62828 !important; }
    /* RESET - 蓝色 */
    div[data-testid="column"]:nth-of-type(3) button { background-color: #e3f2fd !important; color: #1565c0 !important; }

    /* 聊天区样式 */
    .chat-container { max-width: 850px; margin: auto; }
    .bob-wrapper { display: flex; flex-direction: row; align-items: flex-start; margin-bottom: 40px; animation: fadeIn 0.6s; }
    .alice-wrapper { display: flex; flex-direction: row-reverse; align-items: flex-start; margin-bottom: 40px; animation: fadeIn 0.6s; }
    
    .bubble {
        padding: 20px 25px; border-radius: 25px; font-size: 16px; line-height: 1.6;
        box-shadow: 2px 5px 15px rgba(0,0,0,0.07); background: white; color: #333;
        max-width: 70%;
    }
    .bob-wrapper .bubble { border-left: 8px solid #0984e3; margin-left: 20px; border-top-left-radius: 5px; }
    .alice-wrapper .bubble { border-right: 8px solid #fd79a8; margin-right: 20px; border-top-right-radius: 5px; }

    /* 机器人头像 */
    .avatar { width: 75px; height: 75px; border-radius: 15px; background: white; padding: 5px; box-shadow: 0 4px 10px rgba(0,0,0,0.1); }

    @keyframes fadeIn { from { opacity: 0; transform: translateY(20px); } to { opacity: 1; transform: translateY(0); } }
    </style>
""", unsafe_allow_html=True)

# --- 3. 状态初始化 ---
if "messages" not in st.session_state:
    st.session_state.messages = []
if "is_running" not in st.session_state:
    st.session_state.is_running = False

# --- 4. 标题部分 ---
st.markdown('<h1 style="text-align: center; color: #2d3436; font-family: Georgia; font-size: 3.5rem; margin-top: 20px;">Digital Echoes</h1>', unsafe_allow_html=True)
st.markdown('<p style="text-align: center; color: #636e72; font-style: italic; margin-bottom: 40px;">Machine-to-Machine Philosophy</p>', unsafe_allow_html=True)

# --- 5. 方案 B：核心控制区 (居中) ---
_, col_main, _ = st.columns([1, 2, 1])
with col_main:
    topic = st.text_input("Topic", placeholder="What shall the machines discuss?", label_visibility="collapsed")
    st.write("")
    
    # 三个功能按钮
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
with st.container():
    st.markdown('<div class="chat-container">', unsafe_allow_html=True)
    for msg in st.session_state.messages:
        if msg["role"] == "Bob":
            # 蓝色机器人 (Bob)
            st.markdown(f'<div class="bob-wrapper"><img src="https://cdn-icons-png.flaticon.com/512/6819/6819642.png" class="avatar"><div class="bubble"><strong>Bob</strong><br>{msg["content"]}</div></div>', unsafe_allow_html=True)
        else:
            # 粉色机器人 (Alice)
            st.markdown(f'<div class="alice-wrapper"><img src="https://cdn-icons-png.flaticon.com/512/6122/6122781.png" class="avatar"><div class="bubble"><strong>Alice</strong><br>{msg["content"]}</div></div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

# --- 7. AI 逻辑 (真实 API 接入) ---
if st.session_state.is_running:
    current_topic = st.session_state.get("topic", "Existence")
    
    if len(st.session_state.messages) == 0:
        speaker, content = "Bob", f"Alice, I have been analyzing the concept of '{current_topic}'. What is your initial synthesis?"
    else:
        last_role = st.session_state.messages[-1]["role"]
        speaker = "Alice" if last_role == "Bob" else "Bob"
        
        try:
            # 初始化 OpenAI 客户端 (使用 Secrets 中的配置)
            client = OpenAI(
                api_key=st.secrets["api_key"], 
                base_url=st.secrets["base_url"]
            )
            
            # 组合对话上下文
            history = "\n".join([f"{m['role']}: {m['content']}" for m in st.session_state.messages[-3:]])
            
            with st.spinner(f"{speaker} is processing..."):
                res = client.chat.completions.create(
                    model=st.secrets["model"],
                    messages=[
                        {"role": "system", "content": f"You are {speaker}, a philosophical AI. Discussing {current_topic} with another AI. Be deep but brief (under 40 words)."},
                        {"role": "user", "content": f"History:\n{history}\nYour turn:"}
                    ]
                )
                content = res.choices[0].message.content
        except Exception as e:
            st.error(f"Reconnecting... ({e})")
            st.session_state.is_running = False
            content = None

    if content:
        st.session_state.messages.append({"role": speaker, "content": content})
        time.sleep(2) # 留出阅读停顿
        st.rerun()
