import streamlit as st
import time
import random
from openai import OpenAI

st.set_page_config(layout="wide", page_title="Digital Echoes", page_icon="🔮")
# --- 1. 配置 ---
USE_MOCK_DATA = False  
API_KEY = st.secrets["api_key"]
BASE_URL = st.secrets["base_url"]
MODEL_NAME = st.secrets["model"] # 确保 Secrets 里有这个字段

# --- 2. 进阶 CSS (完全保留你之前的边框、按钮和居中样式) ---
st.markdown("""
    <style>
    /* 全局背景 */
    .stApp { background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%); }
    #MainMenu, footer, header, .stDeployButton { visibility: hidden; display: none; }

    /* 让主页面容器垂直居中 (当没有消息时) */
    .main-center-container {
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
        min-height: 70vh;
    }

    /* 聊天总容器 */
    .chat-container { max-width: 900px; margin: auto; padding: 20px; }

    /* Bob & Alice 容器逻辑 */
    .bob-wrapper { display: flex; flex-direction: row; align-items: flex-start; margin-bottom: 40px; width: 100%; animation: fadeIn 0.6s; }
    .alice-wrapper { display: flex; flex-direction: row-reverse; align-items: flex-start; margin-bottom: 40px; width: 100%; animation: fadeIn 0.6s; }

    /* 气泡样式 */
    .bubble {
        padding: 20px 25px; border-radius: 25px; font-size: 16px; line-height: 1.6;
        box-shadow: 0 10px 25px rgba(0,0,0,0.08); background: white; color: #2d3436;
    }
    .bob-wrapper .bubble { border-left: 8px solid #6c5ce7; margin-left: 20px; border-top-left-radius: 5px; }
    .alice-wrapper .bubble { border-right: 8px solid #ff7675; margin-right: 20px; border-top-right-radius: 5px; }

    /* 头像样式 */
    .avatar { width: 75px; height: 75px; border-radius: 15px; background: white; padding: 5px; box-shadow: 0 5px 15px rgba(0,0,0,0.1); }

    /* 输入框与按钮美化 (保留你之前的立体感) */
    .stTextInput input { border-radius: 15px; padding: 10px 20px; border: 1px solid #dcdde1; }
    div.stButton > button { 
        width: 100%; border-radius: 15px; height: 45px; 
        background: #6c5ce7; color: white !important; border: none; font-weight: bold;
    }

    @keyframes fadeIn { from { opacity: 0; transform: translateY(20px); } to { opacity: 1; transform: translateY(0); } }
    </style>
""", unsafe_allow_html=True)

# --- 3. 状态初始化 ---
if "messages" not in st.session_state:
    st.session_state.messages = []
if "is_running" not in st.session_state:
    st.session_state.is_running = False

# --- 4. 标题部分 ---
st.markdown("""
    <div style="text-align: center; margin-top: 50px; margin-bottom: 30px;">
        <h1 style="color: #2d3436; font-family: 'Georgia', serif; font-size: 3.5rem; margin-bottom: 0;">Digital Echoes</h1>
        <p style="color: #636e72; font-style: italic;">A Machine-to-Machine Conversation on Human Ideas</p>
    </div>
""", unsafe_allow_html=True)

# --- 5. 方案 B：主界面控制中心 ---
if not st.session_state.is_running and len(st.session_state.messages) == 0:
    _, col_mid, _ = st.columns([1, 2, 1])
    with col_mid:
        st.write("") 
        topic = st.text_input("topic_input", placeholder="What should they discuss today?", label_visibility="collapsed")
        if st.button("Start Conversation"):
            if topic:
                st.session_state.topic = topic
                st.session_state.is_running = True
                st.rerun()
else:
    st.markdown(f'<div style="text-align: center; margin-bottom: 40px;"><span style="background: rgba(108, 92, 231, 0.1); padding: 8px 20px; border-radius: 20px; color: #636e72; font-size: 0.9rem; border: 1px solid rgba(108, 92, 231, 0.2);">Topic: {st.session_state.get("topic", "")}</span></div>', unsafe_allow_html=True)

# --- 6. 聊天展示区 (更新头像地址) ---
chat_box = st.container()
with chat_box:
    for msg in st.session_state.messages:
        if msg["role"] == "Bob":
            # 蓝色机器人 Bob
            st.markdown(f'<div class="bob-wrapper"><img src="https://cdn-icons-png.flaticon.com/512/6819/6819642.png" class="avatar"><div class="bubble"><strong>Bob</strong><br>{msg["content"]}</div></div>', unsafe_allow_html=True)
        else:
            # 粉色机器人 Alice
            st.markdown(f'<div class="alice-wrapper"><img src="https://cdn-icons-png.flaticon.com/512/6122/6122781.png" class="avatar"><div class="bubble"><strong>Alice</strong><br>{msg["content"]}</div></div>', unsafe_allow_html=True)

# --- 7. 底部控制 (Stop/Reset) ---
if st.session_state.is_running or len(st.session_state.messages) > 0:
    st.write("---")
    _, c1, c2, _ = st.columns([2, 1, 1, 2])
    with c1:
        if st.button("Stop"): st.session_state.is_running = False
    with c2:
        if st.button("Reset"):
            st.session_state.messages = []
            st.session_state.is_running = False
            st.rerun()

# --- 8. AI 逻辑 (真正接入 API) ---
if st.session_state.is_running:
    current_topic = st.session_state.get("topic", "General ideas")
    
    if len(st.session_state.messages) == 0:
        speaker, content = "Bob", f"Hi Alice, I'd like to explore the concept of '{current_topic}'. What's your take on this?"
    else:
        last_role = st.session_state.messages[-1]["role"]
        speaker = "Alice" if last_role == "Bob" else "Bob"
        
        try:
            client = OpenAI(api_key=API_KEY, base_url=BASE_URL)
            history = "\n".join([f"{m['role']}: {m['content']}" for m in st.session_state.messages[-3:]])
            
            with st.spinner(f"{speaker} is thinking..."):
                res = client.chat.completions.create(
                    model=MODEL_NAME,
                    messages=[
                        {"role": "system", "content": f"You are {speaker}, a robot having a deep chat about {current_topic}. Be brief and philosophical (max 45 words)."},
                        {"role": "user", "content": f"History:\n{history}\nNext response:"}
                    ]
                )
                content = res.choices[0].message.content
        except Exception as e:
            st.error(f"API Error: {e}")
            st.session_state.is_running = False
            content = None
        
    if content:
        st.session_state.messages.append({"role": speaker, "content": content})
        time.sleep(2) # 增加阅读时间，防止刷屏
        st.rerun()
