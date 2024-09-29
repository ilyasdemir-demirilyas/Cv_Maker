import streamlit as st
import pandas as pd
from streamlit_option_menu import option_menu
from Chat_bot import run_cv_bot_app
from datetime import datetime
from docx.shared import Pt, Inches
from docx.shared import RGBColor
import os
from io import BytesIO
from docx import Document


# Başlık ve sayfa yapılandırması
st.set_page_config(page_title="CV Oluşturucu", layout="wide")

CSV_FILES = {
    'personal_info': 'personal_info.csv',
    'education': 'education.csv',
    'projects': 'projects.csv',
    'experience': 'experience.csv',
    'certifications': 'certifications.csv',
    'activities': 'activities.csv',
    'skills': 'skills.csv',
    'accounts': 'accounts.csv'  # Add 'accounts' to the CSV_FILES
}

# Update DEFAULT_COLUMNS with default structure for 'accounts'
DEFAULT_COLUMNS = {
    'personal_info': ['name', 'email', 'phone'],
    'education': ['university', 'faculty', 'department', 'start_year', 'end_year'],
    'projects': ['title', 'description', 'technologies', 'show_in_cv'],
    'experience': ['company', 'position', 'start_date', 'end_date', 'description', 'show_in_cv'],
    'certifications': ['name', 'institution', 'date', 'show_in_cv'],
    'activities': ['name', 'role', 'date_range', 'description', 'show_in_cv'],
    'skills': ['name', 'proficiency', 'show_in_cv'],
    'accounts': ['name', 'link']  # Default structure for 'accounts'
}

import os
import streamlit as st

import os
import streamlit as st

DATA_DIR =""
photo_folder_path = ""
# Kullanıcıdan CSV dosyalarının bulunduğu klasör yolunu alıyoruz
DATA_DIR = st.text_input(
    "Lütfen bilgilerinizi içeren dosyaların bulunduğu veya kaydedilmesini istediğiniz klasör yolunu giriniz:",
    key="data_folder_link"
)

# Eğer kullanıcı girişi yapmamışsa, bir uyarı ver
if not DATA_DIR:
    st.warning("Lütfen geçerli bir klasör yolu girin.")

# Klasör yolunu doğrulamak için bir buton ekleyebilirsiniz
if os.path.isdir(DATA_DIR):

    UPLOAD_FOLDER = "cv_photo"
    # DATA_DIR içinde UPLOAD_FOLDER'ı oluşturmak için tam yolu belirliyoruz
    photo_folder_path = os.path.join(DATA_DIR, UPLOAD_FOLDER)

    # Fotoğraf klasörünün var olup olmadığını kontrol edip, yoksa oluşturuyoruz
    if not os.path.exists(photo_folder_path):
        os.makedirs(photo_folder_path)
        st.write(f"'{photo_folder_path}' klasörü oluşturuldu.")





# Fonksiyon: CSV dosyasını oluşturma (eğer yoksa)
def initialize_csv(section):
    file_path = os.path.join(DATA_DIR, CSV_FILES[section])
    if not os.path.exists(file_path):
        df = pd.DataFrame(columns=DEFAULT_COLUMNS[section])
        df.to_csv(file_path, index=False)

# Fonksiyon: CSV'den veriyi okuma (UTF-8 encoding kullanarak)
def load_data(section):
    file_path = os.path.join(DATA_DIR, CSV_FILES[section])
    initialize_csv(section)  # Ensure file exists
    return pd.read_csv(file_path, encoding='utf-8')  # Specify encoding

# Fonksiyon: CSV'ye veri yazma (UTF-8 encoding ile)
def save_data(section, df):
    file_path = os.path.join(DATA_DIR, CSV_FILES[section])
    df.to_csv(file_path, index=False, encoding='utf-8')  # Specify encoding

# Fonksiyon: Kişisel Bilgileri yükleme
def load_personal_info():
    df = load_data('personal_info')
    if not df.empty:
        return df.iloc[0].to_dict()
    return {}

# Fonksiyon: Kişisel Bilgileri kaydetme
def save_personal_info(info):
    df = pd.DataFrame([info])
    save_data('personal_info', df)

# Fonksiyon: Fotoğrafı kaydetme ve yolunu döndürme
def save_photo(photo):
    file_name = f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{photo.name}"
    file_path = os.path.join(photo_folder_path, file_name)
    st.write("yol ",file_path)
    with open(file_path, "wb") as f:
        f.write(photo.getbuffer())
    return file_path

# Fonksiyon: Diğer bölümler için genel veri ekleme
def add_entry(section, entry):
    df = load_data(section)
    df = df.append(entry, ignore_index=True)
    save_data(section, df)

# Fonksiyon: Diğer bölümler için genel veri güncelleme
def update_entry(section, index, entry):
    df = load_data(section)
    for key, value in entry.items():
        df.at[index, key] = value
    save_data(section, df)

# Fonksiyon: Diğer bölümler için genel veri silme
def delete_entry(section, index):
    df = load_data(section)
    df = df.drop(index)
    df.reset_index(drop=True, inplace=True)
    save_data(section, df)

# Oturum durumu için başlangıç verileri
if 'edit_section' not in st.session_state:
    st.session_state['edit_section'] = None
if 'edit_index' not in st.session_state:
    st.session_state['edit_index'] = None

# Sol taraftaki menü
sidebar = st.sidebar
sidebar.title("CV Oluşturucu")

with st.sidebar:
    selected = option_menu("Ana Menü",
        ["Kişisel Bilgiler", "Eğitim", "Projeler", "Deneyim",
        "Sertifikalar", "Aktiviteler", "Beceriler", "CV Asistanı"],
        icons=['person', 'book', 'projector', 'briefcase',
               'certificate', 'activity', 'tools','chat'],
        menu_icon="cast", default_index=0)  # Varsayılan olarak "Kişisel Bilgiler" sekmesi açık

