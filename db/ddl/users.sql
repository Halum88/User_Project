CREATE TABLE users (
    id integer PRIMARY KEY,
    name text,
    status text,
    city text,
    address text,
    region_id integer,
    ogrn bigint,
    inn bigint UNIQUE,
    acticity text,
    date_registr text,
    constraint fk_users_region_id foreign key (region_id) references region (id)
    );
