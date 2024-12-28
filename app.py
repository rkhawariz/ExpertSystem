import os
from os.path import join, dirname
from dotenv import load_dotenv
from flask import Flask, render_template, request, jsonify, url_for, redirect

from datetime import datetime, timedelta
from bson import ObjectId
import hashlib
import jwt
import requests
from bson.objectid import ObjectId

from pymongo import MongoClient
import requests

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

@app.route('/diagnosaStart')
def diagnosaStart():
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
        return render_template('diagnosaStart.html', user_info=user_info, logged_in = logged_in, is_admin = is_admin)
    except jwt.ExpiredSignatureError:
        msg = 'Your token has expired'
    except jwt.exceptions.DecodeError:
        msg = 'There was a problem logging you in'
    return render_template('diagnosaStart.html', msg=msg)
  
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
        payload =jwt.decode(
            token_receive,
            SECRET_KEY,
            algorithms=['HS256']
        )
        user_info = db.users.find_one({"email": payload["id"]})
        is_admin = user_info.get("category") == "admin"
        logged_in = True
        return render_template('kelolaDiagnosa.html', user_info=user_info, logged_in = logged_in, is_admin = is_admin)
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
                return redirect('/')  # Arahkan ke halaman lain jika bukan admin
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
    return render_template('kelolaGejala.html', msg=msg)

@app.route('/kelolaPenyakitSave', methods=['POST'])
def tambahPenyakitSave():
    data = request.get_json()
    if not data or "penyakit" not in data or not data["penyakit"]:
        return jsonify({"message": "Data penyakit tidak valid."}), 400

    try:
        kode_penyakit = data["kode_penyakit"]
        penyakit = data["penyakit"]
        definisi = data["definisi"]

        db.penyakit.insert_one({"kode_penyakit": kode_penyakit, "penyakit": penyakit, "definisi": definisi})
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
        penyakit = data.get('penyakit', '').strip()
        definisi = data.get('definisi', '').strip()

        if not kode_penyakit or not penyakit:
            return jsonify({"message": "Kode penyakit dan nama penyakit tidak boleh kosong"}), 400

        result = db.penyakit.update_one(
            {"kode_penyakit": kode_penyakit},
            {"$set": {"penyakit": penyakit, "definisi": definisi}}
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
                return redirect('/')  # Arahkan ke halaman lain jika bukan admin
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

@app.route('/kelolaAnjuran')
def kelolaAnjuran():
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
        return render_template('kelolaAnjuran.html', user_info=user_info, logged_in = logged_in, is_admin = is_admin)
    except jwt.ExpiredSignatureError:
        msg = 'Your token has expired'
    except jwt.exceptions.DecodeError:
        msg = 'There was a problem logging you in'
    return render_template('kelolaAnjuran.html', msg=msg)

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
        return render_template('kelolaPengetahuan.html', user_info=user_info, logged_in = logged_in, is_admin = is_admin)
    except jwt.ExpiredSignatureError:
        msg = 'Your token has expired'
    except jwt.exceptions.DecodeError:
        msg = 'There was a problem logging you in'
    return render_template('kelolaPengetahuan.html', msg=msg)

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
