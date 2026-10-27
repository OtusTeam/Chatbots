-- SELECT *
-- FROM users
-- INNER JOIN orders
-- ON users.id = orders.user_id;


-- SELECT *
-- FROM users
-- JOIN orders
-- ON users.id = orders.user_id;


-- SELECT *
-- FROM users
-- LEFT JOIN orders
-- ON users.id = orders.user_id;


-- SELECT *
-- FROM users
-- RIGHT JOIN orders
-- ON users.id = orders.user_id;


-- SELECT *
-- FROM users
-- FULL JOIN orders
-- ON users.id = orders.user_id;


-- SELECT name, status
-- FROM users
-- INNER JOIN orders
-- ON users.id = orders.user_id;


-- SELECT users.name, orders.status
-- FROM users
-- INNER JOIN orders
-- ON users.id = orders.user_id;


-- SELECT users.name AS 'Имя', orders.status AS 'Статус'
-- FROM users
-- INNER JOIN orders
-- ON users.id = orders.user_id;


-- SELECT u.name AS 'Имя', o.status AS 'Статус'
-- FROM users AS u
-- INNER JOIN orders AS o
-- ON u.id = o.user_id;


SELECT u.name AS 'Имя', o.status AS 'Статус'
FROM users u
INNER JOIN orders o
ON u.id = o.user_id
WHERE o.status = 'paid'
ORDER BY u.name;