def get_first_photo_from_directory(directory):
    # Belirtilen dizindeki ilk görüntü dosyasını bulur
    valid_extensions = (".jpg", ".jpeg", ".png")  # Geçerli fotoğraf dosyası uzantıları
    try:
        # Dizindeki dosyaları listele ve yalnızca resim dosyalarını filtrele
        files = [f for f in os.listdir(directory) if f.endswith(valid_extensions)]
        if files:
            # Eğer resim dosyaları varsa, dizindeki ilk resim dosyasını döndür
            first_photo_path = os.path.join(directory, files[0])
            return first_photo_path
        else:
            return None
    except Exception as e:
        pass
        return None

# Bölümlere göre giriş formları
def personal_info_section():
    st.header("Kişisel Bilgiler")
    personal_info = load_personal_info()  # Kayıtlı kişisel bilgileri yükle

    # Using session state to avoid re-creation of keys and widgets
    if 'personal_info_initialized' not in st.session_state:
        st.session_state.personal_info_initialized = True

    # Unique keys for input fields
    name = st.text_input("İsim", personal_info.get('name', ''), key='personal_info_name_unique')
    email = st.text_input("E-posta", personal_info.get('email', ''), key='personal_info_email_unique')
    phone = st.text_input(
        "Telefon (Sıfır olmadan giriniz )",
        personal_info.get('phone', ''),
        key='personal_info_phone_unique',
        placeholder="xxxxxxxxxx",
        max_chars=10
    )

    if st.button("Kaydet", key='personal_info_save_button_unique'):
        if not name.strip():
            st.error("İsim alanı zorunludur.")
        else:
            # Telefon numarası doğrulaması
            phone_digits = ''.join(filter(str.isdigit, phone))
            if phone_digits:
                if len(phone_digits) != 10:
                    st.error("Telefon numarası 10 haneli olmalıdır.")
                elif phone_digits.startswith('0'):
                    st.error("Telefon numarası sıfırla başlamamalıdır.")
                else:
                    formatted_phone = f"({phone_digits[:3]}) {phone_digits[3:]}"
                    info = {
                        'name': name.strip(),
                        'email': email.strip(),
                        'phone': formatted_phone
                    }
                    save_personal_info(info)
                    st.success("Kişisel bilgiler kaydedildi.")
            else:
                # Telefon numarası isteğe bağlı olduğu için boş bırakılabilir
                info = {
                    'name': name.strip(),
                    'email': email.strip(),
                    'phone': ''
                }
                save_personal_info(info)
                st.success("Kişisel bilgiler kaydedildi.")

    st.subheader("Fotoğraf")
    photo = st.file_uploader("Fotoğraf Yükle (İsteğe Bağlı)", type=["jpg", "jpeg", "png"], key="photo_uploader_unique")
    photo_path = personal_info.get('cv_photo', '')

    if photo is not None:
        # Fotoğraf yüklendiyse, ancak kaydedilmeden gösteriliyor
        st.session_state['photo'] = photo  # Fotoğraf geçici olarak bellekte tutuluyor
        st.image(photo, width=150)
    elif photo_path:
        # Eğer kişisel bilgilerde fotoğraf kaydı varsa onu göster
        st.image(photo_path, width=150)
    else:
        # Eğer kişisel bilgilerde fotoğraf yoksa dizinden ilk fotoğrafı al
        directory = "cv_photo"  # Fotoğrafların saklandığı dizin
        first_photo_path = get_first_photo_from_directory(directory)
        if first_photo_path:
            st.image(first_photo_path, width=150)


    # Kaydet butonuna basıldığında yeni fotoğraf kaydedilir
    if st.button("Fotoğrafı Kaydet", key='save_photo_button_unique') and 'photo' in st.session_state:
        photo_path = save_photo(st.session_state['photo'])  # Fotoğraf kaydediliyor
        st.success("Fotoğraf kaydedildi.")

    st.subheader("Hesaplarınız")
    account_name = st.text_input("Sosyal Medya Adı", key="account_name_unique")
    account_link = st.text_input("Hesap Linki", key="account_link_unique")
    if st.button("Hesap Ekle", key='add_account_button_unique'):
        if not account_name.strip() or not account_link.strip():
            st.error("Sosyal medya adı ve hesap linki zorunludur.")
        else:
            entry = {
                'name': account_name.strip(),
                'link': account_link.strip()
            }
            add_entry('accounts', entry)
            st.success("Hesap eklendi.")
            st.experimental_rerun()

    st.subheader("Eklenen Hesaplar")
    df_accounts = load_data('accounts')
    if not df_accounts.empty:
        for idx, acc in df_accounts.iterrows():
            st.markdown(f"**{acc['name']}:** {acc['link']}")
            col1, col2 = st.columns(2)
            with col1:
                if st.button("Düzenle", key=f"edit_acc_{idx}_{acc['name']}"):
                    st.session_state['edit_section'] = 'accounts'
                    st.session_state['edit_index'] = idx
                    st.experimental_rerun()
            with col2:
                if st.button("Sil", key=f"delete_acc_{idx}_{acc['name']}"):
                    delete_entry('accounts', idx)
                    st.success("Hesap silindi.")
                    st.experimental_rerun()

    # Hesap düzenleme
    if st.session_state.get('edit_section') == 'accounts' and st.session_state.get('edit_index') is not None:
        idx = st.session_state['edit_index']
        acc = load_data('accounts').iloc[idx]
        st.write(f"**{acc['name']}** düzenleniyor...")
        account_name_edit = st.text_input("Sosyal Medya Adı", acc['name'], key=f"acc_name_edit_{idx}")
        account_link_edit = st.text_input("Hesap Linki", acc['link'], key=f"acc_link_edit_{idx}")
        if st.button("Kaydet", key=f"save_acc_edit_{idx}"):
            if not account_name_edit.strip() or not account_link_edit.strip():
                st.error("Sosyal medya adı ve hesap linki zorunludur.")
            else:
                updated_entry = {
                    'name': account_name_edit.strip(),
                    'link': account_link_edit.strip()
                }
                update_entry('accounts', idx, updated_entry)
                st.success("Hesap güncellendi.")
                st.session_state['edit_section'] = None
                st.session_state['edit_index'] = None
                st.experimental_rerun()
        if st.button("İptal", key=f"cancel_acc_edit_{idx}"):
            st.session_state['edit_section'] = None
            st.session_state['edit_index'] = None
            st.experimental_rerun()


