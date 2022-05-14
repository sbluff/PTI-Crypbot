CREATE TABLE trades.bot_parameters (
	credit FLOAT DEFAULT 1000 NULL,
	entryAmount varchar(100) DEFAULT '25' NULL,
	mode varchar(100) DEFAULT 'test' NULL
)
ENGINE=InnoDB
DEFAULT CHARSET=utf8
COLLATE=utf8_general_ci;


INSERT INTO trades.bot_parameters (credit, entryAmount, mode) VALUES (1000, '25.0', 'test');