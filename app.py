import os
from os.path import join, dirname
from dotenv import load_dotenv
from flask import Flask, render_template, request, jsonify, url_for, redirect, make_response, render_template_string

from datetime import datetime, timedelta
from bson import ObjectId
import hashlib
import jwt
import requests
from bson.objectid import ObjectId

from pymongo import MongoClient
import requests

from weasyprint import HTML

dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)

MONGODB_URI = os.environ.get("MONGODB_URI")
DB_NAME =  os.environ.get("DB_NAME")

client = MongoClient(MONGODB_URI)

db = client[DB_NAME]

app = Flask(__name__)

SECRET_KEY = 'merzy'
TOKEN_KEY = 'mytoken'


@app.route('/', methods = ['GET'])
def main():
    token_receive = request.cookies.get(TOKEN_KEY)
    try:
        payload =jwt.decode(
            token_receive,
            SECRET_KEY,
            algorithms=['HS256']
        )
        user_info = db.users.find_one({"email": payload["id"]})
        is_admin = user_info.get("category") == "admin"
        logged_in = True
        print(user_info)
        return render_template('index.html', user_info=user_info, logged_in = logged_in, is_admin = is_admin)
    except jwt.ExpiredSignatureError:
        msg = 'Your token has expired'
    except jwt.exceptions.DecodeError:
        msg = 'There was a problem logging you in'
    return render_template('index.html', msg=msg)

@app.route('/login')
def login():
    return render_template('login.html')
  
@app.route('/login_save', methods=['POST'])
def login_save():
    email = request.form["email"]
    password = request.form["password"]
    pw_hash = hashlib.sha256(password.encode("utf-8")).hexdigest()
    result = db.users.find_one(
        {
            "email": email,
            "password": pw_hash,
        }
    )
    
    if result:
        payload = {
            "id": email,
            "exp": datetime.utcnow() + timedelta(seconds=60 * 60 * 24),
        }
        token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")

        # Tentukan URL redirect berdasarkan kategori user
        redirect_url = "/berandaAdmin" if result.get("category") == "admin" else "/"
        
        return jsonify(
            {
                "result": "success",
                "token": token,
                "redirect_url": redirect_url,
            }
        )
    else:
        return jsonify(
            {
                "result": "fail",
                "msg": "We could not find a user with that id/password combination",
            }
        )

@app.route('/register')
def register():
    return render_template('register.html')
  
@app.route('/register/save', methods = ['POST'])
def register_save():
    name = request.form.get('name')
    age = request.form.get('age')
    gender = request.form.get('gender')
    email = request.form.get('email')
    password = request.form.get('password')
    password_hash = hashlib.sha256(password. encode('utf-8')).hexdigest()
    doc = {
        "name" : name,
        "age" : age,
        "gender" : gender,
        "email" : email,
        "category" : 'pasien',
        "password" : password_hash                                          
    }
    db.users.insert_one(doc)
    return jsonify({'result': 'success'})
  
@app.route('/artikel')
def artikel():
    token_receive = request.cookies.get(TOKEN_KEY)
    try:
        payload =jwt.decode(
            token_receive,
            SECRET_KEY,
            algorithms=['HS256']
        )
        user_info = db.users.find_one({"email": payload["id"]})
        is_admin = user_info.get("category") == "admin"
        logged_in = True
        return render_template('artikel.html', user_info=user_info, logged_in = logged_in, is_admin = is_admin)
    except jwt.ExpiredSignatureError:
        msg = 'Your token has expired'
    except jwt.exceptions.DecodeError:
        msg = 'There was a problem logging you in'
    return render_template('artikel.html', msg=msg)

@app.route('/about')
def about():
    token_receive = request.cookies.get(TOKEN_KEY)
    try:
        payload =jwt.decode(
            token_receive,
            SECRET_KEY,
            algorithms=['HS256']
        )
        user_info = db.users.find_one({"email": payload["id"]})
        is_admin = user_info.get("category") == "admin"
        logged_in = True
        return render_template('about.html', user_info=user_info, logged_in = logged_in, is_admin = is_admin)
    except jwt.ExpiredSignatureError:
        msg = 'Your token has expired'
    except jwt.exceptions.DecodeError:
        msg = 'There was a problem logging you in'
    return render_template('about.html', msg=msg)

