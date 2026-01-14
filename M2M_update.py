import streamlit as st
import time
import random
from openai import OpenAI

st.set_page_config(layout="wide", page_title="Digital Echoes", page_icon="🔮")
# --- 1. 配置 ---
USE_MOCK_DATA = False  
API_KEY = st.secrets["api_key"]
BASE_URL = st.secrets["base_url"]
import streamlit as st
import time
import random
from openai import OpenAI

# --- 1. 页面配置 ---
st.set_page_config(layout="wide", page_title="Digital Echoes", page_icon="🔮")

# --- 2. 增强版 CSS ---
st.markdown("""
    <style>
    .stApp { background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%); }
    #MainMenu, footer, header, .stDeployButton { visibility: hidden; display: none; }

    /* 顶部固定输入区样式 */
    .input-card {
        background: white;
        padding: 20px;
        border-radius: 20px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.05);
        margin-bottom: 40px;
    }

    /* 聊天容器 */
    .chat-container { max-width: 900px; margin: auto; padding: 20px; }

    /* 左右布局逻辑 */
    .bob-wrapper { display: flex; flex-direction: row; align-items: flex-start; margin-bottom: 40px; width: 100%; animation: fadeIn 0.6s; }
    .alice-wrapper { display: flex; flex-direction: row-reverse; align-items: flex-start; margin-bottom: 40px; width: 100%; animation: fadeIn 0.6s; }

    /* 气泡样式 */
    .bubble {
        padding: 20px 25px; border-radius: 25px; font-size: 16px; line-height: 1.6;
        box-shadow: 0 10px 25px rgba(0,0,0,0.08); background: white; color: #2d3436;
        max-width: 75%;
    }
    .bob-wrapper .bubble { border-left: 8px solid #0984e3; margin-left: 20px; border-top-left-radius: 5px; }
    .alice-wrapper .bubble { border-right: 8px solid #fd79a8; margin-right: 20px; border-top-right-radius: 5px; }

    /* 机器人头像 */
    .avatar { width: 70px; height: 70px; border-radius: 20%; background: white; padding: 5px; box-shadow: 0 5px 15px rgba(0,0,0,0.1); }

    @keyframes fadeIn { from { opacity: 0; transform: translateY(20px); } to { opacity: 1; transform: translateY(0); } }
    </style>
""", unsafe_allow_html=True)

# --- 3. 状态初始化 ---
if "messages" not in st.session_state:
    st.session_state.messages = []
if "is_running" not in st.session_state:
    st.session_state.is_running = False

# --- 4. 标题 ---
st.markdown('<h1 style="text-align: center; color: #2d3436; font-family: Georgia; font-size: 3rem;">Digital Echoes</h1>', unsafe_allow_html=True)

# --- 5. 方案 B：常驻主界面的输入框 ---
with st.container():
    _, col_mid, _ = st.columns([1, 2, 1])
    with col_mid:
        # 输入框始终存在
        topic = st.text_input("Enter Topic", placeholder="Type a topic for the robots...", label_visibility="collapsed")
        c1, c2 = st.columns(2)
        with c1:
            if st.button("Start / Update Topic"):
                if topic:
                    st.session_state.topic = topic
                    st.session_state.is_running = True
                    st.rerun()
        with c2:
            if st.button("Reset All"):
                st.session_state.messages = []
                st.session_state.is_running = False
                st.rerun()

st.markdown("---")

# --- 6. 聊天展示区 ---
chat_box = st.container()
with chat_box:
    for msg in st.session_state.messages:
        if msg["role"] == "Bob":
            # 蓝色机器人 Bob
            st.markdown(f'''
                <div class="bob-wrapper">
                    <img src="https://cdn-icons-png.flaticon.com/512/6819/6819642.png" class="avatar">
                    <div class="bubble"><strong>Bob</strong><br>{msg["content"]}</div>
                </div>
            ''', unsafe_allow_html=True)
        else:
            # 粉色机器人 Alice
            st.markdown(f'''
                <div class="alice-wrapper">
                    <img src="https://cdn-icons-png.flaticon.com/512/6122/6122781.png" class="avatar">
                    <div class="bubble"><strong>Alice</strong><br>{msg["content"]}</div>
                </div>
            ''', unsafe_allow_html=True)

# --- 7. 核心 AI 对话逻辑 (接回 API) ---
if st.session_state.is_running:
    current_topic = st.session_state.get("topic", "Technology")
    
    # 确定说话者
    if len(st.session_state.messages) == 0:
        speaker = "Bob"
        content = f"Hi Alice, I was just thinking about '{current_topic}'. What do you think about it?"
    else:
        last_role = st.session_state.messages[-1]["role"]
        speaker = "Alice" if last_role == "Bob" else "Bob"
        
        # 尝试调用真实 API
        try:
            client = OpenAI(
                api_key=st.secrets["api_key"], 
                base_url=st.secrets["base_url"]
            )
            # 获取最近的对话历史
            history = "\n".join([f"{m['role']}: {m['content']}" for m in st.session_state.messages[-3:]])
            
            with st.spinner(f"{speaker} is thinking..."):
                res = client.chat.completions.create(
                    model=st.secrets["model"],
                    messages=[
                        {"role": "system", "content": f"You are {speaker}, a robot. Having a friendly chat about {current_topic}. Keep it under 40 words."},
                        {"role": "user", "content": f"Conversation so far:\n{history}\nNext response:"}
                    ]
                )
                content = res.choices[0].message.content
        except Exception as e:
            st.error(f"API Error: {e}")
            st.session_state.is_running = False
            content = None

    if content:
        st.session_state.messages.append({"role": speaker, "content": content})
        time.sleep(1.5) # 给观众留阅读时间
        st.rerun()
