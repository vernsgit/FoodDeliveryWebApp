from database.database import get_db

class RoleService:
    @staticmethod
    def update_role(user_id: int, role_type: str) -> bool:
        db = get_db()
        try:
            db.execute(
                """UPDATE uzivatele SET role = ? WHERE id_uzivatele = ?""",
                (role_type, user_id)
            )
            db.commit()
            return True
        except Exception as e:
            print(f"Error inserting role request: {e}")
            db.rollback()
            return False

    @staticmethod
    def insert_role_request(user_id: int, role_type: str, state: str) -> bool:
        db = get_db()
        try:
            db.execute(
                """INSERT INTO zadost_role (id_uzivatele, typ_role, stav_zadosti) VALUES (?, ?, ?)""",
                (user_id, role_type, state)
            )
            db.commit()
            return True
        except Exception as e:
            print(f"Error inserting role request: {e}")
            db.rollback()
            return False

    @staticmethod
    def get_requests(user_id: int):
        db = get_db()
        try:
            cursor = db.cursor()
            sql = """
            SELECT typ_role, stav_zadosti, strftime('%d.%m.%Y %H:%M:%S', datum_zadosti) AS datum_zadosti
            FROM zadost_role
            WHERE id_uzivatele = ?
            ORDER BY datum_zadosti DESC
            """
            result = cursor.execute(sql, (user_id,)).fetchall()
            return result
        except Exception as e:
            print(f"Error fetching requests by user: {e}")
            return None

###
    @staticmethod
    def update_role(user_id: int, role_type: str) -> bool:
        db = get_db()
        try:
            db.execute(
                """UPDATE uzivatele SET role = ? WHERE id_uzivatele = ?""",
                (role_type, user_id)
            )
            db.commit()
            return True
        except Exception as e:
            print(f"Error updating role: {e}")
            db.rollback()
            return False

    @staticmethod
    def update_request_status(request_id: int, status: str) -> bool:
        db = get_db()
        try:
            db.execute(
                """UPDATE zadost_role SET stav_zadosti = ? WHERE id_zadosti = ?""",
                (status, request_id)
            )
            db.commit()
            return True
        except Exception as e:
            print(f"Error updating request status: {e}")
            db.rollback()
            return False

    @staticmethod
    def get_pending_requests():
        db = get_db()
        try:
            return db.execute(
                """SELECT zr.id_zadosti, u.id_uzivatele, u.jmeno, u.prijmeni, u.email, zr.typ_role, strftime('%d.%m.%Y %H:%M:%S', zr.datum_zadosti) as datum_zadosti
                FROM zadost_role zr 
                JOIN uzivatele u ON zr.id_uzivatele = u.id_uzivatele 
                WHERE zr.stav_zadosti = 'čekající'
                ORDER BY datum_zadosti DESC"""
            ).fetchall()
        except Exception as e:
            print(f"Error fetching pending requests: {e}")
            return []

    @staticmethod
    def get_request_details(request_id: int):
        db = get_db()
        try:
            return db.execute(
                """SELECT id_uzivatele, typ_role FROM zadost_role WHERE id_zadosti = ?""",
                (request_id,)
            ).fetchone()
        except Exception as e:
            print(f"Error fetching request details: {e}")
            return None

    @staticmethod
    def get_current_role(user_id: int):
        db = get_db()
        cursor = db.cursor()
        sql = "SELECT role FROM uzivatele WHERE id_uzivatele = ?"
        result = cursor.execute(sql, [user_id]).fetchone()
        return result['role'] if result else None