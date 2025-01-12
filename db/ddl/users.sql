CREATE TABLE users (
    id integer PRIMARY KEY,
    name text,
    status text,
    city text,
    address text,
    region_id integer,
    ogrn bigint,
    inn bigint UNIQUE,
    activity text,
    date text,
    constraint fk_users_region_id foreign key (region_id) references region (id)
    );
