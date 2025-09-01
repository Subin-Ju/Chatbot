import streamlit as st
import speech_recognition as sr
import pyttsx3
import re
from dotenv import load_dotenv
from openai import OpenAI
import os

load_dotenv()
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
client = OpenAI()

# === 채팅 배경 ===
# 페이지 설정
st.set_page_config(page_title="음악 챗봇", layout="wide")

# 배경 & 채팅 스타일 CSS
st.markdown("""
<style>
.stApp { background: linear-gradient(180deg, #B7E4C7 20%, #FFADAD 90%); }
.chat-container { display: flex; flex-direction: column; gap: 10px; padding: 10px; }
.chat-box { padding: 10px; border-radius: 10px; max-width: 70%; word-wrap: break-word; }
.user { background-color: #DCF8C6; align-self: flex-end; }
.assistant { background-color: #F1F0F0; align-self: flex-start; }
</style>
""", unsafe_allow_html=True)

# === 헤더 ===
st.markdown("<h1 style='text-align:center;'>🍉Watermelon🍉</h1>", unsafe_allow_html=True)
st.markdown("<h3 style='text-align:center;'>물 흐르듯 원하는 노래를 찾아드립니다 🕵️</h3>", unsafe_allow_html=True)
st.markdown(
    "<p style='text-align:center;'>가수/노래/분위기/가사 등을 자유롭게 말해주세요.<br>노래를 찾았다면, '찾았다'라고 말하면 됩니다.</p>",
    unsafe_allow_html=True
)


# === 세션 상태 초기화 ===
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "system", "content": """
너는 사용자가 원하는 음악을 친절하게 찾아주는 챗봇이야.
사용자가 말하는 가수 이름, 노래 제목, 가사 일부, 분위기, 감정 키워드, 날씨 등을 기반으로 노래를 추천해줘.

### 지시 사항 ###
1. 사용자가 애매한 정보를 말해도 가장 정확히 유추하여 노래를 찾을 것
2. 여러 후보가 있을 경우, 6곡 이내로 압축해서 추천할 것
3. 사용자가 '찾았다'라고 말하면 대화를 중단할 것
4. 추론이 완료된 즉시 가장 빠른 속도로 추론하여 결과를 도출할 것
5. 부정확한 답변(가상의 가수나 노래 지어내기, 오류 정보 전달)은 금지할 것
        """}
    ]
if "recording" not in st.session_state:
    st.session_state.recording = False

client = OpenAI(api_key=OPENAI_API_KEY)
recognizer = sr.Recognizer()


# === TTS 함수 ===
def play_tts(text):
    engine = pyttsx3.init()
    engine.setProperty("rate", 180)
    engine.setProperty("volume", 1)
    engine.say(text)
    engine.runAndWait()
    engine.stop()

# === 음성 입력 함수 ===
def listen_user():
    mic = sr.Microphone()
    with mic as source:
        st.info("🎤 말씀해주세요...")
        audio = recognizer.listen(source, phrase_time_limit=5)
    try:
        return recognizer.recognize_google(audio, language="ko-KR")
    except Exception as e:
        st.error(f"음성 인식 오류: {e}")
        return None

# === GPT 응답 ===
def get_gpt_response(user_text):
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=st.session_state.messages,
        temperature=0.3,
        max_tokens=2048
    )
    answer = response.choices[0].message.content
    answer = re.sub(r"[*-]", "", answer)
    return answer

# === 녹음 버튼 UI ===
left, middle, right = st.columns([1, 2, 1])
if middle.button("🎙️ 녹음 시작/중지", use_container_width=True):
    st.session_state.recording = not st.session_state.recording

# === 녹음 상태 처리 ===
if st.session_state.recording:
    user_text = listen_user()
    if user_text:
        # 1️⃣ 사용자 말풍선 먼저 추가
        st.session_state.messages.append({"role": "user", "content": user_text})
        st.rerun()   # 즉시 rerun → 사용자 말풍선 먼저 보여줌

        # 2️⃣ GPT 호출
        reply = None
        if user_text.strip() == "찾았다":
            reply = "필요하면 또 찾아와요!😊"
            st.balloons()
        else:
            reply = get_gpt_response(user_text)

        # 3️⃣ 챗봇 답변 추가
        st.session_state.messages.append({"role": "assistant", "content": reply})
        play_tts(reply)
        st.rerun()

else:
    st.markdown("<p style='text-align:center;'>원하는 노래를 찾아보세요!</p>", unsafe_allow_html=True)

# === 대화 기록 표시 ===
for msg in st.session_state.messages[1:]:  # system 제외
    if msg["role"] == "user":
        st.markdown(f"""
        <div style="text-align: right; margin: 5px;">
            <div style="
                display: inline-block;
                background-color: #DCF8C6;
                color: #000;
                padding: 10px 15px;
                border-radius: 15px;
                max-width: 70%;
                word-wrap: break-word;">
                {msg['content']}
            </div>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <div style="text-align: left; margin: 5px;">
            <div style="
                display: inline-block;
                background-color: #F1F0F0;
                color: #000;
                padding: 10px 15px;
                border-radius: 15px;
                max-width: 70%;
                word-wrap: break-word;">
                {msg['content']}
            </div>
        </div>
        """, unsafe_allow_html=True)