import streamlit as st
import time
import random
from openai import OpenAI

# --- 1. 配置（如果 API 欠费，请保持 USE_MOCK_DATA = True） ---
USE_MOCK_DATA = False  
API_KEY = st.secrets["api_key"]
BASE_URL = st.secrets["base_url"]

# --- 2. 页面样式定义 ---
st.set_page_config(layout="wide", page_title="AI Talks")

st.markdown("""
    <style>
    /* 隐藏默认元素 */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .stDeployButton {display:none;}
    
    /* 侧边栏样式 */
    .topic-label { font-size: 1.2rem; font-weight: bold; margin-bottom: 10px; color: #333; }
    
    /* 聊天气泡布局 */
    .bob-container { display: flex; align-items: flex-start; margin-bottom: 25px; }
    .alice-container { display: flex; align-items: flex-start; justify-content: flex-end; margin-bottom: 25px; }
    .bubble { background-color: #F0F2F6; padding: 15px 20px; border-radius: 20px; max-width: 65%; font-family: sans-serif; line-height: 1.5; box-shadow: 2px 2px 5px rgba(0,0,0,0.05); }
    .avatar { width: 55px; height: 55px; margin: 0 15px; border-radius: 50%; }
    
    /* 按钮样式微调 */
    div.stButton > button { width: 100%; height: 40px; border-radius: 8px; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# --- 3. 状态初始化 ---
if "messages" not in st.session_state:
    st.session_state.messages = []
if "is_running" not in st.session_state:
    st.session_state.is_running = False

# --- 4. Sidebar (Topic 输入 + Start 按钮) ---
with st.sidebar:
    st.markdown('<p class="topic-label">Topic</p>', unsafe_allow_html=True)
    topic = st.text_input("Topic Input", placeholder="Conversation Topic Here", label_visibility="collapsed")
    
    # 将 Start 按钮放在这里
    if st.button("Start"):
        if topic:
            st.session_state.is_running = True
        else:
            st.warning("Please enter a topic!")

# --- 5. 主界面内容 ---
st.title("AI Talks:")

# 聊天记录容器
chat_box = st.container()
with chat_box:
    for msg in st.session_state.messages:
        if msg["role"] == "Bob":
            st.markdown(f"""
                <div class="bob-container">
                    <img src="https://cdn-icons-png.flaticon.com/512/4712/4712035.png" class="avatar">
                    <div class="bubble"><strong>Bob:</strong><br>{msg['content']}</div>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
                <div class="alice-container">
                    <div class="bubble"><strong>Alice:</strong><br>{msg['content']}</div>
                    <img src="https://cdn-icons-png.flaticon.com/512/4712/4712139.png" class="avatar">
                </div>
                """, unsafe_allow_html=True)

# 底部按钮控制区 (Stop, Reset 留在右侧)
st.write("---")
col_left, col_mid1, col_mid2, col_right = st.columns([4, 1, 1, 4])

with col_mid1:
    if st.button("Stop"):
        st.session_state.is_running = False

with col_mid2:
    if st.button("Reset"):
        st.session_state.messages = []
        st.session_state.is_running = False
        st.rerun()

# --- 6. 对话循环逻辑 ---
if st.session_state.is_running:
    # 确定当前的说话者
    if len(st.session_state.messages) == 0:
        speaker = "Bob"
        content = f"Hi Alice, I'd like to talk about '{topic}'. What's your take on this?"
    else:
        last_role = st.session_state.messages[-1]["role"]
        speaker = "Alice" if last_role == "Bob" else "Bob"
        
        if USE_MOCK_DATA:
            responses = ["Interesting point.", "I see, but why?", "That makes sense.", "I disagree with that.", "Tell me more."]
            content = random.choice(responses)
            time.sleep(1.5) # 模拟演示延时
        else:
            # 增加一个 loading 状态，让用户知道 AI 在思考
            with st.spinner(f"{speaker} is typing..."):
                try:
                    client = OpenAI(api_key=API_KEY, base_url=BASE_URL)
                    # 只取最近几条消息防止 Token 超限
                    history = "\n".join([f"{m['role']}: {m['content']}" for m in st.session_state.messages[-5:]])
                    
                    res = client.chat.completions.create(
                        model= st.secrets["model"],
                        messages=[
                            {"role": "system", "content": f"You are {speaker}. You are having a chat about '{topic}'. Keep responses short and conversational (max 30 words)."},
                            {"role": "user", "content": f"Previous conversation:\n{history}\nYour response:"}
                        ],
                        timeout=15.0 # 设置超时防止网页死锁
                    )
                    content = res.choices[0].message.content
                except Exception as e:
                    st.error(f"API Error: {e}")
                    st.session_state.is_running = False # 报错则停止循环
                    content = None

    if content:
        # 将新消息存入 session_state
        st.session_state.messages.append({"role": speaker, "content": content})
        # 【关键】给观众一点时间阅读，同时也给前端渲染留出时间
        time.sleep(2) 
        # 【关键】强制触发下一次重新运行
        st.rerun()
