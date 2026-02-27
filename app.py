import streamlit as st
import os
import re
import json
import random
from datetime import datetime
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

st.set_page_config(
    page_title="TalentScout - Hiring Assistant",
    page_icon="👔",
    layout="centered",
    initial_sidebar_state="collapsed"
)

st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 0.5rem;
    }
    .sub-header {
        font-size: 1.1rem;
        color: #333333;
        text-align: center;
        margin-bottom: 2rem;
    }
    .chat-message {
        padding: 1rem;
        border-radius: 0.5rem;
        margin-bottom: 0.5rem;
        color: #000000;
    }
    .user-message {
        background-color: #e3f2fd;
        border-left: 4px solid #2196f3;
        color: #000000;
    }
    .bot-message {
        background-color: #f5f5f5;
        border-left: 4px solid #4caf50;
        color: #000000;
    }
    .info-box {
        background-color: #fff3e0;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #ff9800;
        margin-bottom: 1rem;
        color: #000000;
    }
    .success-box {
        background-color: #e8f5e9;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #4caf50;
        margin-bottom: 1rem;
        color: #000000;
    }
    .success-box h3 {
        color: #2e7d32;
    }
    .stTextInput > div > div > input {
        font-size: 16px;
        color: #000000;
        background-color: #ffffff;
        border: 1px solid #cccccc;
    }
    .option-button {
        font-size: 1.1rem;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

def init_session_state():
    if 'conversation_state' not in st.session_state:
        st.session_state.conversation_state = 'GREETING'
    if 'candidate_info' not in st.session_state:
        st.session_state.candidate_info = {
            'full_name': '',
            'email': '',
            'phone': '',
            'years_experience': '',
            'desired_position': '',
            'current_location': '',
            'tech_stack': []
        }
    if 'conversation_history' not in st.session_state:
        st.session_state.conversation_history = []
    if 'generated_questions' not in st.session_state:
        st.session_state.generated_questions = {}
    if 'current_questions_index' not in st.session_state:
        st.session_state.current_questions_index = 0
    if 'tech_stack_list' not in st.session_state:
        st.session_state.tech_stack_list = []
    if 'conversation_ended' not in st.session_state:
        st.session_state.conversation_ended = False
    if 'current_question' not in st.session_state:
        st.session_state.current_question = None
    if 'questions_queue' not in st.session_state:
        st.session_state.questions_queue = []
    if 'current_question_num' not in st.session_state:
        st.session_state.current_question_num = 0

EXIT_KEYWORDS = ['exit', 'quit', 'bye', 'goodbye', 'stop', 'end']

EMAIL_REGEX = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'

PHONE_REGEX = r'^[\d\s\-\+\(\)]+$'

def check_exit_keywords(user_input):
    """Check if user wants to exit"""
    return user_input.lower().strip() in EXIT_KEYWORDS

def validate_email(email):
    """Validate email format"""
    return re.match(EMAIL_REGEX, email) is not None

def validate_phone(phone):
    """Validate phone number"""
    return re.match(PHONE_REGEX, phone) is not None and len(re.sub(r'\D', '', phone)) >= 10

def add_to_history(role, message):
    """Add message to conversation history"""
    st.session_state.conversation_history.append({
        'role': role,
        'message': message,
        'timestamp': datetime.now().strftime("%H:%M:%S")
    })

def display_chat_history():
    """Display conversation history"""
    for msg in st.session_state.conversation_history:
        if msg['role'] == 'user':
            st.markdown(f"""
            <div class="chat-message user-message">
                <strong>👤 You:</strong> {msg['message']}
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div class="chat-message bot-message">
                <strong>🤖 TalentScout:</strong> {msg['message']}
            </div>
            """, unsafe_allow_html=True)

def get_fixed_questions(tech_stack):
    """Get 5 fixed questions - same for every iteration"""
 
    fixed_questions = [
        {
            'question_template': 'What is the primary purpose of {tech} in software development?',
            'options': {
                'A': 'To increase system complexity',
                'B': 'To improve application performance and scalability',
                'C': 'To reduce code readability',
                'D': 'To eliminate the need for testing'
            },
            'correct': 'B'
        },
        {
            'question_template': 'Which of the following is a best practice when working with {tech}?',
            'options': {
                'A': 'Ignore error handling',
                'B': 'Follow documentation and community guidelines',
                'C': 'Avoid version control',
                'D': 'Hardcode all configurations'
            },
            'correct': 'B'
        },
        {
            'question_template': 'How does {tech} typically handle security concerns?',
            'options': {
                'A': 'By ignoring security completely',
                'B': 'Through built-in security features and best practices',
                'C': 'By exposing all data publicly',
                'D': 'By disabling authentication'
            },
            'correct': 'B'
        },
        {
            'question_template': 'What is a common challenge when scaling applications with {tech}?',
            'options': {
                'A': 'It cannot be scaled',
                'B': 'Managing resources and optimizing performance',
                'C': 'It requires no configuration',
                'D': 'It works the same at any scale'
            },
            'correct': 'B'
        },
        {
            'question_template': 'Which approach is recommended for debugging issues in {tech}?',
            'options': {
                'A': 'Add random print statements',
                'B': 'Use proper logging and debugging tools',
                'C': 'Restart the server repeatedly',
                'D': 'Ignore errors in production'
            },
            'correct': 'B'
        }
    ]
    
    
    primary_tech = tech_stack[0] if tech_stack else "Technology"
    
    questions = []
    for i, template in enumerate(fixed_questions):
        questions.append({
            'question': template['question_template'].format(tech=primary_tech),
            'options': template['options'],
            'correct': template['correct'],
            'technology': primary_tech
        })
    
    return questions


def get_current_prompt():
    """Get the appropriate prompt based on current conversation state"""
    state = st.session_state.conversation_state
    
    prompts = {
        'GREETING': """👋 Welcome to **TalentScout** - Your AI Hiring Assistant!

I'm here to help you through the initial screening process for technical positions. 

**What I'll do:**
- Collect your basic information
- Ask about your technical skills
- Ask 5 technical questions

**To exit anytime, type:** exit, quit, or bye

Let's get started! 

**Please enter your Full Name:**""",
        
        'COLLECT_NAME': "Please enter your **Full Name**:",
        
        'COLLECT_EMAIL': "Please enter your **Email Address**:",
        
        'COLLECT_PHONE': "Please enter your **Phone Number** (with country code if applicable):",
        
        'COLLECT_EXPERIENCE': "How many **Years of Experience** do you have in the tech industry?",
        
        'COLLECT_POSITION': "What is your **Desired Position** or job title you're applying for?",
        
        'COLLECT_LOCATION': "What is your **Current Location** (City, Country)?",
        
        'COLLECT_TECH_STACK': """Please enter your **Tech Stack** (comma-separated list of technologies).

**Examples:**
- Python, Django, PostgreSQL, Docker
- React, Node.js, MongoDB, AWS
- Java, Spring Boot, MySQL, Kubernetes

**Your Tech Stack:**""",
        
        'GENERATE_QUESTIONS': "Here are your 5 technical questions...",
        
        'END': "Thank you for your time! Our recruitment team will review your profile and contact you shortly."
    }
    
    return prompts.get(state, "How can I help you today?")

def process_user_input(user_input):
    """Process user input based on current conversation state"""
    user_input = user_input.strip()
    
    
    if check_exit_keywords(user_input):
        st.session_state.conversation_state = 'END'
        name = st.session_state.candidate_info.get('full_name', 'there')
        farewell = f"Thank you for your time, {name}. Our recruitment team will contact you shortly if needed. Goodbye! 👋"
        add_to_history('bot', farewell)
        st.session_state.conversation_ended = True
        return
    
    state = st.session_state.conversation_state
    
    if state == 'GREETING':
        if len(user_input) < 2:
            add_to_history('bot', "Please enter a valid name (at least 2 characters).")
            return
        st.session_state.candidate_info['full_name'] = user_input
        st.session_state.conversation_state = 'COLLECT_EMAIL'
        add_to_history('bot', f"Nice to meet you, {user_input}! {get_current_prompt()}")
        return
        
    elif state == 'COLLECT_NAME':
        if len(user_input) < 2:
            add_to_history('bot', "Please enter a valid name (at least 2 characters).")
            return
        st.session_state.candidate_info['full_name'] = user_input
        st.session_state.conversation_state = 'COLLECT_EMAIL'
        add_to_history('bot', f"Nice to meet you, {user_input}! {get_current_prompt()}")
        
    elif state == 'COLLECT_EMAIL':
        if not validate_email(user_input):
            add_to_history('bot', "Please enter a valid email address (e.g., name@example.com).")
            return
        st.session_state.candidate_info['email'] = user_input
        st.session_state.conversation_state = 'COLLECT_PHONE'
        add_to_history('bot', get_current_prompt())
        
    elif state == 'COLLECT_PHONE':
        if not validate_phone(user_input):
            add_to_history('bot', "Please enter a valid phone number with at least 10 digits.")
            return
        st.session_state.candidate_info['phone'] = user_input
        st.session_state.conversation_state = 'COLLECT_EXPERIENCE'
        add_to_history('bot', get_current_prompt())
        
    elif state == 'COLLECT_EXPERIENCE':
        try:
            exp = float(user_input)
            if exp < 0 or exp > 50:
                add_to_history('bot', "Please enter a valid number of years (0-50).")
                return
        except ValueError:
            add_to_history('bot', "Please enter a valid number (e.g., 3, 5.5, etc.).")
            return
        st.session_state.candidate_info['years_experience'] = user_input
        st.session_state.conversation_state = 'COLLECT_POSITION'
        add_to_history('bot', get_current_prompt())
        
    elif state == 'COLLECT_POSITION':
        if len(user_input) < 2:
            add_to_history('bot', "Please enter a valid position title.")
            return
        st.session_state.candidate_info['desired_position'] = user_input
        st.session_state.conversation_state = 'COLLECT_LOCATION'
        add_to_history('bot', get_current_prompt())
        
    elif state == 'COLLECT_LOCATION':
        if len(user_input) < 2:
            add_to_history('bot', "Please enter a valid location.")
            return
        st.session_state.candidate_info['current_location'] = user_input
        st.session_state.conversation_state = 'COLLECT_TECH_STACK'
        add_to_history('bot', get_current_prompt())
        
    elif state == 'COLLECT_TECH_STACK':
        tech_stack = [tech.strip() for tech in user_input.split(',') if tech.strip()]
        if len(tech_stack) == 0:
            add_to_history('bot', "Please enter at least one technology.")
            return
        
        st.session_state.candidate_info['tech_stack'] = tech_stack
        st.session_state.tech_stack_list = tech_stack
        st.session_state.questions_queue = get_fixed_questions(tech_stack)
        st.session_state.current_question_num = 0
        
        st.session_state.conversation_state = 'GENERATE_QUESTIONS'
        add_to_history('bot', f"Great! I've recorded your tech stack: {', '.join(tech_stack)}")
        if st.session_state.questions_queue:
            q = st.session_state.questions_queue[0]
            st.session_state.current_question = q
            question_msg = f"**Question 1 of 5:**\n\n{q['question']}"
            add_to_history('bot', question_msg)
        
    elif state == 'GENERATE_QUESTIONS':
        valid_options = ['A', 'B', 'C', 'D']
        user_answer = user_input.upper().strip()
        
        if user_answer not in valid_options:
            add_to_history('bot', "Please select a valid option: A, B, C, or D.")
            return
        st.session_state.current_question_num += 1

        if st.session_state.current_question_num >= 5:
            st.session_state.conversation_state = 'END'
            name = st.session_state.candidate_info.get('full_name', 'there')
            email = st.session_state.candidate_info.get('email', 'your email')
            farewell = f"🎉 Thank you for your time, {name}! \n\nThanks for answering all 5 questions. We will let you know the result through your mail at {email}.\n\n🍀 Good luck with your application!"
            add_to_history('bot', farewell)
            st.session_state.conversation_ended = True
            save_candidate_info()
        else:
            q = st.session_state.questions_queue[st.session_state.current_question_num]
            st.session_state.current_question = q
            question_num = st.session_state.current_question_num + 1
            question_msg = f"**Question {question_num} of 5:**\n\n{q['question']}"
            add_to_history('bot', question_msg)
    
    else:
        add_to_history('bot', "I'm here to assist with the hiring process. Could you please provide the requested details?")

def save_candidate_info():
    """Save candidate information to a JSON file"""
    try:
        filename = f"candidate_{st.session_state.candidate_info['full_name'].replace(' ', '_').lower()}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        data = {
            'candidate_info': st.session_state.candidate_info,
            'conversation_history': st.session_state.conversation_history,
            'generated_questions': st.session_state.generated_questions,
            'timestamp': datetime.now().isoformat()
        }
        
        with open(filename, 'w') as f:
            json.dump(data, f, indent=2)
        
        st.success(f"✅ Candidate information saved to {filename}")
    except Exception as e:
        st.error(f"Error saving candidate info: {str(e)}")

