DROP TABLE IF EXISTS classes;

CREATE TABLE classes(
    id integer PRIMARY KEY AUTOINCREMENT,
    class_name TEXT NOT NULL UNIQUE
);
    
