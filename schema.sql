drop tble if exists noticias;
create table noticias (
  id integer primary key autoincrement,
  title text not null,
  content text not null
);