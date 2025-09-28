import hashlib
from database.database import get_db
import config


class UserService:
    @staticmethod
    def hash_password(password: str) -> str:
        salted_password = password + config.PASSWORD_SALT
        hashed_password = hashlib.sha256(salted_password.encode()).hexdigest()

        return hashed_password

    @staticmethod
    def login(email: str, password: str):
        password_try = UserService.hash_password(password)
        db = get_db()
        cursor = db.cursor()
        sql = "SELECT id_uzivatele, email, role FROM uzivatele WHERE email=? and heslo=?"
        user = cursor.execute(sql, [email, password_try]).fetchone()
        if user is None:
            return
        else:
            return user


    @staticmethod
    def register_user(jmeno: str, prijmeni: str, email: str, password: str, telefon: str) -> int:
        db = get_db()
        cursor = db.cursor()


        existing_user = cursor.execute("SELECT * FROM uzivatele WHERE email=?", (email,)).fetchone()
        if existing_user:
            return 0

        hashed_password = UserService.hash_password(password)
        try:
            cursor.execute(
                'INSERT INTO uzivatele (jmeno, prijmeni, email, heslo, telefon) VALUES (?, ?, ?, ?, ?)',(jmeno, prijmeni, email, hashed_password, telefon)
            )
            db.commit()
            return 2

        except Exception as e:
            print(f"Error creating user: {e}")
            db.rollback()
            return 1

##
    @staticmethod
    def create_user(jmeno:str, prijmeni:str, email:str, password:str, telefon:str, adresa:str, role:str) -> bool:
        db = get_db()
        hashed_password = UserService.hash_password(password)

        try:
            db.execute(
                'INSERT INTO uzivatele (jmeno, prijmeni, email, heslo, telefon, adresa, role) VALUES (?, ?, ?, ?, ?, ?, ?)',
                (jmeno, prijmeni, email, hashed_password, telefon, adresa, role)
            )
            db.commit()
            return True
        except Exception as e:
            print(f"Error creating user: {e}")
            db.rollback()

            return False

    @staticmethod
    def change_password(user_id: int, old_password: str, new_password: str) -> bool:
        db = get_db()
        cursor = db.cursor()
        query = 'SELECT heslo FROM uzivatele WHERE id_uzivatele = ?'
        user = cursor.execute(query, (user_id,)).fetchone()

        if user:
            stored_hash = user['heslo']
            hashed_old_password = UserService.hash_password(old_password)

            if stored_hash == hashed_old_password:
                hashed_new_password = UserService.hash_password(new_password)
                update_query = 'UPDATE uzivatele SET heslo = ? WHERE id_uzivatele = ?'
                cursor.execute(update_query, (hashed_new_password, user_id))
                db.commit()
                return True
            else:
                return False
        return False