@app.route('/halamanDiagnosa', methods=['GET'])
def halamanDiagnosa():
    token_receive = request.cookies.get(TOKEN_KEY)  # Ambil token dari cookie
    if not token_receive:
        return render_template('halamanDiagnosa.html', msg="Token tidak ditemukan. Silakan login kembali.")
    
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        user_info = db.users.find_one({"email": payload["id"]})
        is_admin = user_info.get("category") == "admin"
        logged_in = True
        return render_template(
            'halamanDiagnosa.html',
            user_info=user_info,
            logged_in=logged_in,
            is_admin=is_admin
        )
    except jwt.ExpiredSignatureError:
        return render_template('halamanDiagnosa.html', msg="Sesi login Anda telah berakhir. Silakan login kembali.")
    except jwt.exceptions.DecodeError:
        return render_template('halamanDiagnosa.html', msg="Token tidak valid. Silakan login kembali.")


@app.route('/get-gejala-diagnosa', methods=['GET'])
def get_gejala_diagnosa():
    gejalaList = list(db.gejala.find({}, {'_id': 0, 'kode_gejala': 1, 'gejala': 1})) 
    return jsonify({"gejalaList": gejalaList}), 200

def inference_engine(jawaban):
    # print("Jawaban diterima oleh inference_engine:", jawaban)
    rules = list(db.rules.find())
    fakta = {item['kode_gejala']: item['answer'] for item in jawaban}

    for rule in rules:
        if all(fakta.get(gejala) == "Ya" for gejala in rule["if_gejala"]):
            penyakit_data = db.penyakit.find_one({"kode_penyakit": rule["then_penyakit"]["penyakit"]})
            anjuran_data = db.anjuran.find_one({"kode_anjuran": rule["then_penyakit"]["anjuran"]})
            
            return {
                "penyakit": f"{rule['then_penyakit']['penyakit']} - {penyakit_data['namaPenyakit']}",
                "anjuran": f"{rule['then_penyakit']['anjuran']} - {anjuran_data['deskripsiAnjuran']}"
            }
    return {"penyakit": "Tidak ada diagnosis yang cocok.", "anjuran": "N/A"}


@app.route('/save-diagnosa', methods=['POST'])
def save_diagnosa():
    try:
        token_receive = request.headers.get('Authorization')
        if token_receive:
            token_receive = token_receive.split(" ")[1]
        else:
            return jsonify({"error": "Token tidak ditemukan"}), 401

        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        user_info = db.users.find_one({"email": payload["id"]})
        data = request.json

        jawaban = data.get("jawaban")
        if not jawaban:
            return jsonify({"error": "Jawaban tidak ditemukan dalam permintaan"}), 400

        hasil_diagnosa = inference_engine(jawaban)

        diagnosa = {
            "user_id": user_info["_id"],
            "user_name": user_info["name"],
            "user_email": user_info["email"],
            "user_age": user_info["age"],
            "user_gender": user_info["gender"],
            "tanggal_diagnosa": datetime.now().strftime('%Y-%m-%d'),
            "jawaban": jawaban,
            "hasil_diagnosa": hasil_diagnosa
        }

        db.diagnosa.insert_one(diagnosa)
        return jsonify({"msg": "Diagnosa berhasil disimpan!", "diagnosa_id": str(diagnosa["_id"])})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/hasil-diagnosa', methods=['GET'])
def hasil_diagnosa():
    diagnosa_id = request.args.get('id')
    if not diagnosa_id:
        return "ID diagnosa tidak ditemukan", 400

    try:
        token_receive = request.cookies.get(TOKEN_KEY)  # Ambil token dari cookie
        if not token_receive:
            return redirect(url_for('login', msg="Silakan login terlebih dahulu."))

        # Decode token
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=["HS256"])
        user_info = db.users.find_one({"email": payload["id"]})
        if not user_info:
            return redirect(url_for('login', msg="Pengguna tidak ditemukan."))

        is_admin = user_info.get("category") == "admin"
        logged_in = True

        # Temukan diagnosa berdasarkan ID
        diagnosa = db.diagnosa.find_one({"_id": ObjectId(diagnosa_id)})
        if not diagnosa:
            return "Diagnosa tidak ditemukan", 404
        
        gejala_list = list(db.gejala.find())
        
        gejala_dialami = [
            gejala["gejala"]  # Ambil deskripsi gejala
            for jawaban in diagnosa["jawaban"]
            if jawaban["answer"] == "Ya"  # Jawaban "Ya"
            for gejala in gejala_list
            if gejala["kode_gejala"] == jawaban["kode_gejala"]  # Kode cocok
        ]

        # Render halaman hasil diagnosa dengan informasi pengguna
        return render_template(
            'hasilDiagnosa.html',
            diagnosa=diagnosa,
            gejala_dialami=gejala_dialami,
            user_info=user_info,
            logged_in=logged_in,
            is_admin=is_admin
        )
    except jwt.ExpiredSignatureError:
        return redirect(url_for('login', msg="Sesi login Anda telah berakhir."))
    except jwt.exceptions.DecodeError:
        return redirect(url_for('login', msg="Token tidak valid."))
    except Exception as e:
        return f"Terjadi kesalahan: {e}", 500
    