def education_section():
    st.header("Eğitim")
    df_education = load_data('education')
    if not df_education.empty:
        education = df_education.iloc[0].to_dict()
    else:
        education = {}
    university = st.text_input("Üniversite", education.get('university', ''))
    faculty = st.text_input("Fakülte", education.get('faculty', ''))
    department = st.text_input("Bölüm", education.get('department', ''))
    start_year = st.text_input("Başlangıç Yılı", education.get('start_year', ''))

    ongoing = st.checkbox("Devam Ediyor", value=(education.get('end_year', '') == 'Devam Ediyor'), key="education_ongoing")
    if not ongoing:
        end_year = st.text_input("Bitiş Yılı", education.get('end_year', ''))
    else:
        end_year = 'Devam Ediyor'

    if st.button("Kaydet"):
        if not university.strip() or not faculty.strip() or not department.strip() or not start_year.strip():
            st.error("Tüm alanlar zorunludur.")
        elif not start_year.isdigit():
            st.error("Başlangıç Yılı sayısal bir değer olmalıdır.")
        elif not ongoing and (not end_year.strip() or not end_year.isdigit()):
            st.error("Bitiş Yılı sayısal bir değer olmalıdır.")
        else:
            entry = {
                'university': university.strip(),
                'faculty': faculty.strip(),
                'department': department.strip(),
                'start_year': start_year.strip(),
                'end_year': end_year.strip()
            }
            save_data('education', pd.DataFrame([entry]))
            st.success("Eğitim bilgileri kaydedildi.")


def projects_section():
    st.header("Projeler")
    df_projects = load_data('projects')  # Projeleri yüklüyoruz

    # Düzenleme durumu kontrolü
    if st.session_state.get('edit_section') == 'projects' and st.session_state.get('edit_index') is not None:
        idx = st.session_state['edit_index']
        proj = df_projects.iloc[idx]
        st.write(f"**{proj['title']}** düzenleniyor..." if proj['title'] else "Proje düzenleniyor...")

        # İsteğe bağlı proje başlığı ve teknolojiler alanları
        project_title = st.text_input("Proje Başlığı (İsteğe Bağlı)", proj['title'] if pd.notna(proj['title']) else "", key=f"title_edit_{idx}")
        project_description = st.text_area("Proje Açıklaması", proj['description'], key=f"desc_edit_{idx}")
        technologies = st.text_input("Kullanılan Teknolojiler (virgülle ayırın)", proj['technologies'] if pd.notna(proj['technologies']) else "", key=f"tech_edit_{idx}")
        show_in_cv = st.checkbox("CV'de Göster", value=proj['show_in_cv'], key=f"show_edit_{idx}")

        if st.button("Kaydet", key=f"save_proj_edit_{idx}"):
            if not project_description.strip():
                st.error("Proje açıklaması zorunludur.")
            else:
                updated_entry = {
                    'title': project_title.strip(),  # Proje başlığı boş olabilir
                    'description': project_description.strip(),  # Proje açıklaması zorunlu
                    'technologies': technologies.strip(),  # Teknolojiler alanı boş olabilir
                    'show_in_cv': show_in_cv
                }
                update_entry('projects', idx, updated_entry)
                st.success("Proje güncellendi.")
                st.session_state['edit_section'] = None
                st.session_state['edit_index'] = None
                st.experimental_rerun()

        if st.button("İptal", key=f"cancel_proj_edit_{idx}"):
            st.session_state['edit_section'] = None
            st.session_state['edit_index'] = None
            st.experimental_rerun()
    else:
        # Yeni proje ekleme formu
        project_description = st.text_area("Proje Açıklaması", key="project_description")
        project_title = st.text_input("Proje Başlığı (İsteğe Bağlı)", key="project_title")
        technologies = st.text_input("Kullanılan Teknolojiler (virgülle ayırın)", key="technologies")
        show_in_cv = st.checkbox("CV'de Göster", value=True, key="show_project_cv")

        if st.button("Ekle"):
            if not project_description.strip():
                st.error("Proje açıklaması zorunludur.")
            else:
                entry = {
                    'title': project_title.strip(),  # Proje başlığı isteğe bağlı, boş olabilir
                    'description': project_description.strip(),  # Proje açıklaması zorunlu
                    'technologies': technologies.strip(),  # Teknolojiler isteğe bağlı, boş olabilir
                    'show_in_cv': show_in_cv
                }
                add_entry('projects', entry)
                st.success("Proje eklendi.")
                st.experimental_rerun()

    # Eklenen projeler
    st.subheader("Eklenen Projeler")
    if not df_projects.empty:
        for idx, proj in df_projects.iterrows():
            # Proje başlığı ve teknolojiler NaN ise boş göster
            title_display = f"**{proj['title']}**" if pd.notna(proj['title']) and proj['title'] else ""
            description_display = proj['description'] if pd.notna(proj['description']) else ""
            technologies_display = proj['technologies'] if pd.notna(proj['technologies']) else ""

            if title_display:
                st.markdown(f"• {title_display}")
            st.markdown(f"   • {description_display}")
            if technologies_display:
                st.markdown(f"   **Kullanılan Teknolojiler:** {technologies_display}")

            col1, col2, col3 = st.columns(3)
            with col1:
                if st.button("Düzenle", key=f"edit_proj_{idx}_{proj['title']}_{proj['description']}"):
                    st.session_state['edit_section'] = 'projects'
                    st.session_state['edit_index'] = idx
                    st.experimental_rerun()

            with col2:
                if st.button("Sil", key=f"delete_proj_{idx}_{proj['title']}_{proj['description']}"):
                    delete_entry('projects', idx)
                    st.success("Proje silindi.")
                    st.experimental_rerun()

            with col3:
                show = st.checkbox("CV'de Göster", value=proj['show_in_cv'],
                                   key=f"show_proj_{idx}_{proj['title']}_{proj['description']}")
                df_projects.at[idx, 'show_in_cv'] = show

        save_data('projects', df_projects)



