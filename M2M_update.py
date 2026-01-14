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

  /* 聊天总容器：增加页边距 */
    .chat-container { max-width: 800px; margin: auto; padding: 40px 20px; }

    /* 通语气泡样式：增加渐变和阴影深度 */
    .bubble {
        padding: 18px 24px; 
        border-radius: 20px; 
        font-size: 16px; 
        line-height: 1.6;
        background: #ffffff;
        color: #2d3436;
        /* 增加分层阴影，让气泡更有悬浮感 */
        box-shadow: 0 4px 15px rgba(0,0,0,0.05), 0 1px 2px rgba(0,0,0,0.1);
        max-width: 55%; /* 缩短宽度 */
        position: relative;
        transition: all 0.3s ease; /* 增加平滑动画 */
    }

    /* 鼠标悬停效果：微小放大和阴影增强 */
    .bubble:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(0,0,0,0.1);
    }

    /* Bob 的气泡：增加左侧尖角小尾巴 */
    .bob-wrapper .bubble { 
        border-left: 6px solid #6c5ce7; 
        margin-left: 25px; 
        background: linear-gradient(to bottom right, #ffffff, #f9f8ff);
    }
    .bob-wrapper .bubble::before {
        content: "";
        position: absolute;
        left: -10px; top: 20px;
        border-style: solid;
        border-width: 10px 10px 10px 0;
        border-color: transparent #6c5ce7 transparent transparent;
    }

    /* Alice 的气泡：增加右侧尖角小尾巴 */
    .alice-wrapper .bubble { 
        border-right: 6px solid #ff7675; 
        margin-right: 25px; 
        background: linear-gradient(to bottom left, #ffffff, #fffafa);
    }
    .alice-wrapper .bubble::after {
        content: "";
        position: absolute;
        right: -10px; top: 20px;
        border-style: solid;
        border-width: 10px 0 10px 10px;
        border-color: transparent transparent transparent #ff7675;
    }

    /* 头像美化：增加白色描边 */
    .avatar { 
        width: 70px; 
        height: 70px; 
        border-radius: 18px; 
        border: 3px solid white;
        box-shadow: 0 4px 10px rgba(0,0,0,0.1);
    }

   
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
           # --- 在 Section 6 找到这段进行替换 ---

# Bob 的图片
    st.markdown(f'''
        <div class="bob-wrapper">
            <img src="这里换成新的网址" class="avatar">
            <div class="bubble">...</div>
        </div>
    ''', unsafe_allow_html=True)

# Alice 的图片
st.markdown(f'''
    <div class="alice-wrapper">
        <img src="这里换成新的网址" class="avatar">
        <div class="bubble">...</div>
    </div>
''', unsafe_allow_html=True)
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
