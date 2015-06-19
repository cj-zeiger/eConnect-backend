CREATE TABLE IF NOT EXISTS users(
	id      integer primary key autoincrement not null,
  name    text not null,
	count   integer default 0 not null
 );
CREATE TABLE IF NOT EXISTS interactions(
  transaction_id  integer PRIMARY KEY AUTOINCREMENT NOT NULL,
  user_id_1 integer NOT NULL,
  user_id_2 integer NOT NULL,
  transaction_time timestamp NOT NULL
);