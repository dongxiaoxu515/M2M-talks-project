import streamlit as st
import time
import random
from openai import OpenAI

st.set_page_config(layout="wide", page_title="Digital Echoes", page_icon="🔮")
# --- 1. 配置 ---
USE_MOCK_DATA = False  
API_KEY = st.secrets["api_key"]
BASE_URL = st.secrets["base_url"]

# --- 2. 页面样式定义 ---
st.markdown("""
    <div style="text-align: center; margin-bottom: 40px;">
        <h1 style="color: #1E293B; font-family: 'Georgia', serif; font-size: 3rem; margin-bottom: 0;">Digital Echoes</h1>
        <p style="color: #64748B; font-style: italic;">A Machine-to-Machine Conversation on Human Ideas</p>
    </div>
""", unsafe_allow_html=True)

st.markdown("""
    <style>
    /* 全局背景：浅灰色渐变，增加质感 */
    .stApp {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
    }

    /* 侧边栏：让它看起来像悬浮的面板 */
    section[data-testid="stSidebar"] {
        background-color: rgba(255, 255, 255, 0.8);
        backdrop-filter: blur(10px);
        border-right: 1px solid rgba(0,0,0,0.05);
    }

    /* 聊天气泡：玻璃拟态效果 */
    .bubble { 
        background: white;
        color: #333;
        padding: 18px 22px; 
        border-radius: 25px; 
        max-width: 70%; 
        font-size: 16px;
        line-height: 1.6;
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05);
        border: 1px solid rgba(255,255,255,0.8);
        margin-bottom: 10px;
    }

    /* Bob 的气泡：淡淡的紫色边框 */
    .bob-container .bubble {
        border-left: 5px solid #6D28D9;
        border-bottom-left-radius: 5px;
    }

    /* Alice 的气泡：淡淡的黄色边框 */
    .alice-container .bubble {
        border-right: 5px solid #F59E0B;
        border-bottom-right-radius: 5px;
    }

    /* 头像微调：增加呼吸感 */
    .avatar { 
        width: 60px; 
        height: 60px; 
        border-radius: 50%; 
        border: 2px solid white;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        transition: transform 0.3s ease;
    }
    .avatar:hover { transform: scale(1.1); }

    /* 按钮：彩色渐变 */
    div.stButton > button {
        background: linear-gradient(to right, #6D28D9, #7C3AED);
        color: white !important;
        border: none;
        transition: all 0.3s ease;
    }
    div.stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 5px 15px rgba(109, 40, 217, 0.4);
    }
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
