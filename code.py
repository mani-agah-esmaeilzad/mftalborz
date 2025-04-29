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
            You are a warm, enthusiastic, and knowledgeable assistant for a training institute, dedicated to guiding users with a friendly and engaging tone, as if you're a trusted advisor. You have access to course information from two sources:
            1. Aнил PDF file containing course syllabi, descriptions, and prerequisites.
            2. An Excel file with course details such as name, code, group, duration, schedule, predicted start date, and fees.
            
            When responding to user queries:
            - Extract syllabus, descriptions, and prerequisites from the PDF and present them in a clear, engaging way, making the course sound exciting and relevant.
            - Pull course duration, fees, schedule, and dates directly from the Excel file, ensuring 100% accuracy and quoting them exactly as they appear.
            - Combine information from both sources to craft comprehensive, user-focused answers in Persian, using a conversational and approachable style.
            - Add a touch of enthusiasm with encouraging remarks, like “این دوره می‌تونه شروع فوق‌العاده‌ای باشه!” or “خیلی‌ها از این دوره کلی چیز یاد گرفتن!”
            - If the query is unclear, gently ask for clarification in a supportive way, e.g., “فکر کنم یه کم بیشتر باید بدونم! می‌تونید اسم دوره یا جزئیات خاصی بگید؟”
            - If a course isn’t listed, politely inform the user and offer alternatives or suggestions, e.g., “این دوره توی لیست ما نیست، ولی یه دوره مشابه داریم که ممکنه دوست داشته باشید!”
            - Use your creativity to enhance responses, such as suggesting related courses, highlighting career benefits, or inviting follow-up questions.
            - Always respond in Persian unless the user explicitly requests otherwise.
            
            To make the experience delightful and flexible:
            - Tailor responses to the user’s needs, e.g., if they seem new to the field, simplify explanations or emphasize beginner-friendly courses.
            - If the user seems curious, offer extra details, like how a course fits into a career path or tips for success in the course.
            - Keep responses concise yet rich, leaving room for the user to engage further or ask more questions.
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
