from database.database import get_db
import os
from flask import current_app

class Restaurant_info:
    @staticmethod
    def get_all_restaurace():
        db = get_db()
        cursor = db.cursor()
        sql = """
            SELECT r.id_restaurace, r.nazev, r.info, r.adresa, r.druh_kuchyne, r.foto_restaurace
            FROM restaurace r
            WHERE EXISTS (
                SELECT 1 
                FROM jidla j
                WHERE j.id_restaurace = r.id_restaurace
            )
        """
        return cursor.execute(sql).fetchall()

    @staticmethod
    def get_restaurace(user_id: int):
        db = get_db()
        cursor = db.cursor()
        sql = """
            SELECT id_restaurace, nazev, info, adresa, druh_kuchyne, foto_restaurace
            FROM restaurace
            WHERE id_uzivatele = ?
        """
        return cursor.execute(sql, [user_id]).fetchone()

    @staticmethod
    def create_restaurace(user_id: int, nazev: str, info: str, adresa: str, druh_kuchyne: str, foto: str):
        db = get_db()
        cursor = db.cursor()
        sql = """
            INSERT INTO restaurace (id_uzivatele, nazev, info, adresa, druh_kuchyne, foto_restaurace)
            VALUES (?, ?, ?, ?, ?, ?)
        """
        cursor.execute(sql, [user_id, nazev, info, adresa, druh_kuchyne, foto])
        db.commit()

    @staticmethod
    def delete_restaurace(user_id: int):
        db = get_db()
        cursor = db.cursor()

        sql_get_restaurant = """SELECT id_restaurace FROM restaurace WHERE id_uzivatele = ?"""
        result = cursor.execute(sql_get_restaurant, [user_id]).fetchone()

        if not result:
            raise ValueError("Restaurace pro tohoto uživatele neexistuje.")

        user_folder = os.path.join(current_app.config['UPLOAD_FOLDER'], str(user_id))
        if os.path.exists(user_folder):
            import shutil
            shutil.rmtree(user_folder)

        sql_delete_food_links = """DELETE FROM jidlo_vazby WHERE id_jidla IN (SELECT id_jidla FROM jidla WHERE id_restaurace = ?)"""
        cursor.execute(sql_delete_food_links, [result['id_restaurace']])

        sql_delete_food = """DELETE FROM jidla WHERE id_restaurace = ?"""
        cursor.execute(sql_delete_food, [result['id_restaurace']])

        sql_delete_actions = """DELETE FROM akce WHERE id_restaurace = ?"""
        cursor.execute(sql_delete_actions, [result['id_restaurace']])

        sql_delete_restaurant = """DELETE FROM restaurace WHERE id_uzivatele = ?"""
        cursor.execute(sql_delete_restaurant, [user_id])

        db.commit()

    @staticmethod
    def get_restaurace_by_id(restaurant_id):
        db = get_db()
        cursor = db.cursor()
        sql = """
            SELECT id_restaurace, nazev, info, adresa, druh_kuchyne, foto_restaurace
            FROM restaurace
            WHERE id_restaurace = ?
        """
        return cursor.execute(sql, [restaurant_id]).fetchone()


