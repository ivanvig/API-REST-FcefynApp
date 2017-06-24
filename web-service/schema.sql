drop table if exists PUBLICACIONES;
CREATE TABLE PUBLICACIONES
(
  id integer PRIMARY KEY AUTOINCREMENT,
  title text NOT NULL,
  content text NOT NULL,
  fecha NUMERIC
);