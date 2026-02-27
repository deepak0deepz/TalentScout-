# 👔 TalentScout - AI-Powered Hiring Assistant Chatbot

TalentScout is an intelligent chatbot built with Python and Streamlit that automates the initial candidate screening process for technical positions. It collects candidate information, parses tech stacks, and asks 5 fixed technical interview questions to evaluate candidates.

---

## 📋 Project Overview

TalentScout is designed to streamline the initial hiring process by:
- **Automating candidate screening** - Collects essential information without human intervention
- **Standardizing evaluation** - Asks the same 5 questions to every candidate for fair assessment
- **Maintaining context** - Uses session state to remember candidate details throughout the conversation
- **Providing professional experience** - Clean UI with proper error handling and validation

### Key Capabilities
- Multi-step conversation flow (Greeting → Info Collection → 5 Technical Questions → End)
- Input validation for email, phone, and required fields
- Fixed 5-question assessment (no random generation)
- JSON data export for each candidate
- Exit handling with professional closing

---

## 🚀 Installation Steps

### Prerequisites
- Python 3.8 or higher
- OpenAI API key (for initial setup, though questions are now fixed)

### Step-by-Step Installation

1. **Clone or download the project files**
   ```bash
   git clone <repository-url>
   cd talentscout
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**
   ```bash
   # Copy the example file
   cp .env.example .env
   
   # Edit .env and add your OpenAI API key
   OPENAI_API_KEY=your_actual_api_key_here
   ```

4. **Run the application**
   ```bash
   streamlit run app.py
   ```

5. **Open your browser**
   - The app will automatically open at `http://localhost:8501`
   - Or check the terminal for the exact URL

---

## 📖 Usage Instructions

### For Candidates

1. **Start the conversation** - The bot will greet you automatically with a welcome message

2. **Provide personal information** - Answer each question one by one:
   - Full Name
   - Email Address (validated)
   - Phone Number (validated, min 10 digits)
   - Years of Experience
   - Desired Position
   - Current Location

3. **Enter your tech stack** - Use comma-separated format:
   - Example: `Python, Django, PostgreSQL, Docker`
   - Example: `React, Node.js, MongoDB, AWS`

4. **Answer 5 technical questions** - Click A, B, C, or D buttons for each question
   - No feedback shown after answers (clean UI)
   - Questions are fixed and consistent for all candidates

5. **Complete the assessment** - After 5 questions, you'll see:
   - "Thanks for answering all 5 questions. We will let you know the result through your mail."

### Exit Commands
Type any of these to end the conversation immediately:
- `exit`, `quit`, `bye`, `goodbye`, `stop`, `end`

### Example Conversation Flow
```
🤖 Bot: Welcome to TalentScout! Please enter your Full Name:
👤 You: John Doe
🤖 Bot: Nice to meet you, John Doe! Please enter your Email Address:
👤 You: john@example.com
... (continues through all fields)
🤖 Bot: Please enter your Tech Stack:
👤 You: Python, Django
🤖 Bot: Here are your 5 technical questions...
🤖 Bot: Question 1 of 5: What is the primary purpose of Python in software development?
👤 You: [Clicks B]
... (continues for 5 questions)
🤖 Bot: Thanks for answering all 5 questions. We will let you know the result through your mail.
```

---

## 🎯 Prompt Design Explanation

### Initial Design (GPT-Generated Questions)
Originally, the system used OpenAI GPT-3.5-turbo to generate dynamic questions:
```python
prompt = f"""Generate 1 multiple choice question (MCQ) about {technology}.
Requirements:
1. Technology: {technology}
2. Difficulty: intermediate to advanced
3. Provide 4 distinct options (A, B, C, D)
4. Only ONE correct answer
5. Format exactly as follows:
QUESTION: [Specific question]
A) [Option A]
B) [Option B]
C) [Option C]
D) [Option D]
CORRECT: [A/B/C/D]"""
```

### Final Design (Fixed Questions)
Switched to **5 fixed questions** for consistency:
- Question templates use the primary technology from the candidate's tech stack
- Same questions for every candidate (fair evaluation)
- No API dependency for question generation
- Faster response time

### Question Templates
1. "What is the primary purpose of {tech} in software development?"
2. "Which of the following is a best practice when working with {tech}?"
3. "How does {tech} typically handle security concerns?"
4. "What is a common challenge when scaling applications with {tech}?"
5. "Which approach is recommended for debugging issues in {tech}?"

---

## 🏗️ Technical Decisions

### 1. **Streamlit for UI**
**Decision:** Used Streamlit instead of Flask/Django
**Rationale:** 
- Rapid prototyping and deployment
- Built-in session state management
- Automatic UI generation from Python code
- Ideal for data apps and chatbots

