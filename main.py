import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import requests, hmac, hashlib, time, threading, sys

sys.stdout.reconfigure(encoding='utf-8')

API_KEY = 'mx0vgljv46jp8aUrRk'
SECRET_KEY = '0de3636c9ccb438f841cb7ee6754de09'
TELEGRAM_TOKEN = '8985526610:AAHqS5dyfrL9PuAi8uDvDPImCn1iFlG8p7Y'
TELEGRAM_CHAT_ID = '7184042984'

bot = telebot.TeleBot(TELEGRAM_TOKEN)
scanner_active = False

session_sniper = requests.Session()
session_sniper.headers.update({
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    'Connection': 'keep-alive'
})

def get_main_keyboard():
    markup = InlineKeyboardMarkup()
    markup.row_width = 2
    markup.add(
        InlineKeyboardButton("📊 فحص الرصيد السحابي", callback_data="check_balance"),
        InlineKeyboardButton("🚀 اقتناص PEPE فوراً", callback_data="buy_pepe")
    )
    markup.add(
        InlineKeyboardButton("🌪️ تشغيل الرادار الأوروبي", callback_data="start_scan"),
        InlineKeyboardButton("🔴 إيقاف الرادار الأوروبي", callback_data="stop_scan")
    )
    return markup

def global_market_scanner():
    global scanner_active
    timeframes = ['1m', '5m']
    bot.send_message(TELEGRAM_CHAT_ID, "🌪️ *تم إطلاق الرادار السحابي المطور من قلب أوروبا!* جاري مسح أعلى 50 عملة سيولة بالثانية...")
    
    while scanner_active:
        try:
            ticker_url = "https://mexc.com"
            all_data = session_sniper.get(ticker_url, timeout=10).json()
            
            active_pairs = sorted(
                [t for t in all_data if t['symbol'].endswith('USDT')],
                key=lambda x: float(x.get('quoteVolume', 0)),
                reverse=True
            )[:50]
            
            symbols_to_scan = [t['symbol'] for t in active_pairs]
            
            for symbol in symbols_to_scan:
                if not scanner_active: break
                for tf in timeframes:
                    if not scanner_active: break
                    url = f"https://mexc.com{symbol}&interval={tf}&limit=2"
                    klines = session_sniper.get(url, timeout=5).json()
                    
                    if len(klines) >= 2:
                        open_p = float(klines[-1]['open'] if isinstance(klines[-1], dict) else klines[-1])
                        close_p = float(klines[-1]['close'] if isinstance(klines[-1], dict) else klines[-1])
                        vol = float(klines[-1]['volume'] if isinstance(klines[-1], dict) else klines[-1])
                        
                        if close_p > open_p:
                            pump = ((close_p - open_p) / open_p) * 100
                            if pump >= 0.02:
                                tf_name = {"1m": "⏱️ شمعة دقيقة", "5m": "📊 شمعة 5 دقائق"}[tf]
                                alert_msg = (
                                    f"🚨 *اكتشاف شمعة خضراء سحابية!* \n"
                                    f"📦 العملة المكتشفة: #{symbol.replace('USDT', '')}\n"
                                    f"⏱️ الإطار الزمني: `{tf_name}`\n"
                                    f"📈 نسبة الصعود الخاطف: `+{pump:.3f}%` \n"
                                    f"🌊 سيولة السيرفر: `{vol:.0f}`"
                                )
                                bot.send_message(TELEGRAM_CHAT_ID, alert_msg, reply_markup=get_main_keyboard(), parse_mode="Markdown")
                                time.sleep(1)
            time.sleep(10)
        except Exception: time.sleep(5)

@bot.callback_query_handler(func=lambda call: True)
def handle_query(call):
    global scanner_active
    ts = int(time.time() * 1000)
    query = f"timestamp={ts}"
    signature = hmac.new(SECRET_KEY.encode('utf-8'), query.encode('utf-8'), hashlib.sha256).hexdigest()
    
    if call.data == "check_balance":
        def run_balance_check():
            try:
                url = f"https://mexc.com?{query}&signature={signature}"
                r = requests.get(url, headers={'X-MEXC-APIKEY': API_KEY}, timeout=5).json()
                usdt = next((b['free'] for b in r['balances'] if b['asset'] == 'USDT'), '0.00')
                pepe = next((b['free'] for b in r['balances'] if b['asset'] == 'PEPE'), '0.00')
                bot.send_message(TELEGRAM_CHAT_ID, f"📊 *تقرير السيرفر الأوروبي المباشر:*\n💰 المتوفر: `{usdt}` USDT\n🐸 الرصيد: `{pepe}` PEPE", reply_markup=get_main_keyboard(), parse_mode="Markdown")
            except Exception:
                bot.send_message(TELEGRAM_CHAT_ID, "⚠️ عائق اتصال سحابي مؤقت. أعد الضغط لتمرير الحزمة.", reply_markup=get_main_keyboard(), parse_mode="Markdown")
        threading.Thread(target=run_balance_check).start()
            
    elif call.data == "buy_pepe":
        def run_buy():
            try:
                url = f"https://mexc.com?{query}&signature={signature}"
                r = requests.get(url, headers={'X-MEXC-APIKEY': API_KEY}, timeout=5).json()
                usdt = next((float(b['free']) for b in r['balances'] if b['asset'] == 'USDT'), 0.0)
                if usdt >= 4.0:
                    amt = usdt - 0.02
                    buy_q = f"symbol=PEPEUSDT&side=BUY&type=MARKET&quoteOrderQty={amt}&timestamp={ts}"
                    buy_sig = hmac.new(SECRET_KEY.encode('utf-8'), buy_q.encode('utf-8'), hashlib.sha256).hexdigest()
                    res = requests.post(f"https://mexc.com?{buy_q}&signature={buy_sig}", headers={'X-MEXC-APIKEY': API_KEY}).json()
                    if 'orderId' in res:
                        bot.send_message(TELEGRAM_CHAT_ID, f"🎉 *تم النصر واقتناص الهدف السحابي!* شراء PEPE بنجاح من سيرفر ألمانيا برقم: `{res['orderId']}`", reply_markup=get_main_keyboard(), parse_mode="Markdown")
                else:
                    bot.send_message(TELEGRAM_CHAT_ID, f"⚠️ ذخيرة غير كافية بالسيرفر: `{usdt}` USDT", reply_markup=get_main_keyboard(), parse_mode="Markdown")
            except Exception: pass
        threading.Thread(target=run_buy).start()
            
    elif call.data == "start_scan":
        if not scanner_active:
            scanner_active = True
            threading.Thread(target=global_market_scanner, daemon=True).start()
            bot.send_message(TELEGRAM_CHAT_ID, "✅ *تم تنشيط رادار المسح السحابي الأوروبي!*", reply_markup=get_main_keyboard(), parse_mode="Markdown")
    elif call.data == "stop_scan":
        scanner_active = False
        bot.send_message(TELEGRAM_CHAT_ID, "🔴 تم إيقاف رادار السحاب الصامت.", parse_mode="Markdown")

@bot.message_handler(commands=['start', 'menu'])
def send_welcome(message):
    bot.send_message(TELEGRAM_CHAT_ID, "👑 *واجهة التحكم السحابية الأوروبية الحرة لـ MEXC!*", reply_markup=get_main_keyboard(), parse_mode="Markdown")

if __name__ == '__main__':
    bot.infinity_polling(timeout=20)
