<?php
// Database connection (adjust credentials as needed)
$host = 'localhost';
$user = 'root';
$password = ''; // your password
$database = 'boltaindia';

$connection = new mysqli($host, $user, $password, $database);
if ($connection->connect_error) {
    die("Connection failed: " . $connection->connect_error);
}

// SQL to create categories table
$categories_sql = "CREATE TABLE IF NOT EXISTS categories (
    id INT(11) NOT NULL AUTO_INCREMENT,
    title VARCHAR(50) NOT NULL,
    description TEXT NOT NULL,
    PRIMARY KEY (id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;";

// SQL to create users table
$users_sql = "CREATE TABLE IF NOT EXISTS users (
    id INT(11) NOT NULL AUTO_INCREMENT,
    firstname VARCHAR(50) NOT NULL,
    lastname VARCHAR(50) NOT NULL,
    username VARCHAR(50) NOT NULL,
    email VARCHAR(100) NOT NULL,
    password VARCHAR(255) NOT NULL,
    avatar VARCHAR(255),
    is_admin TINYINT(1) NOT NULL DEFAULT 0,
    PRIMARY KEY (id),
    UNIQUE KEY username (username),
    UNIQUE KEY email (email)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;";

// SQL to create posts table
$posts_sql = "CREATE TABLE IF NOT EXISTS posts (
    id INT(11) NOT NULL AUTO_INCREMENT,
    title VARCHAR(255) NOT NULL,
    body TEXT NOT NULL,
    thumbnail VARCHAR(255),
    date_time DATETIME DEFAULT CURRENT_TIMESTAMP,
    category_id INT(11) NULL,
    author_id INT(11) NOT NULL,
    is_featured TINYINT(1) NOT NULL DEFAULT 0,
    PRIMARY KEY (id),
    FOREIGN KEY (category_id) REFERENCES categories(id) ON DELETE SET NULL,
    FOREIGN KEY (author_id) REFERENCES users(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;";

// Execute queries and check for errors
foreach ([$categories_sql, $users_sql, $posts_sql] as $sql) {
    if ($connection->query($sql) === TRUE) {
        echo "Table created successfully or already exists.<br>";
    } else {
        echo "Error creating table: " . $connection->error . "<br>";
    }
}

$connection->close();
?>
