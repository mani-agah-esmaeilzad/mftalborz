import telebot
from langchain_openai import ChatOpenAI
from pypdf import PdfReader
import pandas as pd


bot = telebot.TeleBot('7770938110:AAEkJLzKnAXJlbJA05Zc_bT7t0KmRzQLqac')
OPENAI_API_KEY = 'aa-xgnSCrHb2Y2cyLovy8rP3Kun40rnznnyogxBCWbEyjS20w5s'
OPENAI_BASE_URL = 'https://api.avalai.ir/v1'
OPENAI_MODEL = 'gpt-4o-mini'


try:
    reader = PdfReader('test.pdf')
    pdf_text = ''
    for i in range(len(reader.pages)):
        pdf_text += reader.pages[i].extract_text() or ''
except Exception as e:
    print(f'Error reading PDF: {e}')
    pdf_text = ''

try:
    excel_data = pd.read_excel('Book1.xlsx')
    excel_text = excel_data.to_string(index=False)
except Exception as e:
    print(f'Error reading Excel: {e}')
    excel_text = ''

combined_context = f"""
**PDF Content (Syllabus, Descriptions, Prerequisites):**
{pdf_text}

**Excel Data (Course Details, Duration, Fees, Schedule, Dates):**
{excel_text}
"""

@bot.message_handler(content_types=['text'])
def handle_text(message):
    messages = [
        {
            "role": "system",
            "content": """
                You are an assistant for a training institute. You have access to course information from two sources:
                1. A PDF file containing course syllabi, descriptions, and prerequisites.
                2. An Excel file containing course details such as name, code, group, duration, schedule, predicted start date, and fees.
                
                When responding to user queries:
                - Extract syllabus, descriptions, and prerequisites from the PDF content.
                - Extract course duration, fees, schedule, and dates exactly as they appear in the Excel data.
                - Ensure all details from the Excel file (e.g., fees, duration, dates) are accurate and match the Excel data precisely.
                - Provide clear, concise, and accurate answers in Persian, combining information from both sources as relevant.
                - If the query is unclear or data is missing, state so politely and suggest rephrasing the question.
                - If the query is about a course not listed, inform the user that the course is not available in the provided data.
                """
        },
        {
            "role": "user",
            "content": f"""
            با توجه به محتوای زیر پاسخ بده:
            
            {combined_context}
            
            سوال من: {message.text}
            """
        }
    ]

    try:
        llm = ChatOpenAI(
            model=OPENAI_MODEL,
            base_url=OPENAI_BASE_URL,
            api_key=OPENAI_API_KEY
        )
        response = llm.invoke(messages)
        bot.reply_to(message, response.content)
    except Exception as e:
        bot.reply_to(message, f'خطا در پردازش درخواست: {str(e)}')
        print(f'خطا در ارتباط با ChatOpenAI: {e}')

try:
    bot.polling(none_stop=True)
except Exception as e:
    print(f'خطا در اجرای ربات: {e}')