def experience_section():
    st.header("Deneyim")
    df_experience = load_data('experience')

    if st.session_state.get('edit_section') == 'experience' and st.session_state.get('edit_index') is not None:
        idx = st.session_state['edit_index']
        exp = df_experience.iloc[idx]
        st.write(f"**{exp['company']} - {exp['position']}** düzenleniyor...")
        company = st.text_input("Şirket Adı", exp['company'], key=f"company_edit_{idx}")
        position = st.text_input("Pozisyon", exp['position'], key=f"position_edit_{idx}")
        start_date = st.date_input("Başlangıç Tarihi", datetime.strptime(exp['start_date'], "%d.%m.%Y"),
                                   key=f"start_date_edit_{idx}")
        ongoing = st.checkbox("Devam Ediyor", value=(exp['end_date'] == 'Devam Ediyor'), key=f"ongoing_edit_{idx}")
        if not ongoing:
            end_date = st.date_input("Bitiş Tarihi", datetime.strptime(exp['end_date'], "%d.%m.%Y"),
                                     key=f"end_date_edit_{idx}")
            end_date_str = end_date.strftime("%d.%m.%Y")
        else:
            end_date_str = 'Devam Ediyor'
        experience_description = st.text_area("Deneyim Açıklaması", exp['description'], key=f"description_edit_{idx}")
        show_in_cv = st.checkbox("CV'de Göster", value=exp['show_in_cv'], key=f"show_exp_edit_{idx}")
        if st.button("Kaydet", key=f"save_exp_edit_{idx}"):
            if not company.strip() or not position.strip() or not experience_description.strip():
                st.error("Tüm alanlar zorunludur.")
            else:
                updated_entry = {
                    'company': company.strip(),
                    'position': position.strip(),
                    'start_date': start_date.strftime("%d.%m.%Y"),
                    'end_date': end_date_str,
                    'description': experience_description.strip(),
                    'show_in_cv': show_in_cv
                }
                update_entry('experience', idx, updated_entry)
                st.success("Deneyim güncellendi.")
                st.session_state['edit_section'] = None
                st.session_state['edit_index'] = None
                st.experimental_rerun()
        if st.button("İptal", key=f"cancel_exp_edit_{idx}"):
            st.session_state['edit_section'] = None
            st.session_state['edit_index'] = None
            st.experimental_rerun()
    else:
        company = st.text_input("Şirket Adı", key="company_name")
        position = st.text_input("Pozisyon", key="position")
        start_date = st.date_input("Başlangıç Tarihi", value=datetime.today(), key="start_date")
        ongoing = st.checkbox("Devam Ediyor", value=False, key="experience_ongoing")
        if not ongoing:
            end_date = st.date_input("Bitiş Tarihi", value=datetime.today(), key="end_date")
        else:
            end_date = None
        experience_description = st.text_area("Deneyim Açıklaması", key="experience_description")
        show_in_cv = st.checkbox("CV'de Göster", value=True, key="show_experience_cv")
        if st.button("Ekle"):
            if not company.strip() or not position.strip() or not experience_description.strip():
                st.error("Tüm alanlar zorunludur.")
            else:
                exp_entry = {
                    'company': company.strip(),
                    'position': position.strip(),
                    'start_date': start_date.strftime("%d.%m.%Y"),
                    'end_date': 'Devam Ediyor' if ongoing else end_date.strftime("%d.%m.%Y"),
                    'description': experience_description.strip(),
                    'show_in_cv': show_in_cv
                }
                add_entry('experience', exp_entry)
                st.success("Deneyim eklendi.")
                st.experimental_rerun()

    st.subheader("Eklenen Deneyimler")
    if not df_experience.empty:
        for idx, exp in df_experience.iterrows():
            st.markdown(f"**{exp['company']} - {exp['position']}**")
            st.markdown(f"   • {exp['description']}")
            col1, col2, col3 = st.columns(3)
            with col1:
                if st.button("Düzenle", key=f"edit_exp_{idx}_{exp['company']}_{exp['position']}"):
                    st.session_state['edit_section'] = 'experience'
                    st.session_state['edit_index'] = idx
                    st.experimental_rerun()
            with col2:
                if st.button("Sil", key=f"delete_exp_{idx}_{exp['company']}_{exp['position']}"):
                    delete_entry('experience', idx)
                    st.success("Deneyim silindi.")
                    st.experimental_rerun()
            with col3:
                show = st.checkbox("CV'de Göster", value=exp['show_in_cv'],
                                   key=f"show_exp_{idx}_{exp['company']}_{exp['position']}")
                df_experience.at[idx, 'show_in_cv'] = show
        save_data('experience', df_experience)


