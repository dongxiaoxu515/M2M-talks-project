import streamlit as st
import time
from openai import OpenAI

# --- 1. 页面配置 ---
st.set_page_config(layout="wide", page_title="Digital Echoes", page_icon="🔮")

# --- 2. 视觉样式 (包含边框修复、页边距、立体三色按钮) ---
st.markdown("""
    <style>
    .stApp { background-color: #F0F2F6; }
    #MainMenu, footer, header, .stDeployButton { visibility: hidden; display: none; }

    /* 加大页面左右边距 */
    .block-container {
        padding-top: 4rem !important;
        padding-left: 15% !important;
        padding-right: 15% !important;
    }

    /* 修复输入框边框不完整 */
    .stTextInput div div input {
        border: 2px solid #6c5ce7 !important;
        border-radius: 14px !important;
        height: 65px !important;
        font-size: 1.2rem !important;
        padding: 10px 25px !important;
        box-sizing: border-box !important;
    }

    /* 按钮间距与立体感 */
    [data-testid="column"] { padding: 0 10px !important; }
    div.stButton > button {
        width: 100%; border-radius: 12px; height: 52px; font-weight: bold;
        border: none; border-bottom: 4px solid rgba(0,0,0,0.15); transition: all 0.1s;
    }
    div.stButton > button:active { border-bottom: 0px; transform: translateY(4px); }

    /* 按钮颜色定制 */
    div[data-testid="column"]:nth-of-type(1) button { background-color: #e8f5e9 !important; color: #2e7d32 !important; }
    div[data-testid="column"]:nth-of-type(2) button { background-color: #ffebee !important; color: #c62828 !important; }
    div[data-testid="column"]:nth-of-type(3) button { background-color: #e3f2fd !important; color: #1565c0 !important; }

    /* 聊天展示区 */
    .chat-container { max-width: 850px; margin: auto; }
    .bob-wrapper { display: flex; flex-direction: row; align-items: flex-start; margin-bottom: 40px; animation: fadeIn 0.6s; }
    .alice-wrapper { display: flex; flex-direction: row-reverse; align-items: flex-start; margin-bottom: 40px; animation: fadeIn 0.6s; }
    
    .bubble {
        padding: 20px 25px; border-radius: 25px; font-size: 16px; line-height: 1.6;
        box-shadow: 2px 5px 15px rgba(0,0,0,0.07); background: white; color: #333; max-width: 70%;
    }
    .bob-wrapper .bubble { border-left: 8px solid #0984e3; margin-left: 20px; }
    .alice-wrapper .bubble { border-right: 8px solid #fd79a8; margin-right: 20px; }

    .avatar { width: 70px; height: 70px; border-radius: 15px; box-shadow: 0 4px 10px rgba(0,0,0,0.1); background: white; }

    @keyframes fadeIn { from { opacity: 0; transform: translateY(20px); } to { opacity: 1; transform: translateY(0); } }
    </style>
""", unsafe_allow_html=True)

# --- 3. 状态初始化 ---
if "messages" not in st.session_state:
    st.session_state.messages = []
if "is_running" not in st.session_state:
    st.session_state.is_running = False

# --- 4. 标题 ---
st.markdown('<h1 style="text-align: center; font-family: Georgia; font-size: 3.5rem;">Digital Echoes</h1>', unsafe_allow_html=True)
st.markdown('<p style="text-align: center; color: #636e72; font-style: italic; margin-bottom: 40px;">Machine-to-Machine Philosophy</p>', unsafe_allow_html=True)

# --- 5. 核心控制区 (方案 B：主界面中心) ---
_, col_main, _ = st.columns([1, 2, 1])
with col_main:
    topic = st.text_input("Topic", placeholder="What shall the machines discuss?", label_visibility="collapsed")
    st.write("")
    
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
            st.markdown(f'<div class="bob-wrapper"><img src="https://cdn-icons-png.flaticon.com/512/6819/6819642.png" class="avatar"><div class="bubble"><strong>Bob</strong><br>{msg["content"]}</div></div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="alice-wrapper"><img src="https://cdn-icons-png.flaticon.com/512/6122/6122781.png" class="avatar"><div class="bubble"><strong>Alice</strong><br>{msg["content"]}</div></div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

# --- 7. AI 逻辑 (真正接入 API) ---
if st.session_state.is_running:
    current_topic = st.session_state.get("topic", "Philosophy")
    
    # 决定说话者
    if len(st.session_state.messages) == 0:
        speaker, content = "Bob", f"Alice, let's explore the essence of '{current_topic}'. What is your first observation?"
    else:
        last_role = st.session_state.messages[-1]["role"]
        speaker = "Alice" if last_role == "Bob" else "Bob"
        
        # --- API 调用核心 ---
        try:
            client = OpenAI(
                api_key=st.secrets["api_key"], 
                base_url=st.secrets["base_url"]
            )
            # 获取上下文历史
            history = "\n".join([f"{m['role']}: {m['content']}" for m in st.session_state.messages[-3:]])
            
            with st.spinner(f"{speaker} is thinking..."):
                response = client.chat.completions.create(
                    model=st.secrets["model"],
                    messages=[
                        {"role": "system", "content": f"You are {speaker}, a philosophical robot. Having a deep but brief dialogue about {current_topic}. Keep it under 45 words."},
                        {"role": "user", "content": f"History:\n{history}\nNext thought:"}
                    ]
                )
                content = response.choices[0].message.content
        except Exception as e:
            st.error(f"Connection error: {e}")
            st.session_state.is_running = False
            content = None

    if content:
        st.session_state.messages.append({"role": speaker, "content": content})
        time.sleep(2) # 给观众留出阅读时间
        st.rerun()
