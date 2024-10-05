from flask import Flask, render_template, request, redirect, url_for, flash, session  
from datetime import datetime
import csv
import os
import re

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Path ke folder data
DATA_FOLDER = 'data'
CSV_FILE_PATH = os.path.join(DATA_FOLDER, 'user.csv')
CSV_BUKU_PATH = os.path.join(DATA_FOLDER, 'buku.csv')
CSV_PINJAMAN_PATH = os.path.join(DATA_FOLDER, 'pinjaman.csv')

# Fungsi untuk membaca data buku dari CSV
def read_buku_csv():
    buku_list = []
    if os.path.exists(CSV_BUKU_PATH):
        with open(CSV_BUKU_PATH, mode='r') as file:
            csv_reader = csv.DictReader(file)
            for row in csv_reader:
                if row['is_deleted'] == '0':  
                    buku_list.append(row)
    return buku_list

# Tambahkan fungsi baru untuk membaca data pinjaman
def read_pinjaman_csv():
    pinjaman_list = []
    if os.path.exists(CSV_PINJAMAN_PATH):
        with open(CSV_PINJAMAN_PATH, mode='r') as file:
            csv_reader = csv.DictReader(file)
            for row in csv_reader:
                pinjaman_list.append(row)
    return pinjaman_list

# Fungsi untuk memperbarui status buku
def update_buku_status(judul_buku, status):
    buku_list = read_buku_csv()
    updated_buku_list = []
    
    for buku in buku_list:
        if buku['judul'] == judul_buku:
            buku['status'] = str(status)  # Update status (0 atau 1)
        updated_buku_list.append(buku)

    # Simpan kembali ke CSV
    with open(CSV_BUKU_PATH, mode='w', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=['id', 'judul', 'author', 'status', 'is_deleted'])
        writer.writeheader()
        for buku in updated_buku_list:
            writer.writerow(buku)

# Fungsi untuk memeriksa validasi email
def is_valid_email(email):
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email)

# Fungsi untuk memeriksa validasi password
def is_valid_password(password):
    if len(password) < 8:
        return False
    if not any(char.isupper() for char in password):
        return False
    if not any(char.isdigit() for char in password):
        return False
    if not password.isalnum():
        return False
    return True

# Fungsi untuk mendapatkan ID terakhir
def get_last_id():
    if not os.path.exists(CSV_FILE_PATH):
        return 0
    with open(CSV_FILE_PATH, mode='r') as file:
        reader = csv.reader(file)
        rows = list(reader)
        if len(rows) > 1:  # Skip header
            return int(rows[-1][0])
    return 0

# Fungsi untuk menyimpan data pengguna ke CSV
def save_user(name, email, password):
    last_id = get_last_id()
    new_id = last_id + 1
    with open(CSV_FILE_PATH, mode='a', newline='') as file:
        writer = csv.writer(file)
        if file.tell() == 0:  # File is empty, write header
            writer.writerow(['id', 'nama', 'email', 'password'])
        writer.writerow([new_id, name, email, password])

# Fungsi untuk memeriksa apakah email sudah terdaftar
def is_user_registered(email):
    if not os.path.exists(CSV_FILE_PATH):
        return False  # Jika file tidak ada, berarti belum ada user

    with open(CSV_FILE_PATH, mode='r') as file:
        reader = csv.reader(file)
        next(reader, None)  # Skip header
        for row in reader:
            if row[2] == email:  # Email is in the third column
                return True
    return False

