CREATE TABLE IF NOT EXISTS translation_history(
    id int NOT NULL AUTO_INCREMENT,
    user_id int NOT NULL,
    original_text text,
    translated_text text,
    target_language varchar(50),
    translation_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (id),
    FOREIGN KEY (user_id) REFERENCES site_users(user_id)
);
