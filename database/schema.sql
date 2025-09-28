DROP TABLE IF EXISTS uzivatele;
DROP TABLE IF EXISTS restaurace;
DROP TABLE IF EXISTS akce;
DROP TABLE IF EXISTS jidla;
DROP TABLE IF EXISTS objednavky;
DROP TABLE IF EXISTS polozky_objednavky;
DROP TABLE IF EXISTS prijmy_system;
DROP TABLE IF EXISTS transakce;
DROP TABLE IF EXISTS poslicci;
DROP TABLE IF EXISTS zadost_role;
DROP TABLE IF EXISTS jidlo_vazby;


CREATE TABLE uzivatele (
    id_uzivatele INTEGER PRIMARY KEY AUTOINCREMENT,
    jmeno TEXT NOT NULL,
    prijmeni TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    heslo TEXT NOT NULL,
    telefon TEXT NOT NULL,
    adresa TEXT NULL,
    role TEXT CHECK(role IN ('klient', 'restauratér', 'poslíček', 'administrátor')) DEFAULT 'klient',
    datum_registrace TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE zadost_role(
    id_zadosti INTEGER PRIMARY KEY AUTOINCREMENT,
    id_uzivatele INTEGER NOT NULL,
    typ_role TEXT CHECK(typ_role IN ('restauratér', 'poslíček', 'klient')) NOT NULL,
    stav_zadosti TEXT CHECK(stav_zadosti IN ('čekající', 'schváleno', 'zamítnuto')) DEFAULT 'čekající',
    datum_zadosti TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (id_uzivatele) REFERENCES uzivatele (id_uzivatele)
);

CREATE TABLE restaurace (
    id_restaurace INTEGER PRIMARY KEY AUTOINCREMENT,
    nazev TEXT NOT NULL,
    info TEXT,
    adresa TEXT NOT NULL,
    druh_kuchyne TEXT NOT NULL,
    foto_restaurace TEXT NOT NULL,
    id_uzivatele INTEGER NOT NULL,
    FOREIGN KEY (id_uzivatele) REFERENCES uzivatele (id_uzivatele)
);

CREATE TABLE akce (
    id_akce INTEGER PRIMARY KEY AUTOINCREMENT,
    nazev_akce TEXT NOT NULL,
    sleva_procenta INTEGER CHECK(sleva_procenta BETWEEN 0 AND 100),
    zacatek TIMESTAMP NOT NULL,
    konec TIMESTAMP NOT NULL,
    id_restaurace INTEGER NOT NULL,
    FOREIGN KEY (id_restaurace) REFERENCES restaurace (id_restaurace)
);

CREATE TABLE jidla (
    id_jidla INTEGER PRIMARY KEY AUTOINCREMENT,
    nazev TEXT NOT NULL,
    cena REAL NOT NULL,
    cena_nakladu REAL NOT NULL,
    dostupnost INTEGER DEFAULT 1,
    foto_jidla TEXT NOT NULL,
    typ_jidla TEXT CHECK(typ_jidla IN ('pití','chod')) DEFAULT 'chod',
    id_restaurace INTEGER NOT NULL,
    FOREIGN KEY (id_restaurace) REFERENCES restaurace (id_restaurace)
);

CREATE TABLE jidlo_vazby (
    id_jidla INTEGER NOT NULL,
    id_akce INTEGER NOT NULL,
    PRIMARY KEY (id_jidla, id_akce),
    FOREIGN KEY (id_jidla) REFERENCES jidla (id_jidla),
    FOREIGN KEY (id_akce) REFERENCES akce (id_akce)
);


CREATE TABLE objednavky (
    id_objednavky INTEGER PRIMARY KEY AUTOINCREMENT,
    id_klienta INTEGER NOT NULL,
    id_restaurace INTEGER NOT NULL,
    id_poslicka INTEGER,
    stav_objednavky TEXT CHECK(stav_objednavky IN ('cekajici', 'v_priprave', 'na_ceste', 'doruceno', 'zruseno')) DEFAULT 'cekajici',
    zpusob_platby TEXT CHECK(zpusob_platby IN ('online', 'dobirka')) NOT NULL,

    cena_celkem_polozky REAL NOT NULL,
    cena_celkem_naklady REAL NOT NULL,
    naklady_za_dovoz REAL NOT NULL,

    datum_vytvoreni TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    cas_doruceni DATETIME,
    FOREIGN KEY (id_klienta) REFERENCES uzivatele (id_uzivatele),
    FOREIGN KEY (id_restaurace) REFERENCES restaurace (id_restaurace),
    FOREIGN KEY (id_poslicka) REFERENCES poslicci (id_poslicka)
);

CREATE TABLE polozky_objednavky (
    id_polozky INTEGER PRIMARY KEY AUTOINCREMENT,
    id_objednavky INTEGER NOT NULL,
    id_jidla INTEGER NOT NULL,
    mnozstvi INTEGER NOT NULL,
    cena_polozek REAL NOT NULL,
    cena_nakladu_polozek REAL NOT NULL,
    FOREIGN KEY (id_objednavky) REFERENCES objednavky (id_objednavky),
    FOREIGN KEY (id_jidla) REFERENCES jidla (id_jidla)
);

CREATE TABLE prijmy_system (
    id_prijmu INTEGER PRIMARY KEY AUTOINCREMENT,
    /*procento_z_prijmu REAL NOT NULL,*/
    zisk_z_prijmu REAL NOT NULL,
    id_objednavky INTEGER NOT NULL,
    FOREIGN KEY (id_objednavky) REFERENCES objednavky (id_objednavky)
);

CREATE TABLE transakce (
    id_transakce INTEGER PRIMARY KEY AUTOINCREMENT,
    id_objednavky INTEGER NOT NULL,
    stav_transakce TEXT CHECK(stav_transakce IN ('ceka_na_schvaleni', 'dokonceno', 'zruseno')) DEFAULT 'ceka_na_schvaleni',
    castka_s_danemi REAL NOT NULL,
    cas_transakce TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (id_objednavky) REFERENCES objednavky (id_objednavky)
);

CREATE TABLE poslicci (
    id_poslicka INTEGER PRIMARY KEY AUTOINCREMENT,
    aktivni INTEGER NOT NULL CHECK(aktivni IN (0, 1)) DEFAULT 1,
    id_uzivatele INTEGER NOT NULL,
    FOREIGN KEY (id_uzivatele) REFERENCES uzivatele (id_uzivatele)
);