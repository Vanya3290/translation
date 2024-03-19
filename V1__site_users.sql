CREATE TABLE IF NOT EXISTS site_users(
    user_id int NOT NULL AUTO_INCREMENT,
    user_login varchar(50),
    user_pass varchar(50),
    PRIMARY KEY (user_id)
);