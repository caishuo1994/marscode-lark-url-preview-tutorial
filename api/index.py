from flask import Flask, request, redirect, jsonify
import datetime
import hashlib
import random
import re
import os
import uuid
import base64

app = Flask(__name__)

# ============================
# 美观主页 HTML
# ============================
HOME_PAGE_HTML = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>蔡硕的个人空间</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'PingFang SC', 'Hiragino Sans GB', 'Microsoft YaHei', sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            color: #333;
            overflow-x: hidden;
        }

        .container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 40px 20px;
        }

        /* 头部 */
        .header {
            text-align: center;
            color: white;
            margin-bottom: 50px;
            animation: fadeInDown 0.8s ease;
        }

        .header h1 {
            font-size: 3em;
            font-weight: 700;
            margin-bottom: 15px;
            text-shadow: 0 2px 10px rgba(0,0,0,0.2);
        }

        .header p {
            font-size: 1.2em;
            opacity: 0.9;
            font-weight: 300;
        }

        .avatar {
            width: 100px;
            height: 100px;
            border-radius: 50%;
            background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
            margin: 0 auto 20px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 2.5em;
            box-shadow: 0 10px 30px rgba(0,0,0,0.3);
            animation: pulse 2s infinite;
        }

        /* 闹钟入口大卡片 */
        .alarm-card {
            background: white;
            border-radius: 20px;
            padding: 40px;
            margin-bottom: 40px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            text-align: center;
            animation: fadeInUp 0.8s ease 0.2s both;
            transition: transform 0.3s ease, box-shadow 0.3s ease;
            cursor: pointer;
            text-decoration: none;
            display: block;
            color: inherit;
        }

        .alarm-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 25px 70px rgba(0,0,0,0.4);
        }

        .alarm-icon {
            font-size: 4em;
            margin-bottom: 20px;
            animation: ring 1s ease-in-out infinite;
        }

        .alarm-card h2 {
            font-size: 2em;
            color: #333;
            margin-bottom: 10px;
        }

        .alarm-card p {
            font-size: 1.1em;
            color: #666;
            margin-bottom: 25px;
        }

        .alarm-btn {
            display: inline-block;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 15px 50px;
            border-radius: 50px;
            font-size: 1.1em;
            font-weight: 600;
            text-decoration: none;
            transition: transform 0.3s ease, box-shadow 0.3s ease;
            box-shadow: 0 5px 20px rgba(102, 126, 234, 0.4);
        }

        .alarm-btn:hover {
            transform: scale(1.05);
            box-shadow: 0 8px 30px rgba(102, 126, 234, 0.6);
        }

        /* 功能卡片网格 */
        .section-title {
            color: white;
            font-size: 1.5em;
            margin-bottom: 25px;
            text-align: center;
            font-weight: 600;
        }

        .features-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-bottom: 40px;
        }

        .feature-card {
            background: rgba(255, 255, 255, 0.95);
            border-radius: 15px;
            padding: 25px;
            text-align: center;
            text-decoration: none;
            color: inherit;
            transition: transform 0.3s ease, box-shadow 0.3s ease;
            box-shadow: 0 5px 20px rgba(0,0,0,0.1);
            animation: fadeInUp 0.6s ease both;
        }

        .feature-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
        }

        .feature-icon {
            font-size: 2.5em;
            margin-bottom: 15px;
        }

        .feature-card h3 {
            font-size: 1.2em;
            color: #333;
            margin-bottom: 8px;
        }

        .feature-card p {
            font-size: 0.9em;
            color: #888;
        }

        /* 自定义链接区域 */
        .custom-links {
            background: rgba(255, 255, 255, 0.1);
            border-radius: 15px;
            padding: 30px;
            margin-bottom: 40px;
            backdrop-filter: blur(10px);
        }

        .custom-links h3 {
            color: white;
            font-size: 1.3em;
            margin-bottom: 20px;
            text-align: center;
        }

        .custom-links-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
        }

        .custom-link {
            background: rgba(255, 255, 255, 0.9);
            border-radius: 10px;
            padding: 15px;
            text-align: center;
            text-decoration: none;
            color: #333;
            font-weight: 500;
            transition: transform 0.3s ease;
        }

        .custom-link:hover {
            transform: scale(1.05);
        }

        /* 页脚 */
        .footer {
            text-align: center;
            color: rgba(255, 255, 255, 0.7);
            padding: 30px 0;
            font-size: 0.9em;
        }

        .footer a {
            color: rgba(255, 255, 255, 0.9);
            text-decoration: none;
        }

        /* 动画 */
        @keyframes fadeInDown {
            from {
                opacity: 0;
                transform: translateY(-30px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }

        @keyframes fadeInUp {
            from {
                opacity: 0;
                transform: translateY(30px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }

        @keyframes pulse {
            0%, 100% {
                transform: scale(1);
            }
            50% {
                transform: scale(1.05);
            }
        }

        @keyframes ring {
            0%, 100% {
                transform: rotate(0deg);
            }
            10%, 30%, 50%, 70%, 90% {
                transform: rotate(-10deg);
            }
            20%, 40%, 60%, 80% {
                transform: rotate(10deg);
            }
        }

        /* 响应式 */
        @media (max-width: 768px) {
            .header h1 {
                font-size: 2em;
            }

            .alarm-card {
                padding: 30px 20px;
            }

            .alarm-card h2 {
                font-size: 1.5em;
            }

            .features-grid {
                grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <!-- 头部 -->
        <div class="header">
            <div class="avatar">👨‍💻</div>
            <h1>蔡硕的个人空间</h1>
            <p>✨ 飞书动态个性签名 · 倒计时闹钟 · 更多精彩功能</p>
        </div>

        <!-- 闹钟入口大卡片 -->
        <a href="/alarm" class="alarm-card">
            <div class="alarm-icon">⏰</div>
            <h2>倒计时闹钟</h2>
            <p>18+ 个性铃声 · 用户上传专区 · 社区铃声库</p>
            <span class="alarm-btn">立即使用 →</span>
        </a>

        <!-- 飞书个性签名功能 -->
        <h2 class="section-title">🎯 飞书动态个性签名</h2>
        <div class="features-grid">
            <a href="/time" class="feature-card" style="animation-delay: 0.1s">
                <div class="feature-icon">🕐</div>
                <h3>实时时间</h3>
                <p>显示当前时间和星期</p>
            </a>
            <a href="/offwork" class="feature-card" style="animation-delay: 0.2s">
                <div class="feature-icon">🏃</div>
                <h3>下班倒计时</h3>
                <p>距离下班还有多久</p>
            </a>
            <a href="/tarot" class="feature-card" style="animation-delay: 0.3s">
                <div class="feature-icon">🔮</div>
                <h3>每日塔罗</h3>
                <p>今日运势塔罗牌</p>
            </a>
            <a href="/hitokoto" class="feature-card" style="animation-delay: 0.4s">
                <div class="feature-icon">💬</div>
                <h3>一言金句</h3>
                <p>每日一句励志名言</p>
            </a>
            <a href="/hello" class="feature-card" style="animation-delay: 0.5s">
                <div class="feature-icon">👋</div>
                <h3>问候语</h3>
                <p>根据时间自动问候</p>
            </a>
            <a href="/gif1" class="feature-card" style="animation-delay: 0.6s">
                <div class="feature-icon">🎬</div>
                <h3>GIF 动图 1</h3>
                <p>动态表情图片</p>
            </a>
            <a href="/gif2" class="feature-card" style="animation-delay: 0.7s">
                <div class="feature-icon">🎬</div>
                <h3>GIF 动图 2</h3>
                <p>动态表情图片</p>
            </a>
            <a href="/gif3" class="feature-card" style="animation-delay: 0.8s">
                <div class="feature-icon">🎬</div>
                <h3>GIF 动图 3</h3>
                <p>动态表情图片</p>
            </a>
            <a href="/gif4" class="feature-card" style="animation-delay: 0.9s">
                <div class="feature-icon">🎬</div>
                <h3>GIF 动图 4</h3>
                <p>动态表情图片</p>
            </a>
        </div>

        <!-- 自定义链接 -->
        <div class="custom-links">
            <h3>🔗 我的精选链接</h3>
            <div class="custom-links-grid">
                <a href="/d1" class="custom-link">📹 查看当前工作状态</a>
                <a href="/d2" class="custom-link">📹 查看审核状态回放</a>
                <a href="/d3" class="custom-link">🎁 点击领取十天年假</a>
            </div>
        </div>

        <!-- 使用说明 -->
        <div class="custom-links">
            <h3>💡 使用说明</h3>
            <div style="color: rgba(255,255,255,0.9); line-height: 1.8; font-size: 0.95em;">
                <p>• 将 <code style="background: rgba(255,255,255,0.2); padding: 2px 8px; border-radius: 4px;">https://caishuo.work/time</code> 等链接发送到飞书聊天，即可显示动态个性签名预览</p>
                <p>• 支持自定义文字：<code style="background: rgba(255,255,255,0.2); padding: 2px 8px; border-radius: 4px;">https://caishuo.work/say/你想说的话</code></p>
                <p>• 倒计时闹钟支持自定义铃声上传和社区铃声分享</p>
            </div>
        </div>

        <!-- 页脚 -->
        <div class="footer">
            <p>© 2026 蔡硕的个人空间 ·  Powered by Vercel + GitHub</p>
            <p style="margin-top: 10px;">
                <a href="https://github.com/caishuo1994" target="_blank">GitHub</a> · 
                <a href="/alarm">倒计时闹钟</a>
            </p>
        </div>
    </div>
</body>
</html>
"""



# ============================
# GIF 动图配置（4张已替换）
# ============================
GIF_KEYS = {
    'gif1': 'img_v3_0214s_e2def39a-b040-4cab-b8c3-0bef3b66e55g',
    'gif2': 'img_v3_0214s_17a5b761-cc33-443d-b977-919e02f8498g',
    'gif3': 'img_v3_0214s_1462c9b5-3ec6-4a27-abb2-5ee62a05c8dg',
    'gif4': 'img_v3_0214s_6f96c0d6-3b2c-437b-bcd1-44574ff4b7ag',
}

# 默认图标（加载中）
DEFAULT_IMAGE_KEY = 'img_v3_0214s_67cf2b4e-ce7c-41e7-94f2-48e0fb056cfg'

# ============================
# 自定义链接映射
# ============================
CUSTOM_LINKS = {
    'd1': ('https://www.douyin.com/video/7598860026035380454', '查看当前工作状态'),
    'd2': ('https://www.douyin.com/video/7574824840138598565', '查看郑雨阳审核状态回放'),
    'd3': ('https://www.douyin.com/video/7596097269067724773', '点击领取十天年假'),
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
            inline_title = f"👋 {greeting}，"
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
            inline_title = '✨ 蔡硕的链接预览服务'
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
# 闹钟网站路由（直接读取静态文件）
# ============================
@app.route('/alarm')
def alarm_page():
    import os
    possible_paths = [
        os.path.join(os.path.dirname(os.path.abspath(__file__)), 'alarm.html'),
        '/var/task/api/alarm.html',
        'api/alarm.html',
    ]
    for path in possible_paths:
        if os.path.exists(path):
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    return f.read()
            except:
                continue
    return '<h1>⏰ 闹钟网站</h1><p>正在加载中...</p>'

# ============================

# ============================
# Supabase 后端存储配置（使用 requests 直接调用 REST API）
# ============================
import requests as supabase_requests

SUPABASE_URL = os.environ.get('SUPABASE_URL', '')
SUPABASE_SERVICE_KEY = os.environ.get('SUPABASE_SERVICE_KEY', '')
ADMIN_PASSWORD = os.environ.get('ADMIN_PASSWORD', 'admin123')

SUPABASE_AVAILABLE = bool(SUPABASE_URL and SUPABASE_SERVICE_KEY)
supabase_error = None if SUPABASE_AVAILABLE else "SUPABASE_URL 或 SUPABASE_SERVICE_KEY 环境变量未配置"

print(f"[INFO] Supabase 状态: {'可用' if SUPABASE_AVAILABLE else '不可用 - ' + str(supabase_error)}")

def supabase_headers():
    """生成 supabase 请求头"""
    return {
        'apikey': SUPABASE_SERVICE_KEY,
        'Authorization': f'Bearer {SUPABASE_SERVICE_KEY}',
        'Content-Type': 'application/json',
    }

def supabase_get(table, params=None):
    """查询数据"""
    url = f'{SUPABASE_URL}/rest/v1/{table}'
    resp = supabase_requests.get(url, headers=supabase_headers(), params=params or {}, timeout=10)
    resp.raise_for_status()
    return resp.json()

def supabase_insert(table, data):
    """插入数据"""
    url = f'{SUPABASE_URL}/rest/v1/{table}'
    resp = supabase_requests.post(url, headers=supabase_headers(), json=data, timeout=10)
    resp.raise_for_status()
    return resp.json()

def supabase_update(table, data, id_value):
    """更新数据"""
    url = f'{SUPABASE_URL}/rest/v1/{table}?id=eq.{id_value}'
    resp = supabase_requests.patch(url, headers=supabase_headers(), json=data, timeout=10)
    resp.raise_for_status()
    return resp.json()

def supabase_delete(table, id_value):
    """删除数据"""
    url = f'{SUPABASE_URL}/rest/v1/{table}?id=eq.{id_value}'
    resp = supabase_requests.delete(url, headers=supabase_headers(), timeout=10)
    resp.raise_for_status()
    return resp.json()

def supabase_upload_storage(bucket, path, file_bytes, content_type):
    """上传文件到存储"""
    url = f'{SUPABASE_URL}/storage/v1/object/{bucket}/{path}'
    headers = {
        'apikey': SUPABASE_SERVICE_KEY,
        'Authorization': f'Bearer {SUPABASE_SERVICE_KEY}',
        'Content-Type': content_type,
    }
    resp = supabase_requests.post(url, headers=headers, data=file_bytes, timeout=30)
    resp.raise_for_status()
    return resp.json()

def supabase_get_public_url(bucket, path):
    """获取公开 URL"""
    return f'{SUPABASE_URL}/storage/v1/object/public/{bucket}/{path}'


# ============================
# 铃声后端 API（使用 requests 直接调用 Supabase REST API）
# ============================
@app.route('/api/ringtones', methods=['GET'])
def get_ringtones():
    """获取已审核通过的铃声列表"""
    if not SUPABASE_AVAILABLE:
        return jsonify({'error': '后端存储未配置', 'detail': supabase_error}), 500
    try:
        result = supabase_get('ringtones', {'select': '*', 'status': 'eq.approved', 'order': 'created_at.desc'})
        return jsonify({'success': True, 'data': result})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/ringtones/pending', methods=['GET'])
def get_pending_ringtones():
    """获取待审核的铃声列表（管理员）"""
    if not SUPABASE_AVAILABLE:
        return jsonify({'error': '后端存储未配置'}), 500
    password = request.headers.get('X-Admin-Password', '')
    if password != ADMIN_PASSWORD:
        return jsonify({'error': '无权限'}), 403
    try:
        result = supabase_get('ringtones', {'select': '*', 'status': 'eq.pending', 'order': 'created_at.desc'})
        return jsonify({'success': True, 'data': result})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/ringtones/upload', methods=['POST'])
def upload_ringtone():
    """上传铃声（状态为 pending，等待审核）"""
    if not SUPABASE_AVAILABLE:
        return jsonify({'error': '后端存储未配置'}), 500
    try:
        data = request.get_json()
        name = data.get('name', '').strip()
        audio_data = data.get('audio_data', '')
        cover_data = data.get('cover_data', '')
        uploader_name = data.get('uploader_name', '匿名用户').strip()
        
        if not name or not audio_data or not cover_data:
            return jsonify({'error': '铃声名称、音频和封面都不能为空'}), 400
        
        import uuid
        import base64
        file_id = str(uuid.uuid4())
        audio_path = f'audio/{file_id}.mp3'
        cover_path = f'cover/{file_id}.jpg'
        
        audio_bytes = base64.b64decode(audio_data.split(',')[-1])
        cover_bytes = base64.b64decode(cover_data.split(',')[-1])
        
        supabase_upload_storage('ringtones', audio_path, audio_bytes, 'audio/mpeg')
        supabase_upload_storage('ringtones', cover_path, cover_bytes, 'image/jpeg')
        
        audio_url = supabase_get_public_url('ringtones', audio_path)
        cover_url = supabase_get_public_url('ringtones', cover_path)
        
        result = supabase_insert('ringtones', {
            'name': name,
            'audio_url': audio_url,
            'cover_url': cover_url,
            'uploader_name': uploader_name,
            'status': 'pending',
            'plays': 0
        })
        
        return jsonify({'success': True, 'message': '上传成功，等待管理员审核', 'data': result[0] if result else {}})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/ringtones/approve', methods=['POST'])
def approve_ringtone():
    """管理员审核通过"""
    if not SUPABASE_AVAILABLE:
        return jsonify({'error': '后端存储未配置'}), 500
    password = request.headers.get('X-Admin-Password', '')
    if password != ADMIN_PASSWORD:
        return jsonify({'error': '无权限'}), 403
    try:
        data = request.get_json()
        ringtone_id = data.get('id')
        if not ringtone_id:
            return jsonify({'error': '缺少铃声ID'}), 400
        result = supabase_update('ringtones', {'status': 'approved'}, ringtone_id)
        return jsonify({'success': True, 'data': result})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/ringtones/reject', methods=['POST'])
def reject_ringtone():
    """管理员拒绝"""
    if not SUPABASE_AVAILABLE:
        return jsonify({'error': '后端存储未配置'}), 500
    password = request.headers.get('X-Admin-Password', '')
    if password != ADMIN_PASSWORD:
        return jsonify({'error': '无权限'}), 403
    try:
        data = request.get_json()
        ringtone_id = data.get('id')
        if not ringtone_id:
            return jsonify({'error': '缺少铃声ID'}), 400
        result = supabase_update('ringtones', {'status': 'rejected'}, ringtone_id)
        return jsonify({'success': True, 'data': result})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/ringtones/delete', methods=['POST'])
def delete_ringtone():
    """管理员删除"""
    if not SUPABASE_AVAILABLE:
        return jsonify({'error': '后端存储未配置'}), 500
    password = request.headers.get('X-Admin-Password', '')
    if password != ADMIN_PASSWORD:
        return jsonify({'error': '无权限'}), 403
    try:
        data = request.get_json()
        ringtone_id = data.get('id')
        if not ringtone_id:
            return jsonify({'error': '缺少铃声ID'}), 400
        result = supabase_delete('ringtones', ringtone_id)
        return jsonify({'success': True, 'data': result})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/ringtones/stats', methods=['GET'])
def get_ringtone_stats():
    """获取统计信息"""
    if not SUPABASE_AVAILABLE:
        return jsonify({'error': '后端存储未配置'}), 500
    try:
        approved = supabase_get('ringtones', {'select': 'id', 'status': 'eq.approved'})
        pending = supabase_get('ringtones', {'select': 'id', 'status': 'eq.pending'})
        return jsonify({
            'success': True,
            'approved_count': len(approved),
            'pending_count': len(pending)
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500



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
    return '<h1>👋 你好，欢迎来到蔡硕的链接预览服务</h1>'

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



# ============================
# 工具函数
# ============================
def is_admin(request):
    """检查是否是管理员"""
    password = request.headers.get('X-Admin-Password', '')
    return password == ADMIN_PASSWORD

def get_file_extension(filename):
    """获取文件扩展名"""
    if '.' in filename:
        return filename.rsplit('.', 1)[1].lower()
    return ''

# ============================
# API 路由
# ============================

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def catch_all(path):
    if path == '' or path == '/':
        return HOME_PAGE_HTML
    return '<h1>✨ 蔡硕的链接预览服务</h1><p>支持：/time /offwork /tarot /hitokoto /hello /gif1~/gif4 /say/文字 /d1~/d3</p><p><a href="/">返回主页</a></p>' 


if __name__ == '__main__':
    app.run(debug=True)