def certifications_section():
    st.header("Sertifikalar")
    df_certifications = load_data('certifications')

    if st.session_state.get('edit_section') == 'certifications' and st.session_state.get('edit_index') is not None:
        idx = st.session_state['edit_index']
        cert = df_certifications.iloc[idx]
        st.write(f"**{cert['name']}** düzenleniyor...")

        certificate_name = st.text_input("Sertifika Adı", cert['name'], key=f"cert_name_edit_{idx}")
        institution = st.text_input("Kurum", cert['institution'], key=f"institution_edit_{idx}")

        # Tarih bilgisini string olarak kontrol et
        date_str = str(cert['date']) if pd.notna(cert['date']) else ''

        # Tarih bilgilerini ayır
        date_parts = date_str.split('.') if date_str else ['', '', '']
        year = date_parts[-1] if len(date_parts) >= 1 else ''
        month = date_parts[-2] if len(date_parts) >= 2 else ''
        day = date_parts[-3] if len(date_parts) >= 3 else ''

        year = st.text_input("Yıl", year, key=f"year_edit_{idx}")
        month = st.text_input("Ay (İsteğe Bağlı)", month, key=f"month_edit_{idx}")
        day = st.text_input("Gün (İsteğe Bağlı)", day, key=f"day_edit_{idx}")
        show_in_cv = st.checkbox("CV'de Göster", value=cert['show_in_cv'], key=f"show_cert_edit_{idx}")

        if st.button("Kaydet", key=f"save_cert_edit_{idx}"):
            if not certificate_name.strip() or not institution.strip() or not year.strip():
                st.error("Sertifika adı, kurum ve yıl zorunludur.")
            else:
                if not year.isdigit():
                    st.error("Yıl sayısal bir değer olmalıdır.")
                else:
                    date = f"{day}.{month}.{year}" if day and month else (f"{month}.{year}" if month else year)
                    updated_entry = {
                        'name': certificate_name.strip(),
                        'institution': institution.strip(),
                        'date': date,
                        'show_in_cv': show_in_cv
                    }
                    update_entry('certifications', idx, updated_entry)
                    st.success("Sertifika güncellendi.")
                    st.session_state['edit_section'] = None
                    st.session_state['edit_index'] = None
                    st.experimental_rerun()

        if st.button("İptal", key=f"cancel_cert_edit_{idx}"):
            st.session_state['edit_section'] = None
            st.session_state['edit_index'] = None
            st.experimental_rerun()

    else:
        certificate_name = st.text_input("Sertifika Adı", key="certificate_name")
        institution = st.text_input("Kurum", key="institution")
        year = st.text_input("Yıl", key="year")
        month = st.text_input("Ay", key="month")
        day = st.text_input("Gün (İsteğe Bağlı)", key="day")
        show_in_cv = st.checkbox("CV'de Göster", value=True, key="show_cert_cv")
        if st.button("Ekle"):
            if not certificate_name.strip() or not institution.strip() or not year.strip() or not month.strip():
                st.error("Sertifika adı, kurum ve yıl zorunludur.")
            else:
                if not year.isdigit():
                    st.error("Yıl sayısal bir değer olmalıdır.")
                else:
                    date = f"{day}.{month}.{year}" if day and month else (f"{month}.{year}" if month else year)
                    cert_entry = {
                        'name': certificate_name.strip(),
                        'institution': institution.strip(),
                        'date': date,
                        'show_in_cv': show_in_cv
                    }
                    add_entry('certifications', cert_entry)
                    st.success("Sertifika eklendi.")
                    st.experimental_rerun()

    st.subheader("Eklenen Sertifikalar")
    if not df_certifications.empty:
        for idx, cert in df_certifications.iterrows():
            st.markdown(f"**{cert['name']}**")
            st.markdown(f"   • {cert['institution']} – {cert['date']}")
            col1, col2, col3 = st.columns(3)
            with col1:
                if st.button("Düzenle", key=f"edit_cert_{idx}_{cert['name']}"):
                    st.session_state['edit_section'] = 'certifications'
                    st.session_state['edit_index'] = idx
                    st.experimental_rerun()
            with col2:
                if st.button("Sil", key=f"delete_cert_{idx}_{cert['name']}"):
                    delete_entry('certifications', idx)
                    st.success("Sertifika silindi.")
                    st.experimental_rerun()
            with col3:
                show = st.checkbox("CV'de Göster", value=cert['show_in_cv'], key=f"show_cert_{idx}_{cert['name']}")
                df_certifications.at[idx, 'show_in_cv'] = show
        save_data('certifications', df_certifications)

def activities_section():
    st.header("Aktiviteler")
    df_activities = load_data('activities')

    if st.session_state.get('edit_section') == 'activities' and st.session_state.get('edit_index') is not None:
        idx = st.session_state['edit_index']
        act = df_activities.iloc[idx]
        st.write(f"**{act['name']} - {act['role']}** düzenleniyor...")
        community_name = st.text_input("Topluluk Adı", act['name'], key=f"act_name_edit_{idx}")
        role = st.text_input("Pozisyon", act['role'], key=f"role_edit_{idx}")
        date_parts = act['date_range'].split(' - ')
        start_date = datetime.strptime(date_parts[0], "%d.%m.%Y")
        ongoing = date_parts[1] == 'Devam Ediyor'
        start_date = st.date_input("Başlangıç Tarihi", start_date, key=f"start_date_edit_{idx}")
        ongoing = st.checkbox("Devam Ediyor", value=ongoing, key=f"ongoing_edit_{idx}")
        if not ongoing:
            if len(date_parts) > 1 and date_parts[1] != 'Devam Ediyor':
                end_date = datetime.strptime(date_parts[1], "%d.%m.%Y")
            else:
                end_date = datetime.today()
            end_date = st.date_input("Bitiş Tarihi", end_date, key=f"end_date_edit_{idx}")
            end_date_str = end_date.strftime("%d.%m.%Y")
        else:
            end_date_str = 'Devam Ediyor'
        activity_description = st.text_area("Açıklama", act['description'], key=f"description_edit_{idx}")
        show_in_cv = st.checkbox("CV'de Göster", value=act['show_in_cv'], key=f"show_act_edit_{idx}")
        if st.button("Kaydet", key=f"save_act_edit_{idx}"):
            if not community_name.strip() or not role.strip():
                st.error("Topluluk adı ve pozisyon zorunludur.")
            else:
                date_range = f"{start_date.strftime('%d.%m.%Y')} - {'Devam Ediyor' if ongoing else end_date_str}"
                updated_entry = {
                    'name': community_name.strip(),
                    'role': role.strip(),
                    'date_range': date_range,
                    'description': activity_description.strip(),
                    'show_in_cv': show_in_cv
                }
                update_entry('activities', idx, updated_entry)
                st.success("Aktivite güncellendi.")
                st.session_state['edit_section'] = None
                st.session_state['edit_index'] = None
                st.experimental_rerun()
        if st.button("İptal", key=f"cancel_act_edit_{idx}"):
            st.session_state['edit_section'] = None
            st.session_state['edit_index'] = None
            st.experimental_rerun()
    else:
        community_name = st.text_input("Topluluk Adı", key="community_name")
        role = st.text_input("Pozisyon", key="activity_role")
        start_date = st.date_input("Başlangıç Tarihi", value=datetime.today(), key="activity_start_date")
        ongoing = st.checkbox("Devam Ediyor", value=False, key="activity_ongoing")
        if not ongoing:
            end_date = st.date_input("Bitiş Tarihi", value=datetime.today(), key="activity_end_date")
        else:
            end_date = None
        activity_description = st.text_area("Açıklama", key="activity_description")
        show_in_cv = st.checkbox("CV'de Göster", value=True, key="show_activity_cv")
        if st.button("Ekle"):
            if not community_name.strip() or not role.strip():
                st.error("Topluluk adı ve pozisyon zorunludur.")
            else:
                date_range = f"{start_date.strftime('%d.%m.%Y')} - {'Devam Ediyor' if ongoing else end_date.strftime('%d.%m.%Y')}"
                activity_entry = {
                    'name': community_name.strip(),
                    'role': role.strip(),
                    'date_range': date_range,
                    'description': activity_description.strip(),
                    'show_in_cv': show_in_cv
                }
                add_entry('activities', activity_entry)
                st.success("Aktivite eklendi.")
                st.experimental_rerun()

    st.subheader("Eklenen Aktiviteler")
    if not df_activities.empty:
        for idx, act in df_activities.iterrows():
            st.markdown(f"**{act['name']} - {act['role']}**")
            st.markdown(f"   • {act['description']}")
            col1, col2, col3 = st.columns(3)
            with col1:
                if st.button("Düzenle", key=f"edit_act_{idx}_{act['name']}"):
                    st.session_state['edit_section'] = 'activities'
                    st.session_state['edit_index'] = idx
                    st.experimental_rerun()
            with col2:
                if st.button("Sil", key=f"delete_act_{idx}_{act['name']}"):
                    delete_entry('activities', idx)
                    st.success("Aktivite silindi.")
                    st.experimental_rerun()
            with col3:
                show = st.checkbox("CV'de Göster", value=act['show_in_cv'],
                                   key=f"show_act_{idx}_{act['name']}")
                df_activities.at[idx, 'show_in_cv'] = show
        save_data('activities', df_activities)

