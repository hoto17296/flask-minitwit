CREATE TABLE users (
  id serial PRIMARY KEY,
  name text NOT NULL,
  email text NOT NULL,
  pw_hash text NOT NULL
);

CREATE TABLE followers (
  who_id int NOT NULL,
  whom_id int NOT NULL,
  FOREIGN KEY (who_id) REFERENCES users(id),
  FOREIGN KEY (whom_id) REFERENCES users(id),
  UNIQUE (who_id, whom_id)
);

CREATE TABLE messages (
  id serial PRIMARY KEY,
  user_id int NOT NULL,
  text text NOT NULL,
  pub_date int,
  FOREIGN KEY (user_id) REFERENCES users(id)
);
