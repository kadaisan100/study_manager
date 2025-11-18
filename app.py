import os
from flask import Flask, render_template, request, redirect, url_for, flash
from PIL import Image, ImageDraw
from datetime import datetime

app = Flask(__name__)
app.secret_key = "secret"

# --- データ保存用（簡易版：メモリ上） ---
tasks = []
task_id_counter = 1

# --- アップロード用フォルダ ---
UPLOAD_FOLDER = 'static/uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# --- ルート：トップページ ---
@app.route('/')
def index():
    today = datetime.now().strftime("%Y-%m-%d")
    return render_template(
        'index.html',
        current_date=today,
        tasks=tasks,
        prediction_result=""
    )

# --- ルート：課題追加 ---
@app.route('/add_task', methods=['POST'])
def add_task():
    global task_id_counter
    name = request.form.get('task_name')
    estimated_time = request.form.get('estimated_time', type=int)
    if name and estimated_time:
        tasks.append({
            "id": task_id_counter,
            "name": name,
            "estimated_time": estimated_time,
            "elapsed_time": 0,
            "done": False
        })
        task_id_counter += 1
    return redirect(url_for('index'))

# --- ルート：課題完了 ---
@app.route('/complete_task/<int:task_id>', methods=['POST'])
def complete_task(task_id):
    for task in tasks:
        if task['id'] == task_id:
            task['done'] = True
            break
    return redirect(url_for('index'))

# --- ルート：AI予測（ダミー） ---
@app.route('/predict', methods=['GET'])
def predict():
    prediction = "次の課題にかかる時間は約 45 分です"
    return render_template('index.html', tasks=tasks, prediction_result=prediction, current_date=datetime.now().strftime("%Y-%m-%d"))

# --- ルート：アイコンアップロード（丸くリサイズ） ---
@app.route('/upload_icon', methods=['POST'])
def upload_icon():
    if 'icon_file' not in request.files:
        flash('ファイルが選択されていません')
        return redirect(url_for('index'))
    
    file = request.files['icon_file']
    if file.filename == '':
        flash('ファイル名がありません')
        return redirect(url_for('index'))
    
    if file:
        # 画像を開く
        img = Image.open(file)
        size = (100, 100)
        img = img.resize(size)

        # 丸く切り抜き
        mask = Image.new('L', size, 0)
        draw = ImageDraw.Draw(mask)
        draw.ellipse((0, 0) + size, fill=255)
        output = Image.new('RGBA', size)
        output.paste(img, (0, 0), mask=mask)

        # 保存
        save_path = os.path.join(app.config['UPLOAD_FOLDER'], 'user_icon.png')
        output.save(save_path)

    return redirect(url_for('index'))

# --- 実行 ---
if __name__ == '__main__':
    app.run(debug=True)