def skills_section():
    st.header("Beceriler")
    df_skills = load_data('skills')

    if st.session_state.get('edit_section') == 'skills' and st.session_state.get('edit_index') is not None:
        idx = st.session_state['edit_index']
        skill = df_skills.iloc[idx]
        st.write(f"**{skill['name']}** düzenleniyor...")
        skill_name = st.text_input("Beceri Adı", skill['name'], key=f"skill_name_edit_{idx}")
        proficiency = st.text_input("Yeterlilik Seviyesi", skill['proficiency'], key=f"proficiency_edit_{idx}")
        show_in_cv = st.checkbox("CV'de Göster", value=skill['show_in_cv'], key=f"show_skill_edit_{idx}")
        if st.button("Kaydet", key=f"save_skill_edit_{idx}"):
            if not skill_name.strip():
                st.error("Beceri adı zorunludur.")
            else:
                updated_entry = {
                    'name': skill_name.strip(),
                    'proficiency': proficiency.strip(),
                    'show_in_cv': show_in_cv
                }
                update_entry('skills', idx, updated_entry)
                st.success("Beceri güncellendi.")
                st.session_state['edit_section'] = None
                st.session_state['edit_index'] = None
                st.experimental_rerun()
        if st.button("İptal", key=f"cancel_skill_edit_{idx}"):
            st.session_state['edit_section'] = None
            st.session_state['edit_index'] = None
            st.experimental_rerun()
    else:
        skill_name = st.text_input("Beceri Adı", key="skill_name")
        proficiency = st.text_input("Yeterlilik Seviyesi", key="proficiency")
        show_in_cv = st.checkbox("CV'de Göster", value=True, key="show_skill_cv")
        if st.button("Ekle"):
            if not skill_name.strip():
                st.error("Beceri adı zorunludur.")
            else:
                skill_entry = {
                    'name': skill_name.strip(),
                    'proficiency': proficiency.strip(),
                    'show_in_cv': show_in_cv
                }
                add_entry('skills', skill_entry)
                st.success("Beceri eklendi.")
                st.experimental_rerun()

    st.subheader("Eklenen Beceriler")
    if not df_skills.empty:
        for idx, skill in df_skills.iterrows():
            st.markdown(f"**{skill['name']}** - {skill['proficiency']}")
            col1, col2, col3 = st.columns(3)
            with col1:
                if st.button("Düzenle", key=f"edit_skill_{idx}_{skill['name']}"):
                    st.session_state['edit_section'] = 'skills'
                    st.session_state['edit_index'] = idx
                    st.experimental_rerun()
            with col2:
                if st.button("Sil", key=f"delete_skill_{idx}_{skill['name']}"):
                    delete_entry('skills', idx)
                    st.success("Beceri silindi.")
                    st.experimental_rerun()
            with col3:
                show = st.checkbox("CV'de Göster", value=skill['show_in_cv'],
                                   key=f"show_skill_{idx}_{skill['name']}")
                df_skills.at[idx, 'show_in_cv'] = show
        save_data('skills', df_skills)





if DATA_DIR !="":
    # Bölüm seçimine göre ilgili fonksiyonu çağırma
    if selected == "Kişisel Bilgiler":
        personal_info_section()
    elif selected == "Eğitim":
        education_section()
    elif selected == "Projeler":
        projects_section()
    elif selected == "Deneyim":
        experience_section()
    elif selected == "Sertifikalar":
        certifications_section()
    elif selected == "Aktiviteler":
        activities_section()
    elif selected == "Beceriler":
        skills_section()
    elif selected == "CV Asistanı":
        run_cv_bot_app()










def save_cv_as_word(markdown_content, filename):
    doc = Document()
    # Markdown içeriğini parçalara ayır
    sections = markdown_content.split('\n\n')
    for section in sections:
        # Başlıkları kontrol et
        if section.startswith('# '):  # Ana başlık
            doc.add_heading(section[2:], level=1)
        elif section.startswith('## '):  # Alt başlık
            doc.add_heading(section[3:], level=2)
        else:
            doc.add_paragraph(section)
    doc.save(filename)


