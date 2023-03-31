CREATE TABLE companies (
    id integer GENERATED BY DEFAULT AS IDENTITY PRIMARY KEY,
    name text,
    status text,
    city text,
    manager text,
    address text,
    region_id integer,
    ogrn bigint,
    inn bigint UNIQUE,
    capital text,
    activity text,
    date text,
    constraint fk_users_region_id foreign key (region_id) references region (id)
);