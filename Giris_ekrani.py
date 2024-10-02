import streamlit as st
from Veri_tabanı_oluşturma import create_tables
from database import add_userdata, login_user
import sqlite3
import pandas as pd

# Sayfa açıldığında veri tabanı tablolarını kontrol et ve oluştur
create_tables()

# Kullanıcı kimlik doğrulama fonksiyonu
def user_authentication():
    # Kayıt ol
    st.header("Kayıt Ol")
    reg_username = st.text_input("Kullanıcı Adı")
    reg_password = st.text_input("Şifre", type='password')
    reg_email = st.text_input("E-posta")

    if st.button("Kayıt Ol"):
        if add_userdata(reg_username, reg_password, reg_email):
            st.success("Kayıt başarılı!")
        else:
            st.error("Kullanıcı adı veya e-posta zaten kullanılıyor.")

    # Giriş yap
    st.header("Giriş Yap")
    login_username = st.text_input("Kullanıcı Adı", key="login_username")
    login_password = st.text_input("Şifre", type='password', key="login_password")

    if st.button("Giriş Yap"):
        user_id = login_user(login_username, login_password)
        if user_id:  # Eğer kullanıcı ID'si döndüyse
            st.session_state.login = True  # Oturum durumunu güncelle
            st.session_state.user_id = user_id  # Kullanıcı ID'sini sakla
            st.success("Giriş başarılı!")
            return True, user_id
        else:
            st.error("Kullanıcı adı veya şifre yanlış.")
            return False, None

def get_connection():
    return sqlite3.connect('database.db')


def fetch_data(table_name, user_id):
    # Veritabanı bağlantısını aç
    conn = get_connection()
    # Verileri al
    query = f"SELECT * FROM {table_name} WHERE user_id = ?"
    df = pd.read_sql_query(query, conn, params=(user_id,))
    conn.close()

    # Eğer sonuç yoksa boş bir DataFrame döndür
    if df.empty:
        return pd.DataFrame()  # Boş DataFrame
    return df  # DataFrame döndür
