from database.database import get_db


class UserInfo:
    @staticmethod
    def get_user_info(user_id: int):
        db = get_db()
        cursor = db.cursor()
        sql = "SELECT id_uzivatele, jmeno, prijmeni, email, telefon, role, strftime('%d.%m.%Y %H:%M:%S', datum_registrace) AS datum_registrace FROM uzivatele WHERE id_uzivatele=?"
        user = cursor.execute(sql, [user_id]).fetchone()
        if user is None:
            return
        else:
            return user

    @staticmethod
    def update_info(user_id: int, telefon:int, adresa:str):
        db = get_db()
        cursor = db.cursor()
        sql = """UPDATE uzivatele SET telefon = ?, adresa = ? WHERE id_uzivatele = ?"""
        cursor.execute(sql, [telefon, adresa, user_id])
        db.commit()