# @app.route('/cetak-pdf', methods=['GET'])
# def cetak_pdf():
#     diagnosa_id = request.args.get('id')
#     if not diagnosa_id:
#         return "ID diagnosa tidak ditemukan", 400

#     diagnosa = db.diagnosa.find_one({"_id": ObjectId(diagnosa_id)})
#     if not diagnosa:
#         return "Diagnosa tidak ditemukan", 404

#     # Gejala yang dialami
#     gejala_dialami = []
#     for item in diagnosa["jawaban"]:
#         if item["answer"] == "Ya":
#             gejala_data = db.gejala.find_one({"kode_gejala": item["kode_gejala"]})
#             if gejala_data and "gejala" in gejala_data:
#                 gejala_dialami.append(gejala_data["gejala"])

#     # Render hasil template ke dalam PDF
#     html_template = render_template(
#         "hasilDiagnosa.html", diagnosa=diagnosa, gejala_dialami=gejala_dialami
#     )

#     try:
#         pdf = HTML(string=html_template).write_pdf()
#     except Exception as e:
#         return f"Error saat menghasilkan PDF: {str(e)}", 500

#     response = make_response(pdf)
#     response.headers["Content-Type"] = "application/pdf"
#     response.headers["Content-Disposition"] = f"attachment; filename=hasil_diagnosa_{diagnosa_id}.pdf"
#     return response


@app.route('/cetak-pdf', methods=['GET'])
def cetak_pdf():
    diagnosa_id = request.args.get('id')
    if not diagnosa_id:
        return "ID diagnosa tidak ditemukan", 400

    diagnosa = db.diagnosa.find_one({"_id": ObjectId(diagnosa_id)})
    if not diagnosa:
        return "Diagnosa tidak ditemukan", 404

    gejala_dialami = []
    for gejala in diagnosa['jawaban']:
        if gejala['answer'] == 'Ya':
            gejala_dialami.append(gejala['kode_gejala'])

    # HTML template yang sama seperti di halaman web
    html_template = f"""
<html>
<head>
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bulma@1.0.2/css/bulma.min.css">
    <style>
        body {{
            font-family: 'Arial', sans-serif;
            margin: 0;
            padding: 20px;
            background-color: #f8f9fa;
        }}
        .container {{
            background: #ffffff;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
        }}
        .title {{
            color: #40513B;
            font-size: 28px;
            font-weight: bold;
        }}
        .subtitle {{
            color: #6c757d;
            font-size: 18px;
            margin-bottom: 20px;
        }}
        .content {{
            margin: 20px 0;
        }}
        .columns {{
            display: flex;
            justify-content: space-between;
        }}
        .box {{
            border: 1px solid #dee2e6;
            border-radius: 5px;
            padding: 15px;
            margin-top: 15px;
        }}
        .has-text-warning {{
            color: #FFA500;
            font-weight: bold;
        }}
        .has-text-danger {{
            color: #DC3545;
            font-weight: bold;
        }}
        .has-text-centered {{
            text-align: center;
        }}
        .divider {{
            height: 3px;
            background: linear-gradient(to right, #40513B, #6c757d);
            border: none;
            margin: 20px 0;
        }}
        .footer {{
            text-align: center;
            margin-top: 40px;
            font-size: 14px;
            color: #6c757d;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="content has-text-centered">
            <h1 class="title">Hasil Diagnosa</h1>
            <p class="subtitle">Detail hasil diagnosa dan rekomendasi untuk Anda</p>
            <hr class="divider">
        </div>

        <div class="content">
            <h2 class="title is-5">Informasi Pasien</h2>
            <div class="columns">
                <div class="column">
                    <p><strong>Nama Pasien:</strong><br> {diagnosa['user_name']}</p>
                    <p><strong>Email:</strong><br> {diagnosa['user_email']}</p>
                </div>
                <div class="column">
                    <p><strong>Rentang Usia:</strong><br> {diagnosa['user_age']}</p>
                    <p><strong>Jenis Kelamin:</strong><br> {diagnosa['user_gender']}</p>
                </div>
                <div class="column">
                    <p><strong>Tanggal Diagnosa:</strong><br> {diagnosa['tanggal_diagnosa']}</p>
                    <p><strong>LambungHealth<sup>+</sup> <br> at Klinik Alyssa Medika</strong></p>
                </div>
            </div>
            <hr class="divider">
        </div>

        <div class="content">
            <h2 class="title is-5">Hasil Diagnosa</h2>
            <div class="box">
                <p><strong>Penyakit:</strong> <span class="has-text-danger">{diagnosa['hasil_diagnosa']['penyakit']}</span></p>
                <p><strong>Anjuran:</strong></p>
                <div class="content has-text-justified is-small has-background-white p-3">
                    {diagnosa['hasil_diagnosa']['anjuran']}
                </div>
            </div>
        </div>

        <div class="footer">
            <p>© 2025 LambungHealth<sup>+</sup></p>
            <p>at Klinik Alyssa Medika</p>
        </div>
    </div>
</body>
</html>
"""

    try:
        pdf = HTML(string=html_template).write_pdf()
    except Exception as e:
        return f"Error saat menghasilkan PDF: {str(e)}", 500

    response = make_response(pdf)
    response.headers["Content-Type"] = "application/pdf"
    response.headers["Content-Disposition"] = f"attachment; filename=hasil_diagnosa_{diagnosa_id}.pdf"
    return response