def save_pinjaman_to_csv(peminjam_id, judul_buku, tanggal_batas_pinjaman, status):
    tanggal_pengembalian = 'NULL'
    with open(CSV_PINJAMAN_PATH, mode='a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([peminjam_id, judul_buku, tanggal_batas_pinjaman,tanggal_pengembalian, status])

def check_and_update_status():
    pinjaman_updated = []
    now = datetime.now()

    # Buka file CSV dan baca barisnya
    with open(CSV_PINJAMAN_PATH, mode='r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            batas_waktu = datetime.fromisoformat(row['tanggal_batas_pinjaman'])
            
            # Jika sudah melewati batas waktu, ubah status menjadi 2
            if now > batas_waktu and row['status'] == '1':
                row['status'] = '2'
            
            # Simpan data yang sudah diperbarui
            pinjaman_updated.append(row)
    
    # Tulis kembali file CSV dengan data yang telah diperbarui
    with open(CSV_PINJAMAN_PATH, mode='w', newline='') as file:
        fieldnames = ['id_peminjam', 'judul_buku', 'tanggal_batas_pinjaman', 'tanggal_pengembalian', 'status']
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(pinjaman_updated)

@app.route('/')
def home():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    buku_list = read_buku_csv()
    user_id = session['user_id']
    return render_template('home.html', buku_list=buku_list, user_id=user_id)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        with open(CSV_FILE_PATH, mode='r') as file:
            reader = csv.reader(file)
            next(reader, None)
            for row in reader:
                if row[2] == email and row[3] == password:
                    session['user_id'] = row[0]
                    flash('Login berhasil!', 'success')
                    return redirect(url_for('home'))  # Setelah login, arahkan ke home
        
        flash('Email atau password salah.', 'error')
        return render_template('login.html')

    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['username']
        email = request.form['email']
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        
        if not is_valid_email(email):
            flash('Email tidak valid.', 'error')
            return render_template('register.html')
        
        if not is_valid_password(password):
            flash('Password harus terdiri dari 8 karakter alphanumeric dan setidaknya 1 huruf kapital, tanpa karakter khusus.', 'error')
            return render_template('register.html')
        
        if password != confirm_password:
            flash('Password tidak cocok. Pastikan Anda memasukkan password yang sama.', 'error')
            return render_template('register.html')
        
        if is_user_registered(email):
            flash('Email sudah digunakan. Silakan gunakan email lain.', 'error')
            return render_template('register.html')
        
        save_user(name, email, password)
        flash('Registrasi berhasil! Silakan login.', 'success')
        return redirect(url_for('login'))

    return render_template('register.html')

@app.route('/pinjam_buku', methods=['POST'])
def pinjam_buku():
    if 'user_id' not in session:
        flash('Silakan login terlebih dahulu.', 'error')
        return redirect(url_for('login'))

    judul_buku = request.form.get('judul_buku')
    tanggal_batas_pinjaman = request.form.get('tanggal_batas_pinjaman')
    user_id = session['user_id']

    # Cek apakah user masih memiliki buku yang dipinjam
    if is_user_has_active_borrow(user_id):
        flash('Anda masih memiliki buku yang sedang dipinjam. Silakan kembalikan buku tersebut sebelum meminjam lagi.', 'error')
        return redirect(url_for('home'))

    # Simpan data peminjaman ke CSV dengan status 1 (masih dipinjam)
    save_pinjaman_to_csv(user_id, judul_buku, tanggal_batas_pinjaman, 1)

    # Perbarui status buku menjadi 1 (sedang dipinjam)
    update_buku_status(judul_buku, 1)

    flash(f'Berhasil meminjam buku "{judul_buku}".', 'success')
    return redirect(url_for('home'))

def is_user_has_active_borrow(user_id):
    if not os.path.exists(CSV_PINJAMAN_PATH):
        return False  # Jika file tidak ada, berarti belum ada peminjaman

    with open(CSV_PINJAMAN_PATH, mode='r') as file:
        reader = csv.reader(file)
        next(reader, None)  # Skip header
        for row in reader:
            if row[0] == user_id and row[4] == '1':  # Cek jika ada peminjaman dengan status 1 (masih dipinjam)
                return True
    return False

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    flash('Anda telah logout.', 'success')
    return redirect(url_for('login'))

# Modifikasi route untuk dashboard
@app.route('/dashboard')
def dashboard():
    check_and_update_status()
    books = read_buku_csv()
    loans = read_pinjaman_csv()
    return render_template('dashboard.html', books=books, loans=loans)

# Route untuk mengubah status pinjaman
@app.route('/change_status/<loan_id>')
def change_status(loan_id):
    loans = read_pinjaman_csv()
    books = read_buku_csv()
    
    for loan in loans:
        if loan['id_peminjam'] == loan_id and (loan['status'] == '1' or loan['status'] == '2'):
            loan['status'] = '0'
            loan['tanggal_pengembalian'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')  # Menyimpan waktu pengembalian
            for book in books:
                if book['judul'] == loan['judul_buku']:
                    book['status'] = '0'
                    break
            break
    
    # Tulis kembali data pinjaman yang diperbarui (termasuk tanggal_pengembalian)
    with open(CSV_PINJAMAN_PATH, mode='w', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=['id_peminjam', 'judul_buku', 'tanggal_batas_pinjaman', 'tanggal_pengembalian','status'])
        writer.writeheader()
        writer.writerows(loans)
    
    # Tulis kembali data buku yang diperbarui
    with open(CSV_BUKU_PATH, mode='w', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=['id', 'judul', 'author', 'status','is_deleted'])
        writer.writeheader()
        writer.writerows(books)
    
    flash('Status pinjaman berhasil diubah.', 'success')
    return redirect(url_for('dashboard'))

# Route untuk menambahkan buku baru
@app.route('/add_book', methods=['GET', 'POST'])
def add_book():
    if request.method == 'POST':
        books = read_buku_csv()
        new_id = str(max([int(book['id']) for book in books]) + 1)
        new_book = {
            'id': new_id,
            'judul': request.form['judul_buku'],  # Ubah 'judul' menjadi 'judul_buku'
            'author': request.form['author'],
            'status': '0',
            'is_deleted' : '0'
        }
        books.append(new_book)
        with open(CSV_BUKU_PATH, mode='w', newline='') as file:
            writer = csv.DictWriter(file, fieldnames=['id', 'judul', 'author', 'status', 'is_deleted'])
            writer.writeheader()
            writer.writerows(books)
        flash('Buku baru berhasil ditambahkan.', 'success')
        return redirect(url_for('dashboard'))
    return render_template('add_book.html')

@app.route('/delete_book/<book_id>', methods=['POST'])
def delete_book(book_id):
    soft_delete_book(book_id)
    flash('Buku berhasil dihapus.', 'success')
    return redirect(url_for('dashboard'))

def soft_delete_book(book_id):
    books = read_buku_csv()
    for book in books:
        if book['id'] == book_id:
            book['is_deleted'] = '1'
            break

    # Simpan kembali ke CSV
    with open(CSV_BUKU_PATH, mode='w', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=['id', 'judul', 'author', 'status', 'is_deleted'])
        writer.writeheader()
        writer.writerows(books)


# Fungsi-fungsi dan route lainnya tetap dipertahankan...

if __name__ == '__main__':
    if not os.path.exists(DATA_FOLDER):
        os.makedirs(DATA_FOLDER)
    
    # Create CSV files if they do not exist
    if not os.path.exists(CSV_FILE_PATH):
        with open(CSV_FILE_PATH, mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(['id', 'username', 'password'])
            writer.writerow(['1', 'admin', 'adminpass'])
            writer.writerow(['2', 'user1', 'user1pass'])

    if not os.path.exists(CSV_BUKU_PATH):
        with open(CSV_BUKU_PATH, mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(['id', 'judul', 'author', 'status'])
            writer.writerow(['1', 'Buku A', 'Penulis A', '0'])
            writer.writerow(['2', 'Buku B', 'Penulis B', '0'])

    if not os.path.exists(CSV_PINJAMAN_PATH):
        with open(CSV_PINJAMAN_PATH, mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(['id_peminjam', 'judul_buku', 'tanggal_batas_peminjaman', 'status'])

    app.run(debug=True)
