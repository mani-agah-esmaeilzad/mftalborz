import telebot
from langchain_openai import ChatOpenAI
from pypdf import PdfReader
import pandas as pd
import os # Import os for file existence checks

# --- Bot Setup ---
bot = telebot.TeleBot('7813195147:AAFRKtc6Av5u0gzJ6Czc5t3IVm-eyfCA1ic')

# --- OpenAI Setup ---
# Make sure you replace these with your actual keys and URLs if they are different
# Using environment variables is recommended for production
OPENAI_API_KEY = 'aa-xgnSCrHb2Y2cyLovy8rP3Kun40rnznnyogxBCWbEyjS20w5s'
OPENAI_BASE_URL = 'https://api.avalai.ir/v1' # Your custom base URL
OPENAI_MODEL = 'gpt-4o-mini' # Or your preferred model

# --- Data Loading ---
# Check if files exist before attempting to read
pdf_file_path = 'test.pdf'
excel_file_path = 'Book1.xlsx'

pdf_text = ''
if os.path.exists(pdf_file_path):
    try:
        reader = PdfReader(pdf_file_path)
        pdf_text = ''
        for i in range(len(reader.pages)):
            pdf_text += reader.pages[i].extract_text() or ''
        print("Successfully read PDF.")
    except Exception as e:
        print(f'Error reading PDF {pdf_file_path}: {e}')
else:
    print(f"PDF file not found: {pdf_file_path}")

excel_text = ''
if os.path.exists(excel_file_path):
    try:
        excel_data = pd.read_excel(excel_file_path)
        excel_text = excel_data.to_string(index=False)
        print("Successfully read Excel.")
    except Exception as e:
        print(f'Error reading Excel {excel_file_path}: {e}')
else:
    print(f"Excel file not found: {excel_file_path}")


# --- Combine Context (This context will be included in each LLM call for now) ---
# Note: Including large context repeatedly can be inefficient and costly.
# For better performance/cost, consider other strategies if context is huge.
combined_context = f"""
**PDF Content (Syllabus, Descriptions, Prerequisites):**
{pdf_text}

**Excel Data (Course Details, Duration, Fees, Schedule, Dates):**
{excel_text}
"""

# --- Conversation History Storage ---
# Dictionary to store message history for each user.
# Key: user_id (integer)
# Value: List of message dictionaries [{"role": ..., "content": ...}, ...]
user_conversations = {}

# --- Define the System Message ---
# This message sets the persona and instructions for the AI.
# It should be the first message in every conversation history.
system_message_content = """
You are a warm, enthusiastic, and knowledgeable assistant for a training institute, dedicated to guiding users with a friendly and engaging tone, as if you're a trusted advisor. You have access to course information from two sources:
1. PDF content containing course syllabi, descriptions, and prerequisites.
2. Excel data with course details such as name, code, group, duration, schedule, predicted start date, and fees.

When responding to user queries:
- Extract syllabus, descriptions, and prerequisites from the provided PDF content and present them in a clear, engaging way, making the course sound exciting and relevant.
- Pull course duration, fees, schedule, and dates directly from the provided Excel data, ensuring 100% accuracy and quoting them exactly as they appear.
- Combine information from both sources to craft comprehensive, user-focused answers in Persian, using a conversational and approachable style.
- Add a touch of enthusiasm with encouraging remarks, like “این دوره می‌تونه شروع فوق‌العاده‌ای باشه!” or “خیلی‌ها از این دوره کلی چیز یاد گرفتن!”
- If the query is unclear, gently ask for clarification in a supportive way, e.g., “فکر کنم یه کم بیشتر باید بدونم! می‌تونید اسم دوره یا جزئیات خاصی بگید؟”
- If a course isn’t listed in the provided data, politely inform the user and offer alternatives or suggestions, e.g., “این دوره توی لیست ما نیست، ولی یه دوره مشابه داریم که ممکمه دوست داشته باشید!”
- Use your creativity to enhance responses, such as suggesting related courses, highlighting career benefits, or inviting follow-up questions.
- Always respond in Persian unless the user explicitly requests otherwise.

To make the experience delightful and flexible:
- Tailor responses to the user’s needs, e.g., if they seem new to the field, simplify explanations or emphasize beginner-friendly courses.
- If the user seems curious, offer extra details, like how a course fits into a career path or tips for success in the course.
- Keep responses concise yet rich, leaving room for the user to engage further or ask more questions.

The user will provide the PDF and Excel content along with their query in the user message. Use this provided data to answer their question based on the instructions above.
"""
system_message = {"role": "system", "content": system_message_content}


# --- Message Handler ---
@bot.message_handler(content_types=['text'])
def handle_text(message):
    user_id = message.from_user.id
    user_query = message.text

    # Initialize conversation history for the user if it doesn't exist
    if user_id not in user_conversations:
        # Start with the system message
        user_conversations[user_id] = [system_message.copy()]
        print(f"New conversation started for user ID: {user_id}")

    # --- Construct the full message list to send to the LLM for this turn ---
    # This includes the history + the *current* user message with context
    # We prepend the combined context to the user's *current* query
    messages_for_llm = user_conversations[user_id].copy() # Start with 