def display_candidate_summary():
    """Display a summary of collected candidate information"""
    if st.session_state.candidate_info['full_name']:
        st.sidebar.markdown("---")
        st.sidebar.subheader("📋 Candidate Summary")
        
        info = st.session_state.candidate_info
        st.sidebar.markdown(f"""
        **Name:** {info['full_name'] or 'Not provided'}  
        **Email:** {info['email'] or 'Not provided'}  
        **Phone:** {info['phone'] or 'Not provided'}  
        **Experience:** {info['years_experience'] or 'Not provided'} years  
        **Position:** {info['desired_position'] or 'Not provided'}  
        **Location:** {info['current_location'] or 'Not provided'}  
        **Tech Stack:** {', '.join(info['tech_stack']) if info['tech_stack'] else 'Not provided'}
        """)

        states = ['GREETING', 'COLLECT_NAME', 'COLLECT_EMAIL', 'COLLECT_PHONE', 
                 'COLLECT_EXPERIENCE', 'COLLECT_POSITION', 'COLLECT_LOCATION', 
                 'COLLECT_TECH_STACK', 'GENERATE_QUESTIONS', 'END']
        current_idx = states.index(st.session_state.conversation_state) if st.session_state.conversation_state in states else 8
        progress = (current_idx / (len(states) - 1)) * 100
        st.sidebar.progress(int(progress), text=f"Progress: {int(progress)}%")

