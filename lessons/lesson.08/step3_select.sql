-- SELECT *
-- FROM users;

-- SELECT name, email FROM users;

-- SELECT *
-- FROM orders
-- WHERE status = 'paid';

--   >= <= < > = !=

-- SELECT *
-- FROM orders
-- WHERE amount > 1000;

-- SELECT *
-- FROM orders
-- WHERE status != 'paid';


-- SELECT *
-- FROM orders
-- WHERE status = 'paid'
--   AND amount > 2000;

-- SELECT *
-- FROM orders
-- WHERE status = 'new'
--    OR status = 'cancelled';


-- SELECT *
-- FROM orders
-- WHERE status = 'new'
--    OR status = 'cancelled'
-- ORDER BY amount ASC;


-- SELECT *
-- FROM orders
-- WHERE status = 'new'
--    OR status = 'cancelled'
-- ORDER BY amount;


-- SELECT *
-- FROM orders
-- WHERE status = 'new'
--    OR status = 'cancelled'
-- ORDER BY amount DESC;


-- SELECT *
-- FROM orders
-- WHERE status = 'new'
--    OR status = 'cancelled'
-- ORDER BY status DESC, amount ASC;


-- SELECT *
-- FROM orders
-- WHERE status = 'new'
--    OR status = 'cancelled'
-- ORDER BY status DESC, amount ASC
-- LIMIT 5;


-- INSERT INTO users (name, email)
-- VALUES
--     ('Боб', 'bob@mail.com');


-- INSERT INTO users (name, email)
-- VALUES
--     ('Мэри', 'mary@mail.com')
-- RETURNING id, name, email;
