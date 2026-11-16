-- 20 учебных SQL-запросов к схеме «Банк».
-- Запуск: sqlite3 bank.db < schema.sql < seed.sql < queries.sql
-- Для PostgreSQL меняются только даты (см. комментарии) и типы в схеме.
-- Каждая задача помечена маркером -- @task; scripts/check_sql.py прогоняет их автоматически.

-- ============================================================
-- Блок A. Выборки и фильтрация
-- ============================================================

-- @task 1. Клиенты из Москвы, отсортированные по ФИО
-- Ожидаемо: 5 строк (Григорий Орлов, Дмитрий Попов, Иван Петров, Мария Смирнова, Павел Волков)
SELECT full_name, phone, birth_date, city
FROM clients
WHERE city = 'Москва'
ORDER BY full_name;

-- @task 2. Активные счета с балансом больше 100 000, по убыванию баланса
-- Ожидаемо: 6 строк, первая — 520000.00
SELECT account_number, account_type, currency, balance
FROM accounts
WHERE status = 'active' AND balance > 100000
ORDER BY balance DESC;

-- @task 3. Счета конкретного клиента по номеру телефона (параметризованная выборка)
-- Ожидаемо: 2 счёта клиента Иван Петров
SELECT c.full_name, a.account_number, a.account_type, a.balance
FROM clients AS c
JOIN accounts AS a ON a.client_id = c.client_id
WHERE c.phone = '+79001112233'
ORDER BY a.balance DESC;

-- @task 4. Транзакции по счёту за март 2026
-- Ожидаемо: 2 операции по счёту 13
SELECT transaction_id, operation_type, amount, status, created_at
FROM transactions
WHERE account_id = 13
  AND created_at >= '2026-03-01' AND created_at < '2026-04-01'
ORDER BY created_at;

-- @task 5. Неуспешные и отменённые операции
-- Ожидаемо: 5 строк (3 failed, 2 reversed)
SELECT transaction_id, account_id, operation_type, amount, status
FROM transactions
WHERE status IN ('failed', 'reversed')
ORDER BY created_at;

-- ============================================================
-- Блок B. Соединения таблиц
-- ============================================================

-- @task 6. Все счета с ФИО владельца (INNER JOIN)
-- Ожидаемо: 22 строки
SELECT c.full_name, a.account_number, a.account_type, a.balance
FROM clients AS c
JOIN accounts AS a ON a.client_id = c.client_id
ORDER BY c.full_name, a.account_id;

-- @task 7. Клиенты без счетов (LEFT JOIN + IS NULL)
-- Ожидаемо: 2 строки (Юлия Комарова, Григорий Орлов)
SELECT c.client_id, c.full_name, c.status
FROM clients AS c
LEFT JOIN accounts AS a ON a.client_id = c.client_id
WHERE a.account_id IS NULL
ORDER BY c.client_id;

-- @task 8. Активные карты с владельцем и типом счёта (3 таблицы)
-- Ожидаемо: 16 строк
SELECT c.full_name, ca.card_number_masked, ca.payment_system, ca.status, a.account_type
FROM cards AS ca
JOIN accounts AS a ON a.account_id = ca.account_id
JOIN clients AS c ON c.client_id = a.client_id
WHERE ca.status = 'active'
ORDER BY c.full_name;

-- @task 9. Счета, у которых есть хотя бы одна активная карта (EXISTS)
-- Ожидаемо: 16 счетов
SELECT a.account_id, a.account_number, a.balance
FROM accounts AS a
WHERE EXISTS (
    SELECT 1 FROM cards AS ca
    WHERE ca.account_id = a.account_id AND ca.status = 'active'
)
ORDER BY a.account_id;

-- @task 10. Клиенты с количеством счетов и суммарным балансом
-- Ожидаемо: 13 строк, в реальном отчёте валюты нельзя складывать без пересчёта курса
SELECT c.full_name,
       COUNT(a.account_id)  AS accounts_count,
       ROUND(SUM(a.balance), 2) AS total_balance
FROM clients AS c
JOIN accounts AS a ON a.client_id = c.client_id
GROUP BY c.client_id, c.full_name
ORDER BY total_balance DESC;

-- ============================================================
-- Блок C. Агрегация и группировка
-- ============================================================

-- @task 11. Количество и сумма балансов по типам счетов
-- Ожидаемо: current — 12, savings — 5, deposit — 3, credit — 2 (всего 22)
SELECT account_type,
       COUNT(*) AS accounts_count,
       ROUND(SUM(balance), 2) AS total_balance
FROM accounts
GROUP BY account_type
ORDER BY accounts_count DESC;

-- @task 12. Оборот по типам завершённых операций (группы больше 50 000)
-- Ожидаемо: только типы, чья сумма операций превышает порог
SELECT operation_type,
       COUNT(*) AS operations,
       ROUND(SUM(amount), 2) AS total_amount,
       ROUND(AVG(amount), 2) AS avg_amount
FROM transactions
WHERE status = 'completed'
GROUP BY operation_type
HAVING SUM(amount) > 50000
ORDER BY total_amount DESC;

