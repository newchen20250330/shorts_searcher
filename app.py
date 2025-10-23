from flask import Flask, render_template, request, jsonify, send_file, Response
from googleapiclient.discovery import build
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv
import isodate
import csv
from io import StringIO

# 載入環境變數
load_dotenv()

app = Flask(__name__)

# YouTube API 設定
YOUTUBE_API_SERVICE_NAME = 'youtube'
YOUTUBE_API_VERSION = 'v3'

# 儲存最新搜尋結果用於匯出
last_search_results = []
# 儲存搜尋條件用於檔案命名
last_search_params = {}

# 真實的 API 配額追蹤（每日累積）
daily_quota_usage = {
    'date': datetime.now().strftime('%Y-%m-%d'),
    'search_calls': 0,
    'video_calls': 0,
    'category_calls': 0,
    'total_cost': 0
}

def get_api_key():
    """獲取 API Key，每次都重新讀取環境變數"""
    # 重新載入環境變數以確保最新值
    load_dotenv(override=True)
    api_key = os.getenv('YOUTUBE_API_KEY')
    print(f"🔍 讀取到的 API Key: {api_key[:15] + '...' if api_key and len(api_key) > 15 else api_key}")
    return api_key

def get_youtube_service():
    """建立 YouTube API 服務"""
    api_key = get_api_key()
    
    if not api_key or api_key == 'your_youtube_api_key_here':
        raise ValueError("請設定有效的 YouTube API Key")
    
    # 檢查 API Key 格式
    if not api_key.startswith('AIzaSy') or len(api_key) != 39:
        raise ValueError(f"API Key 格式錯誤。YouTube API Key 應該以 'AIzaSy' 開頭且長度為 39 字符。目前的 Key: {api_key[:10]}...")
    
    print(f"🔑 使用 API Key: {api_key[:15]}...{api_key[-5:]}")
    return build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION, developerKey=api_key)

def get_time_filter(hours):
    """根據小時數產生時間過濾器"""
    if hours == 24:
        published_after = datetime.utcnow() - timedelta(hours=24)
    elif hours == 12:
        published_after = datetime.utcnow() - timedelta(hours=12)
    elif hours == 6:
        published_after = datetime.utcnow() - timedelta(hours=6)
    else:
        return None
    
    return published_after.strftime('%Y-%m-%dT%H:%M:%SZ')

def format_duration(duration):
    """將 ISO 8601 格式的時間轉換為可讀格式"""
    try:
        parsed_duration = isodate.parse_duration(duration)
        total_seconds = int(parsed_duration.total_seconds())
        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        seconds = total_seconds % 60
        
        if hours > 0:
            return f"{hours}:{minutes:02d}:{seconds:02d}"
        else:
            return f"{minutes}:{seconds:02d}"
    except:
        return duration

def get_duration_seconds(duration):
    """將 ISO 8601 格式的時間轉換為秒數"""
    try:
        parsed_duration = isodate.parse_duration(duration)
        return int(parsed_duration.total_seconds())
    except:
        return 0

def format_view_count(view_count):
    """格式化觀看次數"""
    try:
        count = int(view_count)
        if count >= 1000000:
            return f"{count/1000000:.1f}M"
        elif count >= 1000:
            return f"{count/1000:.1f}K"
        else:
            return str(count)
    except:
        return view_count

def get_video_categories(youtube, region_code='TW'):
    """獲取YouTube影片類別清單"""
    try:
        categories_response = youtube.videoCategories().list(
            part='snippet',
            regionCode=region_code
        ).execute()
        
        categories = {}
        for item in categories_response['items']:
            categories[item['id']] = item['snippet']['title']
        
        return categories
    except Exception as e:
        print(f"⚠️  無法獲取類別資訊: {e}")
        return {}

def get_category_name(category_id, categories_dict):
    """根據類別ID獲取類別名稱"""
    return categories_dict.get(category_id, f'未知類別 ({category_id})')

