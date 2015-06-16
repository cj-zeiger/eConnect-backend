CREATE TABLE IF NOT EXISTS interactions(
	id      integer primary key autoincrement not null,
        name    text not null,
	count   integer default 0 not null
 );
