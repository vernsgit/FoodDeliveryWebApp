from database.database import get_db
import os
from flask import current_app
class MenuService:
    #left join umožnuje vybrat předměty s akcemi vramci aktualniho data + předměty co nejsou vramci akce
    @staticmethod
    def get_menu_items(restaurant_id):
        db = get_db()
        cursor = db.cursor()
        sql = """SELECT j.id_jidla,j.nazev,j.cena,j.cena_nakladu,j.dostupnost,j.foto_jidla,j.typ_jidla,a.nazev_akce,a.sleva_procenta,a.zacatek,a.konec
                FROM jidla j
                LEFT JOIN jidlo_vazby ja ON j.id_jidla = ja.id_jidla
                LEFT JOIN akce a ON ja.id_akce = a.id_akce AND a.zacatek <= datetime('now', 'localtime') AND a.konec >= datetime('now', 'localtime') 
                WHERE j.id_restaurace = ?"""
        return cursor.execute(sql, [restaurant_id]).fetchall()

    @staticmethod
    def get_menu_items_client(restaurant_id):
        db = get_db()
        cursor = db.cursor()
        sql = """SELECT j.id_jidla,j.nazev,j.cena,j.cena_nakladu,j.dostupnost,j.foto_jidla,j.typ_jidla,a.nazev_akce,a.sleva_procenta,a.zacatek,a.konec
                FROM jidla j
                LEFT JOIN jidlo_vazby ja ON j.id_jidla = ja.id_jidla
                LEFT JOIN akce a ON ja.id_akce = a.id_akce 
                           AND a.zacatek <= datetime('now', 'localtime') 
                           AND a.konec >= datetime('now', 'localtime') 
                WHERE 
                    j.id_restaurace = ? AND j.dostupnost = 1
            """
        return cursor.execute(sql, [restaurant_id]).fetchall()

    @staticmethod
    def add_menu_item(restaurant_id, name, price, cost, item_type, photo_path):
        db = get_db()
        cursor = db.cursor()
        sql_check = """SELECT COUNT(*) as pocet from jidla where id_restaurace = ?"""
        query_check = cursor.execute(sql_check, [restaurant_id]).fetchone()
        if query_check['pocet'] >=24:
            return None

        sql = """ INSERT INTO jidla (nazev, cena, cena_nakladu, dostupnost, foto_jidla, typ_jidla, id_restaurace) VALUES (?, ?, ?, 1, ?, ?, ?)"""
        cursor.execute(sql, [name, price, cost, photo_path, item_type, restaurant_id])
        db.commit()
        return cursor.lastrowid

    @staticmethod
    def delete_menu_item(item_id):
        db = get_db()
        cursor = db.cursor()

        sql_select = """SELECT foto_jidla FROM jidla WHERE id_jidla = ?"""
        result = cursor.execute(sql_select, [item_id]).fetchone()

        if result:
            foto_jidla = result['foto_jidla']
            if foto_jidla:
                sql_check = """SELECT COUNT(*) AS pocet FROM jidla WHERE foto_jidla = ? AND id_jidla != ?"""
                count_result = cursor.execute(sql_check, [foto_jidla, item_id]).fetchone()

                if count_result and count_result['pocet'] == 0:
                    foto_path = os.path.join(current_app.root_path, 'static', foto_jidla)
                    if os.path.exists(foto_path):
                        os.remove(foto_path)

        sql_select_vazby = """SELECT id_akce FROM jidlo_vazby WHERE id_jidla = ?"""
        vazby = cursor.execute(sql_select_vazby, [item_id]).fetchall()

        for vazba in vazby:
            id_akce = vazba['id_akce']

            sql_check_akce = """SELECT COUNT(*) AS pocet FROM jidlo_vazby WHERE id_akce = ? AND id_jidla != ?"""
            count_akce_result = cursor.execute(sql_check_akce, [id_akce, item_id]).fetchone()

            if count_akce_result and count_akce_result['pocet'] == 0:
                sql_delete_akce = """DELETE FROM akce WHERE id_akce = ?"""
                cursor.execute(sql_delete_akce, [id_akce])

        sql_delete_vazby = """DELETE FROM jidlo_vazby WHERE id_jidla = ?"""
        cursor.execute(sql_delete_vazby, [item_id])

        sql_delete_jidlo = """DELETE FROM jidla WHERE id_jidla = ?"""
        cursor.execute(sql_delete_jidlo, [item_id])
        db.commit()

    @staticmethod
    def update_availability(item_id, dostupnost):
        db = get_db()
        cursor = db.cursor()
        sql = """
            UPDATE jidla
            SET dostupnost = ?
            WHERE id_jidla = ?
        """
        cursor.execute(sql, [dostupnost, item_id])
        db.commit()
        cursor.close()

    @staticmethod
    def get_availability(item_id):
        db = get_db()
        cursor = db.cursor()
        sql = """SELECT dostupnost FROM jidla WHERE id_jidla = ?"""
        result = cursor.execute(sql, [item_id]).fetchone()

        if result:
            return result['dostupnost']
        return None



    @staticmethod
    def add_discount_action(restaurant_id, name, discount, start, end, item_ids):
        db = get_db()
        cursor = db.cursor()

        sql_check = """
            SELECT COUNT(*) AS pocet
            FROM akce
            WHERE id_restaurace = ? AND (
                (? BETWEEN zacatek AND konec OR ? BETWEEN zacatek AND konec) OR
                (zacatek BETWEEN ? AND ?) OR
                (konec BETWEEN ? AND ?)
            )
        """
        formatted_start = start.strftime("%Y-%m-%d %H:%M:%S")
        formatted_end = end.strftime("%Y-%m-%d %H:%M:%S")

        overlap_result = cursor.execute(
            sql_check,
            [restaurant_id, formatted_start, formatted_end, formatted_start, formatted_end, formatted_start,
             formatted_end]
        ).fetchone()

        if overlap_result['pocet'] > 0:
            return None  #Konflikt s existující akcí

        sql_insert = """
            INSERT INTO akce (nazev_akce, sleva_procenta, zacatek, konec, id_restaurace)
            VALUES (?, ?, ?, ?, ?)
        """
        cursor.execute(sql_insert, [name, discount, formatted_start, formatted_end, restaurant_id])
        db.commit()

        discount_action_id = cursor.lastrowid
        for item_id in item_ids:
            sql_check_link = """
                SELECT COUNT(*) AS pocet
                FROM jidlo_vazby
                WHERE id_jidla = ? AND id_akce = ?
            """
            link_check_result = cursor.execute(sql_check_link, [item_id, discount_action_id]).fetchone()

            if link_check_result['pocet'] == 0:
                sql_insert_link = """
                    INSERT INTO jidlo_vazby (id_jidla, id_akce)
                    VALUES (?, ?)
                """
                cursor.execute(sql_insert_link, [item_id, discount_action_id])

        db.commit()
        return discount_action_id

    @staticmethod
    def get_discount_actions(restaurant_id):
        db = get_db()
        cursor = db.cursor()
        sql = """
               SELECT id_akce, nazev_akce, sleva_procenta, strftime('%d.%m.%Y %H:%M', zacatek) AS zacatek, strftime('%d.%m.%Y %H:%M', konec) AS konec
               FROM akce
               WHERE id_restaurace = ?
                 AND konec >= datetime('now', 'localtime') 
           """
        return cursor.execute(sql, [restaurant_id]).fetchall()

    @staticmethod
    def delete_action(action_id):
        db = get_db()
        cursor = db.cursor()
        sql_delete_vazby = "DELETE FROM jidlo_vazby WHERE id_akce = ?"
        cursor.execute(sql_delete_vazby, [action_id])

        sql_delete_action = "DELETE FROM akce WHERE id_akce = ?"
        cursor.execute(sql_delete_action, [action_id])

        db.commit()

    @staticmethod
    def delete_expired_actions():
        db = get_db()
        cursor = db.cursor()

        sql= """
            DELETE FROM jidlo_vazby
            WHERE id_akce IN (
                SELECT id_akce FROM akce WHERE konec < datetime('now', 'localtime') 
            )
        """
        cursor.execute(sql)

        sql_delete_actions = """
            DELETE FROM akce WHERE konec < datetime('now', 'localtime') 
        """
        cursor.execute(sql_delete_actions)

        db.commit()
        cursor.close()