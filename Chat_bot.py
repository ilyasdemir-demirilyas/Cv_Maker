import os
import streamlit as st
import google.generativeai as genai

# API anahtarının kaydedileceği dosya
API_KEY_FILE = "api_key.txt"

def load_api_key():
    """API anahtarını dosyadan yükler."""
    if os.path.exists(API_KEY_FILE):
        with open(API_KEY_FILE, "r") as file:
            return file.read().strip()
    return None

def save_api_key(api_key):
    """API anahtarını dosyaya kaydeder."""
    with open(API_KEY_FILE, "w") as file:
        file.write(api_key)

def run_cv_bot_app():
    st.title("CV Asistanı")

    # API anahtarını yükle
    if "api_key" not in st.session_state:
        st.session_state.api_key = load_api_key()  # Dosyadan API anahtarını yükle

    # API anahtarı girilmediyse
    if not st.session_state.api_key:
        st.write("Lütfen Google GenAI API anahtarınızı girin.")
        st.session_state.api_key = st.text_input(
            "API Key",
            placeholder="API anahtarınızı buraya girin",
            type="password"
        )
        if st.session_state.api_key:
            # API anahtarını kontrol et
            if st.session_state.api_key.startswith("AIza"):
                save_api_key(st.session_state.api_key)  # API anahtarını dosyaya kaydet
                st.success("API anahtarınızı kaydettiniz. Şimdi uygulamayı kullanabilirsiniz.")
                st.experimental_rerun()  # Sayfayı yeniden yükle
            else:
                st.error("Geçersiz API anahtarı. Lütfen `AIza` ile başlayan bir anahtar girin.")
    else:
        # API anahtarını doğrulama
        try:
            os.environ["API_KEY"] = st.session_state.api_key
            genai.configure(api_key=os.environ["API_KEY"])

            # Modeli tanımlama
            model = genai.GenerativeModel('gemini-1.5-flash-latest')

            # Sistem mesajı
            sistem_mesaji = (
                "Sen profesyonel bir CV danışmanısın. Kullanıcıların CV bölümlerini profesyonel bir dil kullanarak düzenleyeceksin. "
                "Eğer kullanıcı sohbet etmek istiyorsa, uygun ve nazik bir şekilde sohbet et. "
                "Açık, net ve etkili bir dil kullanarak yanıt ver. "
                "Her bölüm için önerilerde bulun ve gerektiğinde ek bilgiler ver. "
                "Kullanıcıların hangi konularda yardım istediğini anlamak için sorular sor. "
                "Eğer kullanıcı 'Merhaba' veya 'Nasılsın?' gibi bir mesaj gönderirse, samimi bir yanıt ver ve ardından CV ile ilgili nasıl yardımcı olabileceğini sor."
            )

            # Streamlit uygulaması
            if "messages" not in st.session_state:
                st.session_state.messages = []

                # İlk mesaj: bot kendini tanıtıyor
                welcome_message = "Merhaba! Ben profesyonel bir CV danışmanıyım. Size CV'nizle ilgili nasıl yardımcı olabilirim?"
                st.session_state.messages.append({"role": "assistant", "content": welcome_message})

            # Mesajları göster
            for message in st.session_state.messages:
                with st.chat_message(message["role"]):
                    st.markdown(message["content"])

            # Kullanıcıdan CV bölümü alma
            if prompt := st.chat_input("Sorunuzu girin:"):
                st.session_state.messages.append({"role": "user", "content": prompt})

                with st.chat_message("user"):
                    st.markdown(prompt)

                try:
                    # Modelden yanıt al
                    response = model.generate_content(f"{sistem_mesaji} CV BÖLÜMÜ: '{prompt}'\nDÜZENLENMİŞ CEVAP:")
                    response_text = response.text.strip()
                except Exception as e:
                    response_text = f"Model yanıt oluştururken bir hata oluştu: {e}"

                # Yanıtı göster
                with st.chat_message("assistant"):
                    st.markdown(response_text)

                st.session_state.messages.append({"role": "assistant", "content": response_text})

        except Exception as e:
            st.error(f"API anahtarını doğrularken bir hata oluştu: {e}")
            st.write("Geçerli bir API anahtarınız yoksa, bir tane oluşturmak için [buraya tıklayın](https://aistudio.google.com/app/apikey).")
            # API anahtarını sıfırlama
            st.session_state.api_key = ""
            os.remove(API_KEY_FILE)  # Geçersizse dosyayı sil
            st.experimental_rerun()  # Sayfayı yeniden yükle

# Uygulamayı çalıştır
if __name__ == "__main__":
    run_cv_bot_app()