def reset_conversation():
    """Reset the conversation to start over"""
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    init_session_state()
    st.rerun()

def process_answer(answer):
    """Process MCQ answer from button click"""
    add_to_history('user', answer)
    process_user_input(answer)
    st.rerun()

def main():
    init_session_state()
    
    st.markdown('<h1 class="main-header">👔 TalentScout</h1>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">AI-Powered Hiring Assistant</p>', unsafe_allow_html=True)

    if not os.getenv("OPENAI_API_KEY") or os.getenv("OPENAI_API_KEY") == "your_openai_api_key_here":
        st.error("⚠️ **OpenAI API Key not configured!**")
        st.info("""
        Please set up your API key:
        1. Copy `.env.example` to `.env`
        2. Add your OpenAI API key to `.env`
        3. Restart the application
        
        Get your API key from: https://platform.openai.com/api-keys
        """)
        return
    
    with st.sidebar:
        st.title("🎯 TalentScout")
        st.markdown("---")
        
        if st.button("🔄 Start New Conversation", use_container_width=True):
            reset_conversation()
        
        st.markdown("---")
        st.markdown("""
        **Quick Guide:**
        - Answer questions one by one
        - Type **exit**, **quit**, or **bye** to end anytime
        - Provide accurate information
        - Tech stack should be comma-separated
        
        **Current Status:**  
        """)
        
        status_color = "🟢" if not st.session_state.conversation_ended else "🔴"
        st.markdown(f"{status_color} **{st.session_state.conversation_state.replace('_', ' ')}**")
        
        display_candidate_summary()
    
  
    chat_container = st.container()
    
    with chat_container:
       
        display_chat_history()
        
       
        if not st.session_state.conversation_ended:
            
            last_bot_msg = None
            for msg in reversed(st.session_state.conversation_history):
                if msg['role'] == 'bot':
                    last_bot_msg = msg['message']
                    break
            
            if not last_bot_msg:
               
                initial_msg = get_current_prompt()
                st.markdown(f"""
                <div class="chat-message bot-message">
                    <strong>🤖 TalentScout:</strong> {initial_msg}
                </div>
                """, unsafe_allow_html=True)
            
           
            if st.session_state.conversation_state == 'GENERATE_QUESTIONS' and st.session_state.current_question:
                q = st.session_state.current_question
                st.markdown(f"""
                <div class="chat-message bot-message" style="margin-top: 0.5rem;">
                    <strong>Options:</strong><br>
                    <span style="font-size: 1.1rem;">
                    <b>A)</b> {q['options']['A']}<br>
                    <b>B)</b> {q['options']['B']}<br>
                    <b>C)</b> {q['options']['C']}<br>
                    <b>D)</b> {q['options']['D']}
                    </span>
                </div>
                """, unsafe_allow_html=True)
    
   
    if not st.session_state.conversation_ended:
        st.markdown("---")
        
       
        if st.session_state.conversation_state == 'GENERATE_QUESTIONS':
           
            st.markdown("**Select your answer:**")
            cols = st.columns(4)
            with cols[0]:
                if st.button("A", use_container_width=True, key="btn_A"):
                    process_answer("A")
            with cols[1]:
                if st.button("B", use_container_width=True, key="btn_B"):
                    process_answer("B")
            with cols[2]:
                if st.button("C", use_container_width=True, key="btn_C"):
                    process_answer("C")
            with cols[3]:
                if st.button("D", use_container_width=True, key="btn_D"):
                    process_answer("D")
        else:
           
            with st.form(key='chat_form', clear_on_submit=True):
                user_input = st.text_input(
                    "Your response:",
                    placeholder="Type your answer here...",
                    key="user_input",
                    label_visibility="collapsed"
                )
                submit_button = st.form_submit_button("Send ➤", use_container_width=True)
            
            if submit_button and user_input:
               
                add_to_history('user', user_input)
                
               
                process_user_input(user_input)
                
                
                st.rerun()

    else:
       
        st.markdown("---")
        st.markdown("""
        <div class="success-box">
            <h3>✅ Conversation Completed</h3>
            <p>Thank you for using TalentScout! Click "Start New Conversation" in the sidebar to begin with a new candidate.</p>
        </div>
        """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