-- @task 13. Топ-5 клиентов по суммарному балансу
-- Ожидаемо: 5 строк, первая — Иван Петров
SELECT c.full_name, ROUND(SUM(a.balance), 2) AS total_balance
FROM clients AS c
JOIN accounts AS a ON a.client_id = c.client_id
GROUP BY c.client_id, c.full_name
ORDER BY total_balance DESC
LIMIT 5;

-- @task 14. Динамика операций по месяцам
-- Ожидаемо: 6 строк (2026-01 … 2026-06)
-- Для PostgreSQL: GROUP BY to_char(created_at, 'YYYY-MM')
SELECT substr(created_at, 1, 7) AS month,
       COUNT(*) AS operations,
       ROUND(SUM(amount), 2) AS total_amount
FROM transactions
WHERE status = 'completed'
GROUP BY month
ORDER BY month;

-- @task 15. Разрез по валютам через CASE
-- Ожидаемо: 3 строки (RUB, USD, EUR)
SELECT CASE currency
           WHEN 'RUB' THEN 'Рубли'
           WHEN 'USD' THEN 'Доллары'
           WHEN 'EUR' THEN 'Евро'
       END AS currency_name,
       COUNT(*) AS operations,
       ROUND(SUM(amount), 2) AS total_amount
FROM transactions
GROUP BY currency
ORDER BY total_amount DESC;

-- ============================================================
-- Блок D. Подзапросы
-- ============================================================

-- @task 16. Операции выше средней суммы по всем транзакциям (скалярный подзапрос)
-- Ожидаемо: 10+ строк, сверху суммы 180000 и 120000
SELECT transaction_id, account_id, operation_type, amount
FROM transactions
WHERE amount > (SELECT AVG(amount) FROM transactions)
ORDER BY amount DESC;

-- @task 17. Клиенты, у которых есть операции на сумму больше 50 000 (EXISTS)
-- Ожидаемо: 6 клиентов
SELECT c.client_id, c.full_name
FROM clients AS c
WHERE EXISTS (
    SELECT 1
    FROM transactions AS t
    JOIN accounts AS a ON a.account_id = t.account_id
    WHERE a.client_id = c.client_id AND t.amount > 50000
)
ORDER BY c.client_id;

-- @task 18. Клиенты, у которых вообще нет операций (NOT EXISTS)
-- Ожидаемо: 5 клиентов (11-15)
SELECT c.client_id, c.full_name
FROM clients AS c
WHERE NOT EXISTS (
    SELECT 1
    FROM transactions AS t
    JOIN accounts AS a ON a.account_id = t.account_id
    WHERE a.client_id = c.client_id
)
ORDER BY c.client_id;

-- @task 19. Операции выше средней по своему счёту (коррелированный подзапрос)
-- Ожидаемо: по каждому счёту только крупные операции
SELECT t.transaction_id, t.account_id, t.amount
FROM transactions AS t
WHERE t.amount > (
    SELECT AVG(t2.amount) FROM transactions AS t2 WHERE t2.account_id = t.account_id
)
ORDER BY t.account_id, t.amount DESC;

-- @task 20. Оконные функции: накопительный итог по счёту и ранг по сумме операции
-- Оконные функции доступны в SQLite 3.25+ и PostgreSQL
SELECT account_id,
       transaction_id,
       created_at,
       amount,
       SUM(amount) OVER (PARTITION BY account_id ORDER BY created_at, transaction_id) AS running_total,
       RANK() OVER (ORDER BY amount DESC) AS amount_rank
FROM transactions
WHERE status = 'completed'
ORDER BY account_id, created_at;

-- ============================================================
-- Блок E. Работа с индексами
-- ============================================================

-- @indexes Дополнительные индексы и план запроса
CREATE INDEX IF NOT EXISTS idx_transactions_status ON transactions (status);
CREATE INDEX IF NOT EXISTS idx_accounts_balance ON accounts (balance);
EXPLAIN QUERY PLAN
SELECT * FROM transactions
WHERE account_id = 13 AND created_at >= '2026-03-01' AND created_at < '2026-04-01';

-- ============================================================
-- Блок F. Изменение данных в транзакции
-- ============================================================

-- @dml Изменение данных с контролем транзакции
-- Предусловие: выполнены schema.sql и seed.sql
BEGIN;
INSERT INTO transactions (transaction_id, account_id, operation_type, amount, currency, status, counterparty_account, description, created_at)
VALUES (999, 1, 'payment', 777.00, 'RUB', 'completed', 'ТЕСТ', 'Тестовая операция', '2026-07-01 12:00:00');

UPDATE accounts
SET balance = balance - 777.00
WHERE account_id = 1;

SELECT transaction_id, amount, description FROM transactions WHERE transaction_id = 999;
SELECT account_id, balance FROM accounts WHERE account_id = 1;
COMMIT;

-- @dml-rollback Откат вставки: операция 1000 не должна сохраниться
BEGIN;
INSERT INTO transactions (transaction_id, account_id, operation_type, amount, currency, status, description, created_at)
VALUES (1000, 1, 'fee', 50.00, 'RUB', 'completed', 'Операция для отката', '2026-07-02 12:00:00');
UPDATE accounts SET balance = balance - 50.00 WHERE account_id = 1;
ROLLBACK;
