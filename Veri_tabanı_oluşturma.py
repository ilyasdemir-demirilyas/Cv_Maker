import sqlite3

def get_connection():
    return sqlite3.connect('database.db')

def create_tables():
    conn = get_connection()
    c = conn.cursor()

    create_users_table = '''
    CREATE TABLE IF NOT EXISTS Users (
        user_id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT NOT NULL UNIQUE,
        password TEXT NOT NULL,
        email TEXT NOT NULL UNIQUE,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    );
    '''

    create_personal_info_table = '''
    CREATE TABLE IF NOT EXISTS PersonalInfo (
        info_id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER UNIQUE,  -- Benzersiz yapıldı
        name TEXT,
        email TEXT,
        phone TEXT,
        FOREIGN KEY (user_id) REFERENCES Users(user_id) ON DELETE CASCADE  -- Silindiğinde kişisel bilgileri de sil
    );
    '''

    create_photos_table = '''
    CREATE TABLE IF NOT EXISTS Photos (
        photo_id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        photo BLOB,  -- Fotoğraf verisi
        FOREIGN KEY (user_id) REFERENCES Users(user_id) ON DELETE CASCADE  -- Kullanıcı silindiğinde fotoğraflar da silinsin
    );'''


    create_education_table = '''
    CREATE TABLE IF NOT EXISTS Education (
        edu_id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        university TEXT,
        faculty TEXT,
        department TEXT,
        start_year INTEGER,
        end_year INTEGER,
        show_in_cv BOOLEAN,
        FOREIGN KEY (user_id) REFERENCES Users(user_id) ON DELETE CASCADE  -- Silindiğinde eğitim bilgilerini de sil
    );
    '''

    create_projects_table = '''
    CREATE TABLE IF NOT EXISTS Projects (
        project_id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        title TEXT,
        description TEXT,
        technologies TEXT,
        show_in_cv BOOLEAN,
        FOREIGN KEY (user_id) REFERENCES Users(user_id) ON DELETE CASCADE  -- Silindiğinde proje bilgilerini de sil
    );
    '''

    create_experience_table = '''
    CREATE TABLE IF NOT EXISTS Experience (
        exp_id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        company TEXT,
        position TEXT,
        start_date DATE,
        end_date DATE,
        description TEXT,
        show_in_cv BOOLEAN,
        FOREIGN KEY (user_id) REFERENCES Users(user_id) ON DELETE CASCADE  -- Silindiğinde deneyim bilgilerini de sil
    );
    '''

    create_certifications_table = '''
    CREATE TABLE IF NOT EXISTS Certifications (
        cert_id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        name TEXT,
        institution TEXT,
        date DATE,
        show_in_cv BOOLEAN,
        FOREIGN KEY (user_id) REFERENCES Users(user_id) ON DELETE CASCADE  -- Silindiğinde sertifikaları da sil
    );
    '''

    create_activities_table = '''
    CREATE TABLE IF NOT EXISTS Activities (
        activity_id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        name TEXT,
        role TEXT,
        date_range TEXT,
        description TEXT,
        show_in_cv BOOLEAN,
        FOREIGN KEY (user_id) REFERENCES Users(user_id) ON DELETE CASCADE  -- Silindiğinde aktiviteleri de sil
    );
    '''

    create_skills_table = '''
    CREATE TABLE IF NOT EXISTS Skills (
        skill_id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        name TEXT,
        proficiency TEXT,
        show_in_cv BOOLEAN,
        FOREIGN KEY (user_id) REFERENCES Users(user_id) ON DELETE CASCADE  -- Silindiğinde becerileri de sil
    );
    '''

    create_accounts_table = '''
    CREATE TABLE IF NOT EXISTS Accounts (
        account_id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        name TEXT,
        link TEXT,
        show_in_cv BOOLEAN,
        FOREIGN KEY (user_id) REFERENCES Users(user_id) ON DELETE CASCADE  -- Silindiğinde hesapları da sil
    );
    '''

    c.execute(create_users_table)
    c.execute(create_photos_table)
    c.execute(create_personal_info_table)
    c.execute(create_education_table)
    c.execute(create_projects_table)
    c.execute(create_experience_table)
    c.execute(create_certifications_table)
    c.execute(create_activities_table)
    c.execute(create_skills_table)
    c.execute(create_accounts_table)

    conn.commit()
    conn.close()



