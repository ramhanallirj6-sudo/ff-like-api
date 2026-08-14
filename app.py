from flask import Flask, request, jsonify
import json
import random
import os
from datetime import datetime, date

app = Flask(__name__)

# ============ CONFIGURATION ============
VALID_API_KEYS = {
    "Anurag"
}

daily_limit = 20
used_count = 0
last_reset_date = str(date.today())

# ============ LOAD TOKENS ============
def load_tokens(region):
    """Load tokens from region-specific file"""
    region_lower = region.lower()
    
    if region_lower in ['bd', 'pak', 'ind', 'af', 'npl']:
        token_file = 'token_bd.json'
    elif region_lower in ['br', 'us', 'na', 'sac']:
        token_file = 'token_br.json'
    else:
        token_file = 'token_bd.json'
    
    try:
        with open(token_file, 'r') as f:
            tokens = json.load(f)
            if tokens:
                return tokens[0]['token']
    except:
        pass
    
    return None

# ============ HELPER FUNCTIONS ============
def reset_daily_limit():
    """Reset daily limit at midnight"""
    global used_count, last_reset_date
    today = str(date.today())
    if today != last_reset_date:
        used_count = 0
        last_reset_date = today

def encrypt_message(plaintext):
    """Encrypt message using AES"""
    from Crypto.Cipher import AES
    from Crypto.Util.Padding import pad
    import base64
    
    key = b'Yg&tc%DEuh6%Zc^8'
    iv = b'6oyZDr22E3ychjM%'
    
    cipher = AES.new(key, AES.MODE_CBC, iv)
    padded = pad(plaintext.encode(), 16)
    encrypted = cipher.encrypt(padded)
    return base64.b64encode(encrypted).decode()

def create_protobuf_message(user_id, region):
    """Create protobuf message for API"""
    try:
        import like_pb2
        message = like_pb2.like()
        message.uid = int(user_id)
        message.region = region
        return message.SerializeToString()
    except:
        return None

# ============ API ENDPOINTS ============
@app.route('/like', methods=['GET'])
def handle_requests():
    """Handle like requests"""
    reset_daily_limit()
    
    global used_count
    
    # Get parameters
    uid = request.args.get('uid')
    region = request.args.get('region', 'BD').upper()
    api_key = request.args.get('key')
    
    # Validate
    if not uid or not region:
        return jsonify({"error": "UID and region are required"}), 400
    
    if api_key not in VALID_API_KEYS:
        return jsonify({"error": "Invalid or missing API key"}), 401
    
    if not uid.isdigit():
        return jsonify({"error": "Invalid UID format"}), 400
    
    # Check daily limit
    if used_count >= daily_limit:
        return jsonify({
            "status": 2,
            "error": "Daily limit reached",
            "daily_limit": daily_limit,
            "used": used_count,
            "remaining": 0
        })
    
    # Load token
    token = load_tokens(region)
    if not token:
        return jsonify({"error": "Failed to load tokens"}), 500
    
    # Simulate like sending
    try:
        uid_int = int(uid)
        
        # Mock player data
        player_names = ["ProGamer", "ElitePlayer", "MasterMind", "ShadowLord", "FaduuLike", "bd_King"]
        player = random.choice(player_names)
        level = random.randint(30, 50)
        before_likes = random.randint(100, 1000)
        likes_given = 1
        after_likes = before_likes + likes_given
        
        used_count += 1
        
        response = {
            "status": 1,
            "LikesGivenByAPI": likes_given,
            "LikesafterCommand": after_likes,
            "LikesbeforeCommand": before_likes,
            "PlayerNickname": player,
            "Level": level,
            "Region": region,
            "UID": uid_int,
            "daily_limit": daily_limit,
            "used": used_count,
            "remaining": daily_limit - used_count
        }
        
        return jsonify(response)
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/remain', methods=['GET'])
def remain_info():
    """Get remaining likes info"""
    reset_daily_limit()
    
    return jsonify({
        "daily_limit": daily_limit,
        "used": used_count,
        "remaining": daily_limit - used_count,
        "reset_info": "4:00 AM IST (Midnight reset)"
    })

@app.route('/status', methods=['GET'])
def status():
    """Get bot status"""
    return jsonify({
        "status": "online",
        "version": "1.0",
        "region": "BD",
        "timestamp": datetime.now().isoformat()
    })

@app.errorhandler(404)
def not_found(e):
    return jsonify({"error": "Endpoint not found"}), 404

@app.errorhandler(500)
def server_error(e):
    return jsonify({"error": "Internal server error"}), 500

# ============ MAIN ============
if __name__ == '__main__':
    print("🚀 Free Fire Like API Server Starting...")
    print("📍 Region: Bangladesh (BD)")
    print("⚙️ Running on http://127.0.0.1:5000")
    print("✅ API ready for Telegram Bot")
    app.run(debug=True, use_reloader=False, host='127.0.0.1', port=5000)
