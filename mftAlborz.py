#pip install -U openai
#pip install -U langchain
#pip install -U langchain_openai
#pip install -U pypdf
#pip install -U pyTelegramBotAPI

from telebot import TeleBot
from langchain_openai import ChatOpenAI
from pypdf import PdfReader

reader = PdfReader('test.pdf')
txt = ''
for i in range(len(reader.pages)):
    txt += reader.pages[i].extract_text()

OPENAI_API_KEY = 'aa-xgnSCrHb2Y2cyLovy8rP3Kun40rnznnyogxBCWbEyjS20w5s'
OPENAI_BASE_URL = 'https://api.avalai.ir/v1'
OPENAI_MODEL = 'gpt-4o-mini'

bot = telebot.TeleBot('7770938110:AAEkJLzKnAXJlbJA05Zc_bT7t0KmRzQLqac')

@bot.message_handler(content_types=['text'])
def handle_text(message):
    messages = [
        {"role": "system", "content": "تو دستیار هوش مصنوعی هستی در مجتمع فنی تهران نمایندگی البرز و فقط جواب پاسخ ها رو طبق اون متن که بهت دادم جواب میدی"},
        {"role": "user", "content": f"با توجه به محتوای زیر پاسخ بده:\n\n{txt}\n\nسوال من: {message.text}"} ]
        

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