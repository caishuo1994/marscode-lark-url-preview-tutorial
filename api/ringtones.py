from flask import Flask, request, jsonify
import os
import uuid
import datetime
from supabase import create_client, Client

app = Flask(__name__)

# ============================
# Supabase 配置
# ============================
SUPABASE_URL = os.environ.get('SUPABASE_URL', '')
SUPABASE_SERVICE_KEY = os.environ.get('SUPABASE_SERVICE_KEY', '')
ADMIN_PASSWORD = os.environ.get('ADMIN_PASSWORD', 'admin123')

supabase: Client = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)

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

@app.route('/api/ringtones', methods=['GET'])
def get_ringtones():
    """获取所有已审核通过的铃声列表"""
    try:
        response = supabase.table('ringtones')\
            .select('*')\
            .eq('status', 'approved')\
            .order('created_at', desc=True)\
            .execute()
        
        return jsonify({
            'success': True,
            'data': response.data,
            'count': len(response.data)
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/ringtones/pending', methods=['GET'])
def get_pending_ringtones():
    """获取待审核的铃声列表（管理员）"""
    if not is_admin(request):
        return jsonify({
            'success': False,
            'error': '无权限访问'
        }), 403
    
    try:
        response = supabase.table('ringtones')\
            .select('*')\
            .eq('status', 'pending')\
            .order('created_at', desc=True)\
            .execute()
        
        return jsonify({
            'success': True,
            'data': response.data,
            'count': len(response.data)
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/ringtones/upload', methods=['POST'])
def upload_ringtone():
    """上传铃声（音频+封面+名称）"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'error': '请求数据为空'
            }), 400
        
        name = data.get('name', '').strip()
        audio_base64 = data.get('audio', '')
        cover_base64 = data.get('cover', '')
        uploader_name = data.get('uploader_name', '匿名用户')
        
        if not name:
            return jsonify({
                'success': False,
                'error': '铃声名称不能为空'
            }), 400
        
        if not audio_base64:
            return jsonify({
                'success': False,
                'error': '音频文件不能为空'
            }), 400
        
        # 生成唯一文件名
        file_id = str(uuid.uuid4())
        audio_filename = f"{file_id}.mp3"
        cover_filename = f"{file_id}.jpg" if cover_base64 else None
        
        # 上传音频文件到 Supabase 存储
        import base64
        audio_bytes = base64.b64decode(audio_base64)
        
        supabase.storage.from_('ringtones').upload(
            f"audio/{audio_filename}",
            audio_bytes,
            file_options={"content-type": "audio/mpeg"}
        )
        
        # 获取音频公开 URL
        audio_url = supabase.storage.from_('ringtones').get_public_url(f"audio/{audio_filename}")
        
        # 上传封面图片（如果有）
        cover_url = None
        if cover_base64:
            cover_bytes = base64.b64decode(cover_base64)
            supabase.storage.from_('ringtones').upload(
                f"covers/{cover_filename}",
                cover_bytes,
                file_options={"content-type": "image/jpeg"}
            )
            cover_url = supabase.storage.from_('ringtones').get_public_url(f"covers/{cover_filename}")
        
        # 保存铃声信息到数据库（状态为 pending 待审核）
        response = supabase.table('ringtones').insert({
            'name': name,
            'audio_url': audio_url,
            'cover_url': cover_url,
            'uploader_name': uploader_name,
            'status': 'pending'
        }).execute()
        
        return jsonify({
            'success': True,
            'message': '上传成功，等待管理员审核',
            'data': response.data[0] if response.data else None
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/ringtones/approve', methods=['POST'])
def approve_ringtone():
    """管理员审核通过铃声"""
    if not is_admin(request):
        return jsonify({
            'success': False,
            'error': '无权限操作'
        }), 403
    
    try:
        data = request.get_json()
        ringtone_id = data.get('id', '')
        
        if not ringtone_id:
            return jsonify({
                'success': False,
                'error': '铃声ID不能为空'
            }), 400
        
        response = supabase.table('ringtones')\
            .update({'status': 'approved'})\
            .eq('id', ringtone_id)\
            .execute()
        
        return jsonify({
            'success': True,
            'message': '审核通过'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/ringtones/reject', methods=['POST'])
def reject_ringtone():
    """管理员拒绝铃声"""
    if not is_admin(request):
        return jsonify({
            'success': False,
            'error': '无权限操作'
        }), 403
    
    try:
        data = request.get_json()
        ringtone_id = data.get('id', '')
        reason = data.get('reason', '')
        
        if not ringtone_id:
            return jsonify({
                'success': False,
                'error': '铃声ID不能为空'
            }), 400
        
        response = supabase.table('ringtones')\
            .update({'status': 'rejected'})\
            .eq('id', ringtone_id)\
            .execute()
        
        return jsonify({
            'success': True,
            'message': '已拒绝'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/ringtones/delete', methods=['POST'])
def delete_ringtone():
    """管理员删除铃声"""
    if not is_admin(request):
        return jsonify({
            'success': False,
            'error': '无权限操作'
        }), 403
    
    try:
        data = request.get_json()
        ringtone_id = data.get('id', '')
        
        if not ringtone_id:
            return jsonify({
                'success': False,
                'error': '铃声ID不能为空'
            }), 400
        
        # 先获取铃声信息，找到文件路径
        response = supabase.table('ringtones')\
            .select('*')\
            .eq('id', ringtone_id)\
            .execute()
        
        if response.data:
            ringtone = response.data[0]
            # 删除存储中的文件
            try:
                if ringtone.get('audio_url'):
                    # 从 URL 中提取文件路径
                    audio_path = ringtone['audio_url'].split('/ringtones/')[-1]
                    supabase.storage.from_('ringtones').remove([audio_path])
                if ringtone.get('cover_url'):
                    cover_path = ringtone['cover_url'].split('/ringtones/')[-1]
                    supabase.storage.from_('ringtones').remove([cover_path])
            except:
                pass
        
        # 删除数据库记录
        supabase.table('ringtones')\
            .delete()\
            .eq('id', ringtone_id)\
            .execute()
        
        return jsonify({
            'success': True,
            'message': '已删除'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/ringtones/stats', methods=['GET'])
def get_stats():
    """获取铃声统计信息"""
    try:
        # 总数
        total_response = supabase.table('ringtones')\
            .select('id', count='exact')\
            .execute()
        
        # 已通过
        approved_response = supabase.table('ringtones')\
            .select('id', count='exact')\
            .eq('status', 'approved')\
            .execute()
        
        # 待审核
        pending_response = supabase.table('ringtones')\
            .select('id', count='exact')\
            .eq('status', 'pending')\
            .execute()
        
        return jsonify({
            'success': True,
            'data': {
                'total': total_response.count if hasattr(total_response, 'count') else 0,
                'approved': approved_response.count if hasattr(approved_response, 'count') else 0,
                'pending': pending_response.count if hasattr(pending_response, 'count') else 0
            }
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

if __name__ == '__main__':
    app.run(debug=True)
