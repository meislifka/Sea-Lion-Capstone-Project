db.execute("CREATE TABLE sealions(sealionID, sex, encounter)")
db.execute("CREATE TABLE encounters(encounter, sealionID, year, month, day, timeofday, location)")
db.execute("INSERT INTO sealions(name, age) VALUES('John', '21')")
CREATE TABLE sealion
(
    id INTEGER,
    sex TEXT,
    encounter TEXT,
    encounter_id INTEGER,
    PRIMARY KEY(id),
    FOREGIN KEY(encounter_id) REFERENCES encounters(id)
);

 CREATE TABLE encounter
(
    id INTEGER,
    user TEXT,
    sealion_id INTEGER,
    year INTEGER,
    month INTEGER,
    day INTEGER,
    timeofday INTEGER,
    location TEXT,
    PRIMARY KEY(id)
);

    FOREGIN KEY(sealion_id) REFERENCES sealion(id)
