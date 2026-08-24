from flask import Flask, request, redirect, jsonify
import datetime
import hashlib
import random
import re

app = Flask(__name__)

# ============================
# GIF 动图配置（4张已替换）
# ============================
GIF_KEYS = {
    'gif1': 'img_v3_0214s_98a77b14-3eeb-4e8f-8b16-80009a371dbg',
    'gif2': 'img_v3_0214s_5968e7f1-a404-48c9-8378-634a9b8a89fg',
    'gif3': 'img_v3_0214s_db820d4e-d8b4-4593-93fb-8585681dd76g',
    'gif4': 'img_v3_0214s_6414d781-2dad-4a3f-8ce1-6b39d705e77g',
    'gif5': 'img_v3_0214s_6f75ddc8-5d18-40cb-99e1-b5c912333abg',
}

# 默认图标（翻滚小猫）
DEFAULT_IMAGE_KEY = 'img_v3_02gp_bc939d82-ad8d-4dd0-856d-c26e2d161b9g'

# ============================
# 自定义链接映射
# ============================
CUSTOM_LINKS = {
    'd1': ('https://www.douyin.com/video/7669403253999182218', '🔥 点击查看本月绩效'),
    'd2': ('https://www.douyin.com/video/7462354119198608700', '🎵 点击此处扣除郑雨阳本月全部绩效'),
    'd3': ('https://www.douyin.com/video/7483284135268732199', '📱 点击此处带你旅行'),
}

# ============================
# 塔罗牌配置
# ============================
TAROT_CARDS = [
    '愚者', '魔术师', '女祭司', '皇后', '皇帝', '教皇', '恋人', '战车',
    '力量', '隐者', '命运之轮', '正义', '倒吊人', '死神', '节制', '恶魔',
    '塔', '星星', '月亮', '太阳', '审判', '世界'
]

# ============================
# 一言金句库
# ============================
HITOKOTO_SENTENCES = [
    '星光不问赶路人，时光不负有心人。',
    '生活原本沉闷，但跑起来就有风。',
    '凡是过往，皆为序章。',
    '万物皆有裂痕，那是光照进来的地方。',
    '愿你出走半生，归来仍是少年。',
    '山高路远，看世界，也找自己。',
    '慢慢来，谁还没有一个努力的过程。',
    '保持热爱，奔赴山海。',
    '日子常新，未来不远。',
    '今天也是元气满满的一天！',
    '最好的时光，是你在我身边。',
    '心若向阳，无畏悲伤。',
]


# ============================
# 时区工具：转换为北京时间 (UTC+8)
# ============================
def beijing_now():
    return datetime.datetime.utcnow() + datetime.timedelta(hours=8)


def beijing_date():
    return (datetime.datetime.utcnow() + datetime.timedelta(hours=8)).date()