from docx import Document
from docx.shared import Inches, Pt
from docx.shared import RGBColor
import os
import pandas as pd

import tempfile
from PIL import Image  # Resim işleme için Pillow kütüphanesi


def create_word_document():
    doc = Document()

    # Kişisel Bilgiler
    personal_info = load_personal_info()

    # Kişisel bilgilerin boş olup olmadığını kontrol et
    if 'name' in personal_info and personal_info['name']:
        doc.add_heading(personal_info['name'].upper(), level=2)
    else:
        doc.add_heading("Ad Bilgisi Eksik", level=2)  # Eğer isim yoksa başlık ekleyin

    # İki sütunlu tablo oluştur
    table = doc.add_table(rows=1, cols=2)
    table.autofit = False  # Otomatik boyutlandırmayı devre dışı bırak

    # Sol sütun (Kişisel Bilgiler ve Hesaplar)
    cell1 = table.cell(0, 0)
    cell1.width = Inches(4)  # Sol sütun genişliği

    # E-posta kontrolü
    if 'email' in personal_info and personal_info['email']:
        cell1.add_paragraph(f"E-posta: {personal_info['email']}")
    else:
        cell1.add_paragraph("E-posta bilgisi eksik.")

    # Telefon kontrolü
    if personal_info.get('phone'):
        cell1.add_paragraph(f"Telefon: {personal_info['phone']}")
    else:
        cell1.add_paragraph("Telefon bilgisi eksik.")

    # Hesaplar
    df_accounts = load_data('accounts')
    if not df_accounts.empty:
        for acc in df_accounts.itertuples(index=False):
            cell1.add_paragraph(f"{acc.name}: {acc.link}")

    # Sağ sütun (Fotoğraf)
    cell2 = table.cell(0, 1)
    cell2.width = Inches(2)  # Sağ sütun genişliği

    photo_path = None

    # Kullanıcıdan alınan fotoğraf
    if 'photo' in st.session_state and isinstance(st.session_state['photo'], bytes):
        # Geçici dosya oluştur ve fotoğrafı kaydet
        with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as tmp_file:
            tmp_file.write(st.session_state['photo'])
            photo_path = tmp_file.name

    else:
        # Eğer kişisel bilgilerde fotoğraf yoksa dizinden ilk fotoğrafı al
        directory = "cv_photo"
        photo_path = get_first_photo_from_directory(directory)

        # Fotoğraf dosyasını kontrol et ve ekle
    if photo_path and os.path.exists(photo_path):
        cell2.add_paragraph().add_run().add_picture(photo_path, width=Inches(1.5))
    else:
        cell2.add_paragraph("Fotoğraf mevcut değil.")

    # Eğitim
    df_education = load_data('education')
    if not df_education.empty:
        education = df_education.iloc[0]
        doc.add_heading("EĞİTİM", level=2)
        doc.add_paragraph(
            f"{education.get('university', 'Üniversite bilgisi yok')}, "
            f"{education.get('faculty', 'Fakülte bilgisi yok')} – "
            f"{education.get('department', 'Bölüm bilgisi yok')}, "
            f"{education.get('start_year', 'Başlangıç yılı yok')} - "
            f"{education.get('end_year', 'Bitiş yılı yok')}"
        )

    # Projeler
    df_projects = load_data('projects')
    projects_to_show = df_projects[df_projects['show_in_cv'] == True]
    if not projects_to_show.empty:
        doc.add_heading("PROJELER", level=2)
        for proj in projects_to_show.itertuples(index=False):
            if pd.notnull(proj.title) and isinstance(proj.title, str) and len(proj.title) >= 3:
                doc.add_paragraph(f"• {proj.title}")
                doc.add_paragraph(f"   {proj.description}")
            elif pd.notnull(proj.description) and isinstance(proj.description, str) and len(proj.description) >= 3:
                doc.add_paragraph(f"•  {proj.description}")

            if pd.notnull(proj.technologies) and isinstance(proj.technologies, str) and len(proj.technologies) >= 3:
                doc.add_paragraph(f"   Teknolojiler: {proj.technologies}")

    # Deneyim
    df_experience = load_data('experience')
    experiences_to_show = df_experience[df_experience['show_in_cv'] == True]
    if not experiences_to_show.empty:
        doc.add_heading("DENEYİM", level=2)
        for exp in experiences_to_show.itertuples(index=False):
            doc.add_paragraph(f"• {exp.company} – {exp.position} ({exp.start_date} - {exp.end_date})")
            doc.add_paragraph(f"   {exp.description}")

    # Sertifikalar
    df_certifications = load_data('certifications')
    certifications_to_show = df_certifications[df_certifications['show_in_cv'] == True]
    if not certifications_to_show.empty:
        doc.add_heading("SERTİFİKALAR", level=2)
        for cert in certifications_to_show.itertuples(index=False):
            doc.add_paragraph(f"{cert.name}, {cert.institution} – {cert.date}")

    # Aktiviteler
    df_activities = load_data('activities')
    activities_to_show = df_activities[df_activities['show_in_cv'] == True]
    if not activities_to_show.empty:
        doc.add_heading("AKTİVİTELER", level=2)
        for act in activities_to_show.itertuples(index=False):
            doc.add_paragraph(f"• {act.name} – {act.role} ({act.date_range})")
            doc.add_paragraph(f"   {act.description}")

    # Beceriler
    df_skills = load_data('skills')
    skills_to_show = df_skills[df_skills['show_in_cv'] == True]
    if not skills_to_show.empty:
        doc.add_heading("BECERİLER", level=2)
        for skill in skills_to_show.itertuples(index=False):
            doc.add_paragraph(f"• {skill.name}: {skill.proficiency}")

    # Başlıkların stilini ayarla
    for paragraph in doc.paragraphs:
        if paragraph.style.name == 'Heading 2':
            for run in paragraph.runs:
                run.font.size = Pt(13)
                run.font.color.rgb = RGBColor(0, 0, 0)  # Siyah renk

    return doc