### 2. **Session State Management**
**Decision:** Used Streamlit's `session_state` instead of external database
**Rationale:**
- No database setup required
- Fast access to conversation history
- Simple for single-user deployment
- Data persists during session only

### 3. **Fixed vs Dynamic Questions**
**Decision:** Switched from GPT-generated to fixed 5 questions
**Rationale:**
- Consistency across all candidates
- No API costs for question generation
- Faster response times
- No risk of inappropriate questions
- Easier to validate and test

### 4. **JSON File Storage**
**Decision:** Save candidate data to JSON files instead of database
**Rationale:**
- Simple implementation
- Human-readable output
- Easy to export and analyze
- No database maintenance required

### 5. **Button-based MCQ Interface**
**Decision:** A/B/C/D buttons instead of text input for answers
**Rationale:**
- Faster user interaction
- No typing required
- Prevents invalid inputs
- Better mobile experience

### 6. **Light Theme Only**
**Decision:** Removed dark theme toggle, kept light theme
**Rationale:**
- Simpler codebase
- Professional appearance
- Better readability
- Consistent branding

---

## 🚧 Challenges Faced

### 1. **Duplicate Question Generation**
**Problem:** GPT was generating similar questions repeatedly
**Solution:** Switched to fixed question templates with technology substitution

### 2. **Question Numbering Issues**
**Problem:** Questions were skipping numbers (1, 2, 4, 5...)
**Solution:** Fixed indexing logic in `process_user_input()` function

### 3. **Feedback Display**
**Problem:** Users didn't want "Correct/Incorrect" messages shown
**Solution:** Removed feedback messages, now immediately shows next question

### 4. **State Management Complexity**
**Problem:** Conversation state machine had too many states
**Solution:** Simplified to essential states only, removed ASK_CONTINUE state

### 5. **API Dependency**
**Problem:** Application failed when OpenAI API was unavailable
**Solution:** Implemented fallback questions and reduced API dependency

### 6. **Progress Bar Errors**
**Problem:** `ValueError: 'ASK_CONTINUE' is not in list` when calculating progress
**Solution:** Added state validation and default values

---

## 🤖 Model Details

### OpenAI GPT-3.5-turbo (Initial Implementation)
- **Model:** gpt-3.5-turbo
- **Temperature:** 0.7 (balanced creativity)
- **Max Tokens:** 400
- **Use Case:** Dynamic question generation (deprecated in final version)

### Current Implementation (Fixed Questions)
- **No LLM required** for question generation
- **Static templates** with technology substitution
- **Primary tech stack** used for question personalization
- **Consistent evaluation** across all candidates

### Model Prompt Design (Historical)
```python
messages=[
    {"role": "system", "content": "You are a technical interviewer. Create specific multiple choice questions."},
    {"role": "user", "content": prompt}
]
```

### Fallback Strategy
When API fails or is unavailable:
- Uses pre-defined question templates
- Substitutes technology name into generic questions
- Ensures 5 questions always available

---

## 📁 Project Structure

```
talentscout/
├── app.py                 # Main Streamlit application
├── requirements.txt       # Python dependencies
├── .env.example          # Environment variables template
├── .env                  # Your API key (not committed)
├── .gitignore            # Git ignore rules
├── README.md             # This documentation
└── candidate_*.json      # Generated candidate data files
```

---

## 🔒 Security Notes

- API keys stored in `.env` file (not in version control)
- Candidate data saved locally as JSON files
- No external data transmission except OpenAI API (if used)
- `.env` added to `.gitignore` for protection

---

## 🐛 Troubleshooting

| Issue | Solution |
|-------|----------|
| "OpenAI API Key not configured!" | Create `.env` file and add your API key |
| "Error generating questions" | Check internet connection or API credits |
| Module not found errors | Run `pip install -r requirements.txt` |
| Same questions appearing | This is by design - 5 fixed questions for all |

---

## 📝 Output Format

Each candidate generates a JSON file:
```json
{
  "candidate_info": {
    "full_name": "John Doe",
    "email": "john@example.com",
    "phone": "+1 123-456-7890",
    "years_experience": "5",
    "desired_position": "Senior Python Developer",
    "current_location": "New York, USA",
    "tech_stack": ["Python", "Django"]
  },
  "conversation_history": [...],
  "timestamp": "2024-01-15T10:30:00"
}
```

---

## 🙏 Acknowledgments

- Built with [Streamlit](https://streamlit.io/)
- Icons from [Emoji](https://emojipedia.org/)

---

**Happy Hiring! 🎉**
#

