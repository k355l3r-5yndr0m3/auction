DROP TABLE IF EXISTS Auctions;
DROP TABLE IF EXISTS Users;

CREATE TABLE Auctions (
    id          INTEGER   PRIMARY KEY AUTOINCREMENT,
    title       TEXT      NOT NULL,
    description TEXT      NOT NULL
);

CREATE TABLE Users (
    id          INTEGER   PRIMARY KEY AUTOINCREMENT,
    username    TEXT      NOT NULL UNIQUE,
    password    TEXT      NOT NULL,
    role        INTEGER   NOT NULL CHECK(role == 0 OR role == 1 OR role == 2)
)

INSERT INTO Auctions (title, description) VALUES ("Test auction", "This is a test")

