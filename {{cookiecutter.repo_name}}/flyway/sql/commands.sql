CREATE TABLE children (
    id serial PRIMARY KEY,
    first_name character varying(150),
    last_name character varying(150)
);
CREATE TABLE toys (
    id serial PRIMARY KEY,
    name character varying(150),
    child_id integer,
    FOREIGN KEY (child_id) REFERENCES children(id)
);