@app.route('/riwayatDiagnosa')
def riwayatDiagnosa():
    token_receive = request.cookies.get(TOKEN_KEY)
    try:
        payload =jwt.decode(
            token_receive,
            SECRET_KEY,
            algorithms=['HS256']
        )
        user_info = db.users.find_one({"email": payload["id"]})
        is_admin = user_info.get("category") == "admin"
        logged_in = True
        print(user_info)
        return render_template('riwayatDiagnosa.html', user_info=user_info, logged_in = logged_in, is_admin = is_admin)
    except jwt.ExpiredSignatureError:
        msg = 'Your token has expired'
    except jwt.exceptions.DecodeError:
        msg = 'There was a problem logging you in'
    return render_template('index.html', msg=msg)

@app.route('/editProfilPasien', methods=["GET"])
def editProfilPasien():
    token_receive = request.cookies.get(TOKEN_KEY)
    try:
        payload = jwt.decode(
            token_receive,
            SECRET_KEY,
            algorithms=['HS256']
        )
        user_info = db.users.find_one({"email": payload["id"]})
        is_admin = user_info.get("category") == "admin"
        logged_in = True

        # Mengambil riwayat diagnosa pasien berdasarkan ID user
        riwayat = list(db.diagnosa.find({"user_email": user_info["email"]}))
        
        # Kirim data ke template
        return render_template(
            'editProfilPasien.html',
            user_info=user_info,
            logged_in=logged_in,
            is_admin=is_admin,
            riwayat=riwayat
        )
    except jwt.ExpiredSignatureError:
        msg = 'Your token has expired'
    except jwt.exceptions.DecodeError:
        msg = 'There was a problem logging you in'
    return render_template('index.html', msg=msg)


from werkzeug.security import generate_password_hash

@app.route('/updateProfile', methods=['POST'])
def update_profile():
    token_receive = request.cookies.get(TOKEN_KEY)
    try:
        # Decode token to get user information
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        user_email = payload['id']  # Assuming token stores the email
        
        # Get updated data from form
        name = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')
        
        # Prepare update query
        update_data = {"name": name, "email": email}
        if password:
            hashed_password = hashlib.sha256(password. encode('utf-8')).hexdigest()
            update_data["password"] = hashed_password

        # Update user in the database
        db.users.update_one({"email": user_email}, {"$set": update_data})

        return redirect('/editProfilPasien')
    except jwt.ExpiredSignatureError:
        msg = 'Your token has expired'
    except jwt.exceptions.DecodeError:
        msg = 'There was a problem logging you in'
    return render_template('index.html', msg=msg)

@app.route('/updateProfileAdmin', methods=['POST'])
def update_profile_admin():
    token_receive = request.cookies.get(TOKEN_KEY)
    try:
        # Decode token to get user information
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        user_email = payload['id']  # Assuming token stores the email
        
        # Get updated data from form
        name = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')
        
        # Prepare update query
        update_data = {"name": name, "email": email}
        if password:
            hashed_password = hashlib.sha256(password. encode('utf-8')).hexdigest()
            update_data["password"] = hashed_password

        # Update user in the database
        db.users.update_one({"email": user_email}, {"$set": update_data})

        return redirect('/editProfile')
    except jwt.ExpiredSignatureError:
        msg = 'Your token has expired'
    except jwt.exceptions.DecodeError:
        msg = 'There was a problem logging you in'
    return render_template('index.html', msg=msg)

