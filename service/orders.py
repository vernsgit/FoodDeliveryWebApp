from database.database import get_db

class Orders:
    @staticmethod
    def cart_item(item_id):
        db = get_db()
        cursor = db.cursor()

        sql = """
            SELECT 
                j.id_jidla,
                j.nazev,
                j.cena,
                j.cena_nakladu,
                j.dostupnost,
                j.foto_jidla,
                j.typ_jidla,
                a.id_akce,
                a.nazev_akce,
                a.sleva_procenta,
                a.zacatek,
                a.konec
            FROM jidla j
            LEFT JOIN jidlo_vazby ja ON j.id_jidla = ja.id_jidla
            LEFT JOIN 
                akce a ON ja.id_akce = a.id_akce 
                       AND a.zacatek <= datetime('now', 'localtime') 
                       AND a.konec >= datetime('now', 'localtime') 
            WHERE j.id_jidla = ? AND j.dostupnost = 1"""

        cursor.execute(sql, [item_id])
        result = cursor.fetchone()

        if result:
            item_info = {
                'id_jidla': result['id_jidla'],
                'nazev': result['nazev'],
                'cena': result['cena'],
                'cena_nakladu': result['cena_nakladu'],
                'dostupnost': result['dostupnost'],
                'foto_jidla': result['foto_jidla'],
                'typ_jidla': result['typ_jidla'],
                'akce': {
                    'nazev_akce': result['nazev_akce'],
                    'sleva_procenta': result['sleva_procenta'],
                    'zacatek': result['zacatek'],
                    'konec': result['konec']
                } if result['id_akce'] else None
            }
            return item_info
        return None

    @staticmethod
    def save_order(user_id, restaurant_id, items, transport_costs, total_price, payment_method):
        db = get_db()
        cursor = db.cursor()
        total_costs = sum(item['cena_nakladu'] for item in items)
        transport__costs = transport_costs
        sales = sum(item['mnozstvi'] * item['cena'] for item in items)

        sql_order = """
                INSERT INTO objednavky(
                    id_klienta, id_restaurace, stav_objednavky, zpusob_platby,
                    cena_celkem_polozky, cena_celkem_naklady, naklady_za_dovoz
                )VALUES(?, ?, 'cekajici', ?, ?, ?, ?)"""

        cursor.execute(sql_order,[user_id, restaurant_id, payment_method,sales, total_costs, transport__costs])
        order_id = cursor.lastrowid

        sql_item = """INSERT INTO polozky_objednavky (id_objednavky, id_jidla, mnozstvi, cena_polozek, cena_nakladu_polozek)
                    VALUES (?, ?, ?, ?, ?) """
        for item in items:
            cursor.execute(sql_item,[order_id, item['id_jidla'], item['mnozstvi'], item['cena_itemu'], item['mnozstvi'] * item['cena']])

        db.commit()
        return order_id

    @staticmethod
    def get_user_orders(user_id):
        db = get_db()
        cursor = db.cursor()
        sql = """
        SELECT id_objednavky,stav_objednavky,zpusob_platby, strftime('%d.%m.%Y %H:%M', datum_vytvoreni) AS datum_vytvoreni
        FROM objednavky
        WHERE id_klienta = ?
        ORDER BY datum_vytvoreni DESC"""
        cursor.execute(sql, [user_id])
        orders = cursor.fetchall()
        return orders