# ============================
# 飞书回调接口 - 核心
# ============================
@app.route('/api/handler', methods=['POST'])
def lark_api_handler():
    data = request.get_json() or {}
    event = data.get('event', {})
    url = event.get('context', {}).get('url', '')
    
    path = ''
    if url:
        match = re.search(r'caishuo\.work(/.*)?', url)
        if match:
            path = match.group(1) or '/'
    
    # 处理 url_verification
    if data.get('type') == 'url_verification':
        return jsonify({'challenge': data.get('challenge', '')})
    
    # 处理链接预览
    if data.get('header', {}).get('event_type') == 'url.preview.get':
        inline_title = 'caishuo.work'
        image_key = ''
        
        if path.startswith('/time'):
            now = beijing_now()
            week_days = ['周一', '周二', '周三', '周四', '周五', '周六', '周日']
            week_day = week_days[now.weekday()]
            inline_title = f"🕐 {now.strftime('%H:%M')} | {week_day}"
            image_key = DEFAULT_IMAGE_KEY
        
        elif path.startswith('/offwork'):
            now = beijing_now()
            today_18 = now.replace(hour=18, minute=0, second=0, microsecond=0)
            if now >= today_18:
                tomorrow_18 = today_18 + datetime.timedelta(days=1)
                delta = tomorrow_18 - now
                hours = delta.seconds // 3600
                minutes = (delta.seconds % 3600) // 60
                inline_title = f"🎉 已下班！距明天18:00还有 {hours}小时{minutes}分"
            else:
                delta = today_18 - now
                hours = delta.seconds // 3600
                minutes = (delta.seconds % 3600) // 60
                inline_title = f"⏳ 距下班还有 {hours}小时{minutes}分"
            image_key = DEFAULT_IMAGE_KEY
        
        elif path.startswith('/tarot'):
            user_id = event.get('operator', {}).get('open_id', 'default')
            today = beijing_date().strftime('%Y-%m-%d')
            seed = hashlib.sha256(f'{user_id}-{today}'.encode()).hexdigest()
            idx = int(seed, 16) % len(TAROT_CARDS)
            card = TAROT_CARDS[idx]
            inline_title = f"🔮 今日塔罗：{card}"
            image_key = DEFAULT_IMAGE_KEY
        
        elif path.startswith('/hitokoto'):
            today = beijing_date().strftime('%Y-%m-%d')
            idx = int(hashlib.sha256(today.encode()).hexdigest(), 16) % len(HITOKOTO_SENTENCES)
            inline_title = f"💬 {HITOKOTO_SENTENCES[idx]}"
            image_key = DEFAULT_IMAGE_KEY
        
        elif path.startswith('/hello'):
            hour = beijing_now().hour
            if 5 <= hour < 12:
                greeting = '早安'
            elif 12 <= hour < 14:
                greeting = '午安'
            elif 14 <= hour < 18:
                greeting = '下午好'
            elif 18 <= hour < 22:
                greeting = '晚上好'
            else:
                greeting = '夜深了'
            inline_title = f"👋 {greeting}，蔡硕"
            image_key = DEFAULT_IMAGE_KEY
        
        elif path.startswith('/gif1'):
            inline_title = ' '
            image_key = GIF_KEYS.get('gif1', '')
        
        elif path.startswith('/gif2'):
            inline_title = ' '
            image_key = GIF_KEYS.get('gif2', '')
        
        elif path.startswith('/gif3'):
            inline_title = ' '
            image_key = GIF_KEYS.get('gif3', '')
        
        elif path.startswith('/gif4'):
            inline_title = ' '
            image_key = GIF_KEYS.get('gif4', '')
        
        elif path.startswith('/d') and len(path) >= 3 and path[2].isdigit():
            code = path[1:3]
            if code in CUSTOM_LINKS:
                inline_title = CUSTOM_LINKS[code][1]
                image_key = DEFAULT_IMAGE_KEY
        
        elif path.startswith('/say/'):
            text = path[5:]
            try:
                from urllib.parse import unquote
                text = unquote(text)
            except:
                pass
            inline_title = text[:30] if text else '自定义签名'
            image_key = DEFAULT_IMAGE_KEY
        
        elif path == '/' or path == '':
            inline_title = '✨ 蔡硕的动态签名'
            image_key = DEFAULT_IMAGE_KEY
        
        response = {
            'inline': {
                'i18n_title': {
                    'zh_cn': inline_title
                }
            }
        }
        if image_key and not image_key.startswith('REPLACE'):
            response['inline']['image_key'] = image_key
        
        return jsonify(response)
    
    return jsonify({'code': 0})


# ============================
# 浏览器端路由
# ============================
@app.route('/time')
def time_page():
    return redirect('https://time.is/')

@app.route('/offwork')
def offwork_page():
    now = beijing_now()
    today_18 = now.replace(hour=18, minute=0, second=0, microsecond=0)
    if now >= today_18:
        tomorrow_18 = today_18 + datetime.timedelta(days=1)
        delta = tomorrow_18 - now
        hours = delta.seconds // 3600
        minutes = (delta.seconds % 3600) // 60
        return f'<h1>🎉 已经下班啦！</h1><p>距离明天18:00还有 {hours}小时{minutes}分</p >'
    else:
        delta = today_18 - now
        hours = delta.seconds // 3600
        minutes = (delta.seconds % 3600) // 60
        return f'<h1>⏳ 距下班还有 {hours}小时{minutes}分</h1>'

@app.route('/tarot')
def tarot_page():
    return redirect('https://tarotap.com/')

@app.route('/hitokoto')
def hitokoto_page():
    return redirect('https://hitokoto.cn/')

@app.route('/hello')
def hello_page():
    return '<h1>👋 你好，欢迎来到蔡硕的动态签名服务</h1>'

@app.route('/gif1')
def gif1_page():
    return '<h1>🎬 GIF 1</h1>'

@app.route('/gif2')
def gif2_page():
    return '<h1>🎬 GIF 2</h1>'

@app.route('/gif3')
def gif3_page():
    return '<h1>🎬 GIF 3</h1>'

@app.route('/gif4')
def gif4_page():
    return '<h1>🎬 GIF 4</h1>'

@app.route('/d<code>')
def custom_link_page(code):
    key = f'd{code}'
    if key in CUSTOM_LINKS:
        return redirect(CUSTOM_LINKS[key][0])
    return redirect('https://caishuo.work/')

@app.route('/say/<text>')
def say_page(text):
    from urllib.parse import unquote
    try:
        text = unquote(text)
    except:
        pass
    return f'<h1>{text}</h1>'

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def catch_all(path):
    return '<h1>✨ 蔡硕的动态签名服务</h1><p>支持：/time /offwork /tarot /hitokoto /hello /gif1~/gif4 /say/文字 /d1~/d3</p >'


if __name__ == '__main__':
    app.run(debug=True)