@app.route('/forbidden')
def forbidden():
    return render_template('forbidden.html')

@app.route('/berandaAdmin')
def berandaAdmin():
    token_receive = request.cookies.get(TOKEN_KEY)
    try:
        payload =jwt.decode(
            token_receive,
            SECRET_KEY,
            algorithms=['HS256']
        )
        user_info = db.users.find_one({"email": payload["id"]})
        is_admin = user_info.get("category") == "admin"
        logged_in = True
        if is_admin:
            return render_template(
                "berandaAdmin.html",
                user_info=user_info,
                logged_in=logged_in,
                is_admin=is_admin,
            )
        else:
            return redirect('/forbidden')
        return render_template('berandaAdmin.html', user_info=user_info, logged_in = logged_in, is_admin = is_admin)
    except jwt.ExpiredSignatureError:
        msg = 'Your token has expired'
    except jwt.exceptions.DecodeError:
        msg = 'There was a problem logging you in'
    return render_template('berandaAdmin.html', msg=msg)

@app.route('/kelolaDiagnosa')
def kelolaDiagnosa():
    token_receive = request.cookies.get(TOKEN_KEY)
    try:
        payload = jwt.decode(
            token_receive,
            SECRET_KEY,
            algorithms=['HS256']
        )
        user_info = db.users.find_one({"email": payload["id"]})
        is_admin = user_info.get("category") == "admin"
        logged_in = True

        if request.method == 'GET':
            if not is_admin:
                return redirect('/forbidden')  # Arahkan ke halaman lain jika bukan admin
            diagnosaList = list(db.diagnosa.find())
            return render_template(
                'kelolaDiagnosa.html',
                user_info=user_info,
                logged_in=logged_in,
                is_admin=is_admin,
                diagnosaList=diagnosaList
            )
    except jwt.ExpiredSignatureError:
        msg = 'Your token has expired'
    except jwt.exceptions.DecodeError:
        msg = 'There was a problem logging you in'
    return render_template('kelolaDiagnosa.html', msg=msg)

@app.route('/kelolaPenyakit', methods=['GET'])
def kelolaPenyakit():
    token_receive = request.cookies.get(TOKEN_KEY)
    try:
        payload = jwt.decode(
            token_receive,
            SECRET_KEY,
            algorithms=['HS256']
        )
        user_info = db.users.find_one({"email": payload["id"]})
        is_admin = user_info.get("category") == "admin"
        logged_in = True

        if request.method == 'GET':
            if not is_admin:
                return redirect('/forbidden')  # Arahkan ke halaman lain jika bukan admin
            penyakit = list(db.penyakit.find().sort("kode_penyakit", -1))
            kode_penyakit_terakhir = penyakit[0]["kode_penyakit"] if penyakit else "P00"
            kode_penyakit_baru = f"P{int(kode_penyakit_terakhir[1:]) + 1:02d}"
            return render_template(
                'kelolapenyakit.html',
                user_info=user_info,
                logged_in=logged_in,
                is_admin=is_admin,
                kode_penyakit_baru=kode_penyakit_baru,
                penyakit=penyakit
            )

    except jwt.ExpiredSignatureError:
        msg = 'Your token has expired'
    except jwt.exceptions.DecodeError:
        msg = 'There was a problem logging you in'
    return render_template('kelolaPenyakit.html', msg=msg)

@app.route('/kelolaPenyakitSave', methods=['POST'])
def tambahPenyakitSave():
    data = request.get_json()
    if not data or "namaPenyakit" not in data or not data["namaPenyakit"]:
        return jsonify({"message": "Data penyakit tidak valid."}), 400

    try:
        kode_penyakit = data["kode_penyakit"]
        namaPenyakit = data["namaPenyakit"]
        definisi = data["definisi"]

        db.penyakit.insert_one({"kode_penyakit": kode_penyakit, "namaPenyakit": namaPenyakit, "definisi": definisi})
        return jsonify({"message": "Data penyakit berhasil disimpan."}), 200
    except Exception as e:
        return jsonify({"message": f"Terjadi kesalahan: {str(e)}"}), 500
    