# Streamlit uygulaması
if selected != "CV Asistanı" and DATA_DIR !="":
    # Sağ tarafta CV taslağı
    with st.container():
        col1, col2 = st.columns([4, 1])  # 4: başlık için, 1: buton için

        with col1:
            st.title("CV Taslağı")

        with col2:
            # Word belgesini oluştur
            doc = create_word_document()

            # Belgeyi bellekte tutmak için BytesIO kullanın
            doc_stream = BytesIO()
            doc.save(doc_stream)

            # BytesIO'nun başını sıfırla
            doc_stream.seek(0)

            # Gizli indirme butonu
            st.download_button(
                label="CV'yi İndir",  # Butonun etiketini belirleyin
                data=doc_stream,  # İndirilecek dosya verisi
                file_name="CV.docx",  # İndirilecek dosyanın adı
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",  # MIME tipi
                key="hidden_download_button",  # Butonun anahtarı
                help="CV'nizi indirmek için tıklayın.",  # Yardım metni
                on_click=None,  # Butona tıklanınca çalışacak fonksiyon
                disabled=False,  # Butonun durumunu belirleyin
                use_container_width=True,  # Butonu kapsayıcı genişliğinde yap
                type="secondary"  # Buton türü
            )

        # Sütunlar oluştur
        col1, col2 = st.columns([3, 1])  # 3: sol, 1: sağ

        with col1:
            # 1. İsim ve Kişisel Bilgiler
            personal_info = load_personal_info()
            if personal_info:
                st.header(personal_info.get('name', '').upper())
                st.write(f"**E-posta:** {personal_info.get('email', '')}")
                if personal_info.get('phone'):
                    st.write(f"**Telefon:** {personal_info.get('phone', '')}")

                # Hesaplar
                df_accounts = load_data('accounts')
                if not df_accounts.empty:
                    for acc in df_accounts.itertuples(index=False):
                        st.write(f"**{acc.name}:** {acc.link}")

            # 2. Eğitim
            df_education = load_data('education')
            if not df_education.empty:
                education = df_education.iloc[0]
                st.header("EĞİTİM")
                st.write(
                    f"**{education['university']}, {education['faculty']}** – {education['department']}, {education['start_year']} - {education['end_year']}")

            # 3. Projeler
            df_projects = load_data('projects')
            projects_to_show = df_projects[df_projects['show_in_cv'] == True]
            if not projects_to_show.empty:
                st.header("PROJELER")
                for proj in projects_to_show.itertuples(index=False):
                    # Proje başlığı ve teknolojiler NaN ise boş göster
                    title_display = proj.title if pd.notna(proj.title) and proj.title else " "
                    technologies_display = proj.technologies if pd.notna(
                        proj.technologies) and proj.technologies else " "
                    if title_display != " ":
                        st.markdown(f"• **{title_display}**")


                    if proj.description != "":
                        st.markdown(f" **{proj.description}**")

            # 4. Deneyim
            df_experience = load_data('experience')
            experiences_to_show = df_experience[df_experience['show_in_cv'] == True]

            def parse_date_cv(date_str):
                if date_str == 'Devam Ediyor':
                    return datetime.max
                else:
                    return datetime.strptime(date_str, "%d.%m.%Y")

            experiences_sorted = experiences_to_show.copy()
            experiences_sorted['sort_date'] = experiences_sorted['end_date'].apply(parse_date_cv)
            experiences_sorted.sort_values(by=['sort_date', 'start_date'], ascending=False, inplace=True)

            if not experiences_sorted.empty:
                st.header("DENEYİM")
                for exp in experiences_sorted.itertuples(index=False):
                    st.markdown(f"• **{exp.company} – {exp.position}** ({exp.start_date} - {exp.end_date})")
                    st.markdown(f"   {exp.description}")

            # 5. Sertifikalar
            df_certifications = load_data('certifications')
            certifications_to_show = df_certifications[df_certifications['show_in_cv'] == True]

            if not certifications_to_show.empty:
                certifications_to_show['date'] = certifications_to_show['date'].fillna('None')
                valid_dates = certifications_to_show['date'].astype(str).str.split('.', expand=True)
                valid_dates.columns = ['year', 'month']
                certifications_to_show = certifications_to_show[valid_dates['year'] != 'None']
                certifications_to_show[['year', 'month']] = valid_dates[['year', 'month']].astype(int)
                certifications_to_show = certifications_to_show.sort_values(by=['year', 'month'], ascending=False)

                st.header("SERTİFİKALAR")
                for cert in certifications_to_show.itertuples(index=False):
                    st.markdown(f"• **{cert.name}**, {cert.institution} – {cert.date}")

            # 6. Aktiviteler
            df_activities = load_data('activities')
            activities_to_show = df_activities[df_activities['show_in_cv'] == True]
            if not activities_to_show.empty:
                st.header("AKTİVİTELER")
                for act in activities_to_show.itertuples(index=False):
                    st.markdown(f"• **{act.name} – {act.role}** ({act.date_range})")
                    st.markdown(f"   {act.description}")

            # 7. Beceriler
            df_skills = load_data('skills')
            skills_to_show = df_skills[df_skills['show_in_cv'] == True]
            if not skills_to_show.empty:
                st.header("BECERİLER")
                for skill in skills_to_show.itertuples(index=False):
                    st.markdown(f"• **{skill.name}:** {skill.proficiency}")

        with col2:
            # Fotoğrafı sağ üst köşeye yerleştir
            if st.session_state.get('photo'):
                st.image(st.session_state['photo'], width=150)
            else:
                # Eğer kişisel bilgilerde fotoğraf yoksa dizinden ilk fotoğrafı al
                first_photo_path = get_first_photo_from_directory(photo_folder_path)
                if first_photo_path:
                    st.image(first_photo_path, width=150)
                else:
                    st.write("Henüz bir fotoğraf yüklenmedi.")