def update_quota_usage(search_calls=0, video_calls=0, category_calls=0):
    """更新真實的 API 配額使用量"""
    global daily_quota_usage
    
    # 檢查是否是新的一天，如果是則重置
    today = datetime.now().strftime('%Y-%m-%d')
    if daily_quota_usage['date'] != today:
        print(f"🗓️ 新的一天開始，重置配額計算")
        daily_quota_usage = {
            'date': today,
            'search_calls': 0,
            'video_calls': 0,
            'category_calls': 0,
            'total_cost': 0
        }
    
    # 累積使用量
    daily_quota_usage['search_calls'] += search_calls
    daily_quota_usage['video_calls'] += video_calls
    daily_quota_usage['category_calls'] += category_calls
    
    # 計算總成本（搜尋 100 單位，其他 1 單位）
    total_cost = (daily_quota_usage['search_calls'] * 100 + 
                  daily_quota_usage['video_calls'] * 1 + 
                  daily_quota_usage['category_calls'] * 1)
    daily_quota_usage['total_cost'] = total_cost
    
    print(f"📊 配額更新: 搜尋{daily_quota_usage['search_calls']}次, 影片{daily_quota_usage['video_calls']}個, 類別{daily_quota_usage['category_calls']}次 = {total_cost}單位")
    
    return daily_quota_usage

def get_current_quota_info():
    """獲取當前配額資訊"""
    global daily_quota_usage
    
    # 檢查日期
    today = datetime.now().strftime('%Y-%m-%d')
    if daily_quota_usage['date'] != today:
        update_quota_usage()  # 重置到新一天
    
    total_cost = daily_quota_usage['total_cost']
    remaining_quota = 10000 - total_cost
    
    # 計算還能做幾次搜尋（假設每次搜尋 25 個結果 = 125 單位）
    estimated_searches_left = max(0, remaining_quota // 125)
    
    return {
        'current_cost': total_cost,
        'remaining_quota': remaining_quota,
        'estimated_searches_left': estimated_searches_left,
        'quota_percentage': round((total_cost / 10000) * 100, 1),
        'video_count': 0,  # 這個會在調用時更新
        'search_calls': daily_quota_usage['search_calls'],
        'video_calls': daily_quota_usage['video_calls'],
        'category_calls': daily_quota_usage['category_calls']
    }

def calculate_quota_cost(search_count=0, video_details_count=0, categories_call=0):
    """計算 API 配額消耗
    
    YouTube Data API v3 配額消耗:
    - search().list(): 100 單位
    - videos().list(): 1 單位 (每個影片)
    - videoCategories().list(): 1 單位
    """
    search_cost = search_count * 100
    video_details_cost = video_details_count * 1
    categories_cost = categories_call * 1
    
    total_cost = search_cost + video_details_cost + categories_cost
    return {
        'search_cost': search_cost,
        'video_details_cost': video_details_cost,
        'categories_cost': categories_cost,
        'total_cost': total_cost,
        'remaining_quota': 10000 - total_cost  # 假設每日配額 10,000
    }

def format_quota_info(quota_info, video_count):
    """格式化配額資訊為用戶友善的訊息"""
    total_cost = quota_info['total_cost']
    remaining = quota_info['remaining_quota']
    
    # 計算還能做幾次搜尋
    estimated_searches_left = remaining // 125  # 假設每次搜尋 25 個結果
    
    return {
        'current_cost': total_cost,
        'remaining_quota': remaining,
        'estimated_searches_left': max(0, estimated_searches_left),
        'quota_percentage': round((total_cost / 10000) * 100, 1),
        'video_count': video_count
    }

def generate_excel_filename(search_params):
    """根據搜尋條件生成Excel檔案名稱"""
    # 防錯處理
    if not search_params:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        return f'YouTube_搜尋結果_{timestamp}.xlsx'
    
    parts = []
    
    # 關鍵字（不顯示預設的 shorts）
    keyword = search_params.get('keyword', 'shorts')
    if keyword and keyword != 'shorts':
        # 清理不合法的檔案名字元
        safe_keyword = ''.join(c for c in keyword if c.isalnum() or c in '-_')
        if safe_keyword:  # 確保清理後還有內容
            parts.append(safe_keyword[:20])  # 限制長度
    
    # 類別
    category_filter = search_params.get('category_filter', 'all')
    if category_filter != 'all':
        category_names = {
            '1': '電影', '2': '汽車', '10': '音樂', '15': '寵物',
            '17': '體育', '19': '旅遊', '20': '遊戲', '22': '部落格',
            '23': '喜劇', '24': '娛樂', '25': '新聞', '26': '教學',
            '27': '教育', '28': '科技'
        }
        category_name = category_names.get(category_filter, f'cat{category_filter}')
        parts.append(category_name)
    
    # 上傳時間
    time_filter = search_params.get('time_filter', 'all')
    if time_filter != 'all':
        parts.append(f'{time_filter}h')
    
    # 最少觀看次數
    min_views = search_params.get('min_views', 0)
    if min_views > 0:
        if min_views >= 1000000:
            parts.append(f'{min_views//1000000}M觀看')
        elif min_views >= 1000:
            parts.append(f'{min_views//1000}K觀看')
        else:
            parts.append(f'{min_views}觀看')
    
    # 影片長度
    max_duration = search_params.get('max_duration', 'all')
    if max_duration != 'all':
        parts.append(f'{max_duration}s')
    
    # 結果數量（只在非預設值時顯示）
    max_results = search_params.get('max_results', 25)
    if max_results != 25:
        parts.append(f'{max_results}筆')
    
    # 時間戳
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    # 組合檔案名（過濾空部件）
    if parts:
        filename_parts = '_'.join(parts)
        filename = f'YouTube_{filename_parts}_{timestamp}.xlsx'
    else:
        filename = f'YouTube搜尋_{timestamp}.xlsx'
    
    # 確保檔案名不過長
    if len(filename) > 100:
        filename = f'YouTube_搜尋結果_{timestamp}.xlsx'
    
    return filename

def generate_csv_filename(search_params):
    """根據搜尋條件生成CSV檔案名稱"""
    # 防錯處理
    if not search_params:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        return f'YouTube_Search_{timestamp}.csv'
    
    parts = []
    
    # 關鍵字（不顯示預設的 shorts）
    keyword = search_params.get('keyword', 'shorts')
    if keyword and keyword != 'shorts':
        # 清理不合法的檔案名字元，只保留英數字
        safe_keyword = ''.join(c for c in keyword if c.isalnum() or c in '-_')
        if safe_keyword:  # 確保清理後還有內容
            parts.append(safe_keyword[:20])  # 限制長度
    
    # 類別 - 使用英文避免編碼問題
    category_filter = search_params.get('category_filter', 'all')
    if category_filter != 'all':
        category_names = {
            '1': 'movie', '2': 'autos', '10': 'music', '15': 'pets',
            '17': 'sports', '19': 'travel', '20': 'gaming', '22': 'blogs',
            '23': 'comedy', '24': 'entertainment', '25': 'news', '26': 'howto',
            '27': 'education', '28': 'tech'
        }
        category_name = category_names.get(category_filter, f'cat{category_filter}')
        parts.append(category_name)
    
    # 上傳時間
    time_filter = search_params.get('time_filter', 'all')
    if time_filter != 'all':
        parts.append(f'{time_filter}h')
    
    # 最少觀看次數 - 移除中文
    min_views = search_params.get('min_views', 0)
    if min_views > 0:
        if min_views >= 1000000:
            parts.append(f'{min_views//1000000}M')
        elif min_views >= 1000:
            parts.append(f'{min_views//1000}K')
        else:
            parts.append(f'{min_views}v')
    
    # 影片長度
    max_duration = search_params.get('max_duration', 'all')
    if max_duration != 'all':
        parts.append(f'{max_duration}s')
    
    # 結果數量（只在非預設值時顯示）
    max_results = search_params.get('max_results', 25)
    if max_results != 25:
        parts.append(f'{max_results}results')
    
    # 時間戳
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    # 組合檔案名（過濾空部件，只使用英數字）
    if parts:
        filename_parts = '_'.join(parts)
        filename = f'YouTube_{filename_parts}_{timestamp}.csv'
    else:
        filename = f'YouTube_Search_{timestamp}.csv'
    
    # 確保檔案名不過長
    if len(filename) > 100:
        filename = f'YouTube_Search_{timestamp}.csv'
    
    return filename

@app.route('/')
def index():
    """首頁"""
    return render_template('index.html')

@app.route('/search', methods=['POST'])
def search_videos():
    """搜尋影片"""
    global last_search_results, last_search_params  # 在函數開頭統一宣告
    
    try:
        # 取得搜尋參數
        data = request.get_json()
        keyword = data.get('keyword', '').strip()
        category_filter = data.get('categoryFilter', 'all')
        region_filter = data.get('regionFilter', 'TW')
        time_filter = data.get('timeFilter', 'all')
        min_views = data.get('minViews', 10000)  # 預設最少觀看次数1萬
        max_duration = data.get('maxDuration', 'all')
        max_results = data.get('maxResults', 25)
        
        # 儲存搜尋條件用於檔案命名
        last_search_params = {
            'keyword': keyword if keyword else 'shorts',
            'category_filter': category_filter,
            'region_filter': region_filter,
            'time_filter': time_filter,
            'min_views': min_views,
            'max_duration': max_duration,
            'max_results': max_results
        }
        
        # 如果沒有關鍵字，使用預設的 shorts 關鍵字
        if not keyword:
            keyword = 'shorts'
            print("🎥 使用預設關鍵字: shorts")
        
        print(f"🔍 搜尋參數: 關鍵字='{keyword}', 類別={category_filter}, 地區={region_filter}, 時間={time_filter}, 最少觀看={min_views}, 最大長度={max_duration}")
        
        # 建立 YouTube 服務
        youtube = get_youtube_service()
        
        # 獲取影片類別資訊
        print("📊 獲取影片類別資訊...")
        categories = get_video_categories(youtube)
        print(f"🏷️  獲取到 {len(categories)} 個類別")
        
        # 更新配額使用（類別 API 調用）
        update_quota_usage(category_calls=1)
        
        # 記錄 API 呼叫次數用於配額計算
        api_calls = {
            'search_count': 0,
            'video_details_count': 0,
            'categories_call': 1  # 獲取類別資訊
        }
        
        print(f"🔎 使用關鍵字搜尋: {keyword}")
        
        # 為了獲得足夠的結果，我們先搜尋更多的影片
        search_batch_size = min(50, max_results * 3)  # 搜尋3倍的數量以確保有足夠結果
        
        # 使用搜尋 API
        search_params = {
            'part': 'snippet',
            'q': keyword,
            'type': 'video',
            'order': 'relevance',
            'maxResults': search_batch_size,
            'regionCode': region_filter
        }
        
        # 根據地區設定語言偏好
        if region_filter in ['TW', 'CN', 'HK', 'SG']:
            search_params['relevanceLanguage'] = 'zh'
        elif region_filter == 'JP':
            search_params['relevanceLanguage'] = 'ja'
        elif region_filter == 'KR':
            search_params['relevanceLanguage'] = 'ko'
        elif region_filter in ['NO']:
            search_params['relevanceLanguage'] = 'no'
        elif region_filter in ['CH', 'DE']:
            search_params['relevanceLanguage'] = 'de'
        elif region_filter in ['DK']:
            search_params['relevanceLanguage'] = 'da'
        elif region_filter in ['AE', 'SA']:
            search_params['relevanceLanguage'] = 'ar'
        elif region_filter in ['US', 'GB', 'CA', 'AU', 'IN']:
            search_params['relevanceLanguage'] = 'en'
        elif region_filter in ['FR']:
            search_params['relevanceLanguage'] = 'fr'
        elif region_filter in ['RU']:
            search_params['relevanceLanguage'] = 'ru'
        
        # 添加分類過濾器
        if category_filter != 'all':
            search_params['videoCategoryId'] = category_filter
            print(f"🏷️  使用分類過濾: {category_filter}")
        
        # 添加時間過濾器
        if time_filter != 'all':
            hours = int(time_filter)
            published_after = get_time_filter(hours)
            if published_after:
                search_params['publishedAfter'] = published_after
        
        # 執行初次搜尋
        search_response = youtube.search().list(**search_params).execute()
        api_calls['search_count'] = 1
        
        # 更新配額使用（搜尋 API 調用）
        update_quota_usage(search_calls=1)
        
        # 收集所有影片ID並去除重複
        all_video_ids = []
        seen_ids = set()
        
        for item in search_response['items']:
            video_id = item['id']['videoId']
            if video_id not in seen_ids:
                all_video_ids.append(video_id)
                seen_ids.add(video_id)
        
        # 如果結果不夠，嘗試獲取下一頁
        while len(all_video_ids) < min(max_results * 2, 50) and 'nextPageToken' in search_response:
            print(f"📄 當前有 {len(all_video_ids)} 個影片，嘗試獲取更多...")
            search_params['pageToken'] = search_response['nextPageToken']
            search_response = youtube.search().list(**search_params).execute()
            api_calls['search_count'] += 1
            
            # 更新配額使用
            update_quota_usage(search_calls=1)
            
            for item in search_response['items']:
                video_id = item['id']['videoId']
                if video_id not in seen_ids and len(all_video_ids) < 50:
                    all_video_ids.append(video_id)
                    seen_ids.add(video_id)
            
            # 避免過多API呼叫
            if api_calls['search_count'] >= 3:
                break
        
        print(f"🎥 總共獲取到 {len(all_video_ids)} 個唯一影片 ID")
        
        if not all_video_ids:
            print("⚠️  沒有獲取到任何影片 ID")
            return jsonify({
                'success': True,
                'videos': [],
                'totalResults': 0
            })
        
        # 分批取得影片詳細資訊（YouTube API 限制每次最多50個ID）
        batch_size = 50
        all_video_items = []
        
        for i in range(0, len(all_video_ids), batch_size):
            batch_ids = all_video_ids[i:i + batch_size]
            print(f"📊 處理第 {i//batch_size + 1} 批影片，共 {len(batch_ids)} 個")
            
            try:
                videos_response = youtube.videos().list(
                    part='snippet,statistics,contentDetails',
                    id=','.join(batch_ids)
                ).execute()
                
                all_video_items.extend(videos_response.get('items', []))
                # 記錄實際處理的影片數量用於配額計算
                api_calls['video_details_count'] += len(batch_ids)
                
                # 更新配額使用（影片詳情 API 調用）
                update_quota_usage(video_calls=len(batch_ids))
                
            except Exception as e:
                print(f"⚠️ 批次 {i//batch_size + 1} 處理失敗: {e}")
                continue
        
        print(f"📊 成功獲取到 {len(all_video_items)} 個影片詳細資訊")
        
        videos = []
        for item in all_video_items:
            video_data = item['snippet']
            statistics = item['statistics']
            content_details = item['contentDetails']
            
            # 檢查觀看次數過濾器
            view_count = int(statistics.get('viewCount', 0))
            if view_count < min_views:
                print(f"⏭️  跳過影片 {item['id']}: 觀看次數 {view_count} < {min_views}")
                continue
            
            # 檢查影片長度過濾器
            if max_duration != 'all':
                duration_seconds = get_duration_seconds(content_details.get('duration', ''))
                max_duration_seconds = int(max_duration)
                if duration_seconds > max_duration_seconds:
                    print(f"⏭️  跳過影片 {item['id']}: 長度 {duration_seconds}秒 > {max_duration_seconds}秒")
                    continue
            
            print(f"✅ 包含影片 {item['id']}: {video_data['title'][:50]}... (觀看: {view_count}, 長度: {get_duration_seconds(content_details.get('duration', ''))}秒)")
            
            # 獲取類別名稱
            category_id = video_data.get('categoryId', '')
            category_name = get_category_name(category_id, categories)
            
            video_info = {
                'videoId': item['id'],
                'title': video_data['title'],
                'description': video_data['description'],
                'channelTitle': video_data['channelTitle'],
                'channelId': video_data['channelId'],
                'publishedAt': video_data['publishedAt'],
                'thumbnails': video_data['thumbnails'],
                'categoryId': category_id,
                'categoryName': category_name,
                'defaultLanguage': video_data.get('defaultLanguage', ''),
                'defaultAudioLanguage': video_data.get('defaultAudioLanguage', ''),
                'tags': video_data.get('tags', []),
                'viewCount': statistics.get('viewCount', '0'),
                'likeCount': statistics.get('likeCount', '0'),
                'commentCount': statistics.get('commentCount', '0'),
                'duration': content_details.get('duration', ''),
                'definition': content_details.get('definition', ''),
                'caption': content_details.get('caption', ''),
                'licensedContent': content_details.get('licensedContent', False),
                'projection': content_details.get('projection', ''),
                'url': f"https://www.youtube.com/watch?v={item['id']}",
                'formattedViewCount': format_view_count(statistics.get('viewCount', '0')),
                'formattedDuration': format_duration(content_details.get('duration', ''))
            }
            videos.append(video_info)
        
        # 根據觀看次數排序並限制結果數量
        videos.sort(key=lambda x: int(x['viewCount']), reverse=True)
        videos = videos[:max_results]  # 確保返回請求的結果數量
        
        print(f"✅ 篩選後獲得 {len(videos)} 個符合條件的影片")

        # 如果結果數量不足，嘗試放寬條件
        if len(videos) < max_results // 2:  # 如果結果少於要求的一半，啟動放寬模式
            print(f"🔄 結果數量 {len(videos)} 少於要求的一半，嘗試放寬搜尋條件...")
            
            # 嘗試放寬長度限制，但保持最低觀看次數要求
            relaxed_videos = []
            for item in all_video_items:
                video_data = item['snippet']
                statistics = item['statistics']
                content_details = item['contentDetails']
                
                # 仍然檢查觀看次數，但放寬長度限制
                view_count = int(statistics.get('viewCount', 0))
                if view_count < min_views:
                    continue  # 跳過觀看次數不足的影片
                
                category_id = video_data.get('categoryId', '')
                category_name = get_category_name(category_id, categories)
                
                video_info = {
                    'videoId': item['id'],
                    'title': video_data['title'],
                    'description': video_data['description'],
                    'channelTitle': video_data['channelTitle'],
                    'channelId': video_data['channelId'],
                    'publishedAt': video_data['publishedAt'],
                    'thumbnails': video_data['thumbnails'],
                    'categoryId': category_id,
                    'categoryName': category_name,
                    'defaultLanguage': video_data.get('defaultLanguage', ''),
                    'defaultAudioLanguage': video_data.get('defaultAudioLanguage', ''),
                    'tags': video_data.get('tags', []),
                    'viewCount': statistics.get('viewCount', '0'),
                    'likeCount': statistics.get('likeCount', '0'),
                    'commentCount': statistics.get('commentCount', '0'),
                    'duration': content_details.get('duration', ''),
                    'definition': content_details.get('definition', ''),
                    'caption': content_details.get('caption', ''),
                    'licensedContent': content_details.get('licensedContent', False),
                    'projection': content_details.get('projection', ''),
                    'url': f"https://www.youtube.com/watch?v={item['id']}",
                    'formattedViewCount': format_view_count(statistics.get('viewCount', '0')),
                    'formattedDuration': format_duration(content_details.get('duration', ''))
                }
                relaxed_videos.append(video_info)
            
            relaxed_videos.sort(key=lambda x: int(x['viewCount']), reverse=True)
            
            # 確保返回請求的結果數量
            relaxed_videos.sort(key=lambda x: int(x['viewCount']), reverse=True)
            relaxed_videos = relaxed_videos[:max_results]  # 限制放寬模式的結果數量
            
            if relaxed_videos:
                print(f"✅ 放寬條件後找到 {len(relaxed_videos)} 個影片")
                
                # 合併原有結果和放寬條件的結果
                existing_ids = {v['videoId'] for v in videos}
                additional_videos = [v for v in relaxed_videos if v['videoId'] not in existing_ids]
                combined_videos = videos + additional_videos
                combined_videos = combined_videos[:max_results]  # 確保不超過請求數量
                
                # 儲存合併後的結果
                last_search_results = combined_videos.copy()
                
                # 使用真實的配額追蹤
                quota_info = get_current_quota_info()
                quota_info['video_count'] = len(combined_videos)
                
                return jsonify({
                    'success': True,
                    'videos': combined_videos,
                    'totalResults': len(combined_videos),
                    'relaxed': True,
                    'message': f'已放寬長度限制，找到 {len(combined_videos)} 個影片',
                    'quota_info': quota_info,
                    'can_export': len(combined_videos) > 0
                })
        
        # 根據觀看次數排序
        videos.sort(key=lambda x: int(x['viewCount']), reverse=True)
        
        # 如果沒有找到影片，嘗試放寬條件
        if len(videos) == 0 and (min_views > 0 or max_duration != 'all' or time_filter != 'all'):
            print("🔄 沒有找到符合條件的影片，嘗試放寬搜尋條件...")
            
            # 重新搜尋，放寬條件
            relaxed_params = search_params.copy()
            if 'publishedAfter' in relaxed_params:
                del relaxed_params['publishedAfter']  # 移除時間限制
            
            relaxed_response = youtube.search().list(**relaxed_params).execute()
            
            relaxed_video_ids = []
            for item in relaxed_response['items']:
                relaxed_video_ids.append(item['id']['videoId'])
            
            if relaxed_video_ids:
                relaxed_videos_response = youtube.videos().list(
                    part='snippet,statistics,contentDetails',
                    id=','.join(relaxed_video_ids)
                ).execute()
                
                for item in relaxed_videos_response['items']:
                    video_data = item['snippet']
                    statistics = item['statistics']
                    content_details = item['contentDetails']
                    
                    # 只檢查長度限制，放寬觀看次數要求
                    if max_duration != 'all':
                        duration_seconds = get_duration_seconds(content_details.get('duration', ''))
                        max_duration_seconds = int(max_duration)
                        if duration_seconds > max_duration_seconds:
                            continue
                    
                    video_info = {
                        'videoId': item['id'],
                        'title': video_data['title'],
                        'description': video_data['description'],
                        'channelTitle': video_data['channelTitle'],
                        'channelId': video_data['channelId'],
                        'publishedAt': video_data['publishedAt'],
                        'thumbnails': video_data['thumbnails'],
                        'categoryId': video_data.get('categoryId', ''),
                        'defaultLanguage': video_data.get('defaultLanguage', ''),
                        'defaultAudioLanguage': video_data.get('defaultAudioLanguage', ''),
                        'tags': video_data.get('tags', []),
                        'viewCount': statistics.get('viewCount', '0'),
                        'likeCount': statistics.get('likeCount', '0'),
                        'commentCount': statistics.get('commentCount', '0'),
                        'duration': content_details.get('duration', ''),
                        'definition': content_details.get('definition', ''),
                        'caption': content_details.get('caption', ''),
                        'licensedContent': content_details.get('licensedContent', False),
                        'projection': content_details.get('projection', ''),
                        'url': f"https://www.youtube.com/watch?v={item['id']}",
                        'formattedViewCount': format_view_count(statistics.get('viewCount', '0')),
                        'formattedDuration': format_duration(content_details.get('duration', ''))
                    }
                    videos.append(video_info)
                
                videos.sort(key=lambda x: int(x['viewCount']), reverse=True)
                
                return jsonify({
                    'success': True,
                    'videos': videos,
                    'totalResults': len(videos),
                    'relaxed': True,
                    'message': '已放寬搜尋條件以顯示更多結果'
                })
        
        # 儲存搜尋結果以供匯出使用
        last_search_results = videos.copy()
        
        # 使用真實的配額追蹤
        quota_info = get_current_quota_info()
        quota_info['video_count'] = len(videos)  # 更新影片數量
        
        return jsonify({
            'success': True,
            'videos': videos,
            'totalResults': len(videos),
            'quota_info': quota_info,
            'can_export': len(videos) > 0
        })
    
    except ValueError as ve:
        return jsonify({'error': str(ve)}), 400
    except Exception as e:
        error_msg = str(e)
        if 'API key not valid' in error_msg:
            return jsonify({
                'error': 'API Key 無效',
                'details': [
                    '請檢查以下項目：',
                    '1. API Key 格式正確 (以 AIzaSy 開頭，39字符)',
                    '2. 已在 Google Cloud Console 啟用 YouTube Data API v3',
                    '3. API Key 有正確的權限設定',
                    '4. 未超過每日配額限制'
                ]
            }), 400
        elif 'quotaExceeded' in error_msg:
            return jsonify({'error': 'API 配額已用完，請明天再試或升級配額'}), 429
        else:
            return jsonify({'error': f'搜尋失敗: {error_msg}'}), 500

@app.route('/export_csv', methods=['GET'])
def export_csv():
    """匯出CSV檔案"""
    try:
        global last_search_results, last_search_params
        
        if not last_search_results:
            return jsonify({'error': '沒有可匯出的搜尋結果'}), 400
        
        print(f"📊 開始匯出CSV，共 {len(last_search_results)} 筆資料")
        print(f"🔍 搜尋參數: {last_search_params}")  # 調試用
        
        # 準備CSV數據 - 使用 BytesIO 和 UTF-8 編碼
        from io import BytesIO
        output = BytesIO()
        
        # 寫入 UTF-8 BOM，讓 Excel 能正確識別編碼
        output.write('\ufeff'.encode('utf-8'))
        
        # 寫入標題行
        headers = [
            '影片ID', '影片標題', '頻道名稱', '頻道ID', '影片類別', '上傳時間',
            '觀看次數', '按讚數', '留言數', '影片長度', '畫質', '字幕', 
            '授權內容', '影片連結', '影片描述', '標籤'
        ]
        
        # 建立 CSV 行
        csv_lines = []
        csv_lines.append(','.join([f'"{h}"' for h in headers]))
        
        # 寫入數據行
        for video in last_search_results:
            try:
                # 處理時間格式
                try:
                    published_date = datetime.fromisoformat(video['publishedAt'].replace('Z', '+00:00'))
                    formatted_date = published_date.strftime('%Y-%m-%d %H:%M:%S')
                except:
                    formatted_date = video['publishedAt']
                
                # 處理標籤
                tags_str = ', '.join(video.get('tags', [])) if video.get('tags') else '無'
                
                # 清理描述文字中的換行符和特殊字符
                description = video['description'].replace('\n', ' ').replace('\r', ' ').replace('"', '""')
                if len(description) > 500:
                    description = description[:500] + '...'
                
                # 清理標題中的特殊字符
                title = video['title'].replace('"', '""')
                channel_title = video['channelTitle'].replace('"', '""')
                
                row_data = [
                    video['videoId'],
                    title,
                    channel_title,
                    video['channelId'],
                    video.get('categoryName', '未知'),
                    formatted_date,
                    str(int(video['viewCount'])),
                    str(int(video['likeCount'])),
                    str(int(video['commentCount'])),
                    video['formattedDuration'],
                    video['definition'],
                    '有' if video['caption'] == 'true' else '無',
                    '是' if video['licensedContent'] else '否',
                    video['url'],
                    description,
                    tags_str
                ]
                
                # 將每個欄位包裹在引號中以處理逗號和特殊字符
                csv_line = ','.join([f'"{field}"' for field in row_data])
                csv_lines.append(csv_line)
            except Exception as e:
                print(f"⚠️ 處理影片 {video.get('videoId', 'unknown')} 時發生錯誤: {e}")
                continue
        
        # 寫入所有行
        csv_content = '\n'.join(csv_lines)
        output.write(csv_content.encode('utf-8'))
        
        # 準備下載
        output.seek(0)
        
        # 根據搜尋條件生成檔案名稱（改為 CSV）
        filename = generate_csv_filename(last_search_params)
        
        print(f"✅ CSV檔案生成成功: {filename}，共 {len(csv_lines)-1} 筆資料")
        
        # 創建響應 - 使用 send_file 處理二進制數據
        from flask import send_file
        from urllib.parse import quote
        
        output.seek(0)
        
        # URL 編碼檔名以支援中文
        encoded_filename = quote(filename)
        
        return send_file(
            output,
            mimetype='text/csv',
            as_attachment=True,
            download_name=filename
        )
        
    except Exception as e:
        print(f"❌ CSV匯出錯誤: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': f'匯出失敗: {str(e)}'}), 500

if __name__ == '__main__':
    print("=" * 50)
    print("YouTube 熱門影片搜尋器")
    print("=" * 50)
    
    api_key = get_api_key()
    
    if not api_key or api_key == 'your_youtube_api_key_here':
        print("❌ 錯誤: 請在 .env 檔案中設定您的 YouTube API Key")
        print("📝 步驟:")
        print("   1. 前往 https://console.cloud.google.com/")
        print("   2. 建立或選擇專案")
        print("   3. 啟用 YouTube Data API v3")
        print("   4. 建立憑證 > API Key")
        print("   5. 編輯 .env 檔案: YOUTUBE_API_KEY=您的API金鑰")
        print()
    elif not api_key.startswith('AIzaSy') or len(api_key) != 39:
        print(f"⚠️  警告: API Key 格式可能不正確")
        print(f"   目前的 Key: {api_key[:10]}...")
        print(f"   YouTube API Key 應該以 'AIzaSy' 開頭且長度為 39 字符")
        print()
    else:
        print("✅ API Key 格式看起來正確")
        print()
    
    print("🚀 啟動伺服器...")
    app.run(debug=True, host='0.0.0.0', port=5000)