@app.route('/delete_penyakit/<id>', methods=['DELETE'])
def delete_penyakit(id):
    try:
        db.penyakit.delete_one({"_id": ObjectId(id)})
        return jsonify({"message": "berhasil"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
@app.route('/kelolaPenyakitEdit', methods=['PUT'])
def kelolaPenyakitEdit():
    try:
        data = request.get_json()
        kode_penyakit = data.get('kode_penyakit', '').strip()
        namaPenyakit = data.get('namaPenyakit', '').strip()
        definisi = data.get('definisi', '').strip()

        if not kode_penyakit or not namaPenyakit:
            return jsonify({"message": "Kode penyakit dan nama penyakit tidak boleh kosong"}), 400

        result = db.penyakit.update_one(
            {"kode_penyakit": kode_penyakit},
            {"$set": {"namaPenyakit": namaPenyakit, "definisi": definisi}}
        )

        if result.matched_count > 0:
            return jsonify({"message": "Data berhasil diperbarui"}), 200
        else:
            return jsonify({"message": "Kode penyakit tidak ditemukan"}), 404

    except Exception as e:
        return jsonify({"message": f"Terjadi kesalahan: {str(e)}"}), 500

@app.route('/kelolaGejala', methods=['GET'])
def kelolaGejala():
    token_receive = request.cookies.get(TOKEN_KEY)
    try:
        payload = jwt.decode(
            token_receive,
            SECRET_KEY,
            algorithms=['HS256']
        )
        user_info = db.users.find_one({"email": payload["id"]})
        is_admin = user_info.get("category") == "admin"
        logged_in = True

        # Jika metode GET, kembalikan halaman dengan data gejala
        if request.method == 'GET':
            if not is_admin:
                return redirect('/forbidden')  # Arahkan ke halaman lain jika bukan admin
            gejala = list(db.gejala.find().sort("kode_gejala", -1))
            kode_gejala_terakhir = gejala[0]["kode_gejala"] if gejala else "G00"
            kode_gejala_baru = f"G{int(kode_gejala_terakhir[1:]) + 1:02d}"
            return render_template(
                'kelolaGejala.html',
                user_info=user_info,
                logged_in=logged_in,
                is_admin=is_admin,
                kode_gejala_baru=kode_gejala_baru,
                gejala=gejala
            )

    except jwt.ExpiredSignatureError:
        msg = 'Your token has expired'
    except jwt.exceptions.DecodeError:
        msg = 'There was a problem logging you in'
    return render_template('kelolaGejala.html', msg=msg)    

@app.route('/kelolaGejalaSave', methods=['POST'])
def tambahGejalaSave():
    data = request.get_json()
    if not data or "gejala" not in data or not data["gejala"]:
        return jsonify({"message": "Data gejala tidak valid."}), 400

    # Menambahkan data ke database
    try:
        kode_gejala = data["kode_gejala"]
        gejala = data["gejala"]

        db.gejala.insert_one({"kode_gejala": kode_gejala, "gejala": gejala})
        return jsonify({"message": "Data gejala berhasil disimpan."}), 200
    except Exception as e:
        return jsonify({"message": f"Terjadi kesalahan: {str(e)}"}), 500

@app.route('/delete_gejala/<id>', methods=['DELETE'])
def delete_gejala(id):
    try:
        db.gejala.delete_one({"_id": ObjectId(id)})
        return jsonify({"message": "berhasil"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
@app.route('/kelolaGejalaEdit', methods=['PUT'])
def kelolaGejalaEdit():
    try:
        data = request.get_json()
        kode_gejala = data.get('kode_gejala', '').strip()
        gejala = data.get('gejala', '').strip()

        if not kode_gejala or not gejala:
            return jsonify({"message": "Kode gejala dan gejala tidak boleh kosong"}), 400

        result = db.gejala.update_one(
            {"kode_gejala": kode_gejala},
            {"$set": {"gejala": gejala}}
        )

        if result.matched_count > 0:
            return jsonify({"message": "Data berhasil diperbarui"}), 200
        else:
            return jsonify({"message": "Kode gejala tidak ditemukan"}), 404

    except Exception as e:
        return jsonify({"message": f"Terjadi kesalahan: {str(e)}"}), 500

@app.route('/kelolaAnjuran', methods=['GET'])
def kelolaAnjuran():
    token_receive = request.cookies.get(TOKEN_KEY)
    try:
        payload = jwt.decode(
            token_receive,
            SECRET_KEY,
            algorithms=['HS256']
        )
        user_info = db.users.find_one({"email": payload["id"]})
        is_admin = user_info.get("category") == "admin"
        logged_in = True

        if request.method == 'GET':
            if not is_admin:
                return redirect('/forbidden')  # Arahkan ke halaman lain jika bukan admin
            anjuran = list(db.anjuran.find().sort("kode_anjuran", -1))
            kode_anjuran_terakhir = anjuran[0]["kode_anjuran"] if anjuran else "A00"
            kode_anjuran_baru = f"A{int(kode_anjuran_terakhir[1:]) + 1:02d}"
            return render_template(
                'kelolaAnjuran.html',
                user_info=user_info,
                logged_in=logged_in,
                is_admin=is_admin,
                kode_anjuran_baru=kode_anjuran_baru,
                anjuran=anjuran
            )

    except jwt.ExpiredSignatureError:
        msg = 'Your token has expired'
    except jwt.exceptions.DecodeError:
        msg = 'There was a problem logging you in'
    return render_template('kelolaGejala.html', msg=msg)

@app.route('/kelolaAnjuranSave', methods=['POST'])
def tambahAnjuranSave():
    data = request.get_json()
    if not data or "deskripsiAnjuran" not in data or not data["deskripsiAnjuran"]:
        return jsonify({"message": "Data anjuran tidak valid."}), 400

    # Menambahkan data ke database
    try:
        kode_anjuran = data["kode_anjuran"]
        deskripsiAnjuran = data["deskripsiAnjuran"]

        db.anjuran.insert_one({"kode_anjuran": kode_anjuran, "deskripsiAnjuran": deskripsiAnjuran})
        return jsonify({"message": "Data anjuran berhasil disimpan."}), 200
    except Exception as e:
        return jsonify({"message": f"Terjadi kesalahan: {str(e)}"}), 500

@app.route('/delete_anjuran/<id>', methods=['DELETE'])
def delete_anjuran(id):
    try:
        db.anjuran.delete_one({"_id": ObjectId(id)})
        return jsonify({"message": "berhasil"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
@app.route('/kelolaAnjuranEdit', methods=['PUT'])
def kelolaAnjuranEdit():
    try:
        data = request.get_json()
        kode_anjuran = data.get('kode_anjuran', '').strip()
        deskripsiAnjuran = data.get('deskripsiAnjuran', '').strip()

        if not kode_anjuran or not deskripsiAnjuran:
            return jsonify({"message": "Kode anjuran dan deskripsi anjuran tidak boleh kosong"}), 400

        result = db.anjuran.update_one(
            {"kode_anjuran": kode_anjuran},
            {"$set": {"deskripsiAnjuran": deskripsiAnjuran}}
        )

        if result.matched_count > 0:
            return jsonify({"message": "Data berhasil diperbarui"}), 200
        else:
            return jsonify({"message": "Kode gejala tidak ditemukan"}), 404

    except Exception as e:
        return jsonify({"message": f"Terjadi kesalahan: {str(e)}"}), 500

@app.route('/kelolaPengetahuan')
def kelolaPengetahuan():
    token_receive = request.cookies.get(TOKEN_KEY)
    try:
        payload =jwt.decode(
            token_receive,
            SECRET_KEY,
            algorithms=['HS256']
        )
        user_info = db.users.find_one({"email": payload["id"]})
        is_admin = user_info.get("category") == "admin"
        logged_in = True
        if is_admin:
            return render_template(
                "kelolaPengetahuan.html",
                user_info=user_info,
                logged_in=logged_in,
                is_admin=is_admin,
            )
        else:
            return redirect('/forbidden')
    except jwt.ExpiredSignatureError:
        msg = 'Your token has expired'
    except jwt.exceptions.DecodeError:
        msg = 'There was a problem logging you in'
    return render_template('kelolaPengetahuan.html', msg=msg)

@app.route("/getPenyakit", methods=["GET"])
def get_penyakit():
    penyakit = list(db.penyakit.find({}, {"_id": 0}))
    return jsonify(penyakit)

@app.route("/getGejala", methods=["GET"])
def get_gejala():
    gejala = list(db.gejala.find({}, {"_id": 0}))
    return jsonify(gejala)

@app.route("/getAnjuran", methods=["GET"])
def get_anjuran():
    anjuran = list(db.anjuran.find({}, {"_id": 0}))
    return jsonify(anjuran)

@app.route("/addRule", methods=["POST"])
def add_rule():
    data = request.json

    # Validasi input
    if not all(key in data for key in ["penyakit", "gejala", "anjuran"]):
        return jsonify({"message": "Invalid data format!"}), 400

    penyakit = data["penyakit"]
    gejala = data["gejala"]
    anjuran = data["anjuran"]

    # Pastikan gejala adalah list
    if not isinstance(gejala, list):
        return jsonify({"message": "Gejala must be a list!"}), 400

    # Struktur data baru
    rule = {
        "if_gejala": gejala,  # Gejala yang harus terpenuhi
        "then_penyakit": {
            "penyakit": penyakit,  # Kode penyakit
            "anjuran": anjuran  # Kode anjuran
        }
    }

    # Insert rule ke database
    db.rules.insert_one(rule)
    return jsonify({"message": "Rule added successfully!"}), 201


@app.route('/kelolaUser', methods=['GET'])
def kelolaUser():
    token_receive = request.cookies.get(TOKEN_KEY)
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=["HS256"])
        user_info = db.users.find_one({"email": payload["id"]})
        is_admin = user_info.get("category") == "admin"
        logged_in = True
        if is_admin:
            users = db.users.find()
            user_list = []

            for user in users:
                user_lists = {
                    "id": str(user["_id"]),
                    "nama": user["name"],
                    "usia": user["age"],
                    "jenisKelamin": user["gender"],
                    "email": user["email"],
                    'kategori': user['category'],
                }
                user_list.append(user_lists)

            return render_template(
                "kelolaUser.html",
                user_info=user_info,
                logged_in=logged_in,
                is_admin=is_admin,
                users=user_list,
            )
        else:
            return render_template("login.html")
    except jwt.ExpiredSignatureError:
        msg = "Your token has expired"
    except jwt.exceptions.DecodeError:
        msg = "There was a problem logging you in"
    return render_template("login.html", msg=msg)

@app.route('/kelolaUserSave', methods=['POST'])
def kelolaUserSave():
    try:
        data = request.get_json()

        nama = data.get("nama")
        usia = data.get("usia")
        jenis_kelamin = data.get("jenisKelamin")
        email = data.get("email")
        kategori = data.get("kategori")

        user_data = {
            "name": nama,
            "age": usia,
            "gender": jenis_kelamin,
            "email": email,
            "category": kategori
        }
        result = db.users.insert_one(user_data)

        # Mengembalikan response sukses
        return jsonify({
            "message": "Data pengguna berhasil ditambahkan.",
            "id": str(result.inserted_id)
        }), 201

    except Exception as e:
        # Menangani error dan mengembalikan pesan error
        return jsonify({"message": f"Terjadi kesalahan: {str(e)}"}), 500

@app.route('/kelolaUserDelete/<id>', methods=['DELETE'])
def kelolaUserDelete(id):
    try:
        object_id = ObjectId(id)
        
        result = db.users.delete_one({"_id": object_id})
        
        if result.deleted_count > 0:
            return jsonify({"message": "Data berhasil dihapus"}), 200
        else:
            return jsonify({"message": "Data tidak ditemukan"}), 404

    except Exception as e:
        return jsonify({"message": f"Terjadi kesalahan: {str(e)}"}), 500
    
@app.route('/updateUser/<user_id>', methods=['PUT'])
def updateUser(user_id):
    try:
        # Log untuk debug
        print(f"User ID yang diterima: {user_id}")
        data = request.get_json()
        print(f"Data yang diterima: {data}")

        if not data:
            return jsonify({"message": "Data tidak valid."}), 400

        updated_data = {
            "name": data.get("nama"),
            "age": data.get("usia"),
            "gender": data.get("jenisKelamin"),
            "category": data.get("kategori"),
            "email": data.get("email"),
        }

        if "password" in data and data["password"]:
            password = data["password"]
            password_hash = hashlib.sha256(password.encode('utf-8')).hexdigest()
            updated_data["password"] = password_hash

        # Cek apakah user_id valid
        try:
            user_object_id = ObjectId(user_id)
        except Exception as e:
            return jsonify({"message": "User ID tidak valid."}), 400

        # Update data pengguna di database
        result = db.users.update_one({"_id": user_object_id}, {"$set": updated_data})

        # Cek apakah data ditemukan dan diupdate
        if result.matched_count == 0:
            return jsonify({"message": "Pengguna tidak ditemukan."}), 404

        return jsonify({"message": "Data pengguna berhasil diperbarui."}), 200

    except Exception as e:
        print(f"Error: {str(e)}")
        return jsonify({"message": f"Terjadi kesalahan: {str(e)}"}), 500

    
@app.route('/editProfile')
def editProfile():
    token_receive = request.cookies.get(TOKEN_KEY)
    try:
        payload =jwt.decode(
            token_receive,
            SECRET_KEY,
            algorithms=['HS256']
        )
        user_info = db.users.find_one({"email": payload["id"]})
        is_admin = user_info.get("category") == "admin"
        logged_in = True
        return render_template('editProfile.html', user_info=user_info, logged_in = logged_in, is_admin = is_admin)
    except jwt.ExpiredSignatureError:
        msg = 'Your token has expired'
    except jwt.exceptions.DecodeError:
        msg = 'There was a problem logging you in'
    return render_template('editProfile.html', msg=msg)


if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)