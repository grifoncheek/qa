# Баг-репорты

Я выявил все дефекты при исследовательском тестировании REST API Restful-Booker 15.11.2026, воспроизводимость 100 %. Стенд публичный и учебный, поэтому записи создаются каждым запросом заново, а ID в примерах не фиксированы. Все дефекты касаются POST /booking, кроме BUG-05 и BUG-10.

## Жизненный цикл дефекта

Статусы идут так: New → Open → In Progress → Fixed → Ready for Testing → Verified → Closed; из Ready for Testing возможен возврат в Reopened, из Open — в Rejected, Duplicate или Deferred. Severity обозначает влияние на продукт (Blocker, Critical, Major, Minor, Trivial), а Priority — очередь исправления (High, Medium, Low). Они не совпадают: 500 на необязательном поле бывает Critical, но Medium, если воспроизводится редко.

---

## BUG-01 — 500 вместо 400 при отсутствии обязательного поля

**Severity:** Major **Priority:** High **Status:** New  
**Шаги:** выполнить запрос ниже.

    curl -X POST https://restful-booker.herokuapp.com/booking \
      -H "Content-Type: application/json" \
      -d '{"lastname":"Ivanov","totalprice":100,"depositpaid":true,
           "bookingdates":{"checkin":"2026-01-01","checkout":"2026-01-02"}}'

**Ожидаемый:** 400 Bad Request с описанием отсутствующего firstname. **Фактический:** 500 Internal Server Error. Серверная ошибка вместо валидации: клиент не понимает, что исправить.

---

## BUG-02 — 500 при null в обязательном строковом поле

**Severity:** Major **Priority:** High **Status:** New  
**Шаги:** отправить {"firstname": null, "lastname": "B", "totalprice": 100, "depositpaid": true, "bookingdates": {"checkin": "2026-01-01", "checkout": "2026-01-02"}}.

**Ожидаемый:** 400 — firstname обязателен и не может быть null. **Фактический:** 500 Internal Server Error.

---

## BUG-03 — 500 при неверном типе bookingdates

**Severity:** Major **Priority:** High **Status:** New  
**Шаги:** передать bookingdates строкой: {"firstname":"A","lastname":"B","totalprice":100,"depositpaid":true,"bookingdates":"2026-01-01"}.

**Ожидаемый:** 400 — bookingdates должен быть объектом с checkin и checkout. **Фактический:** 500 Internal Server Error.

---

## BUG-04 — 500 при неподдерживаемом Content-Type

**Severity:** Major **Priority:** Medium **Status:** New  
**Шаги:** отправить корректный JSON с заголовком Content-Type: text/plain.

**Ожидаемый:** 415 Unsupported Media Type. **Фактический:** 500 Internal Server Error.

---

## BUG-05 — 500 при невалидной дате в фильтре

**Severity:** Major **Priority:** Medium **Status:** New  
**Шаги:** GET /booking?checkin=not-a-date.

**Ожидаемый:** 400 с сообщением о неверном формате даты. **Фактический:** 500 Internal Server Error. Фильтр с корректными датами работает, ошибка проявляется только на невалидном вводе.

---

## BUG-06 — totalprice строкой принимается и теряется

**Severity:** Critical **Priority:** High **Status:** New  
**Шаги:** отправить {"firstname":"A","lastname":"B","totalprice":"100","depositpaid":true,"bookingdates":{"checkin":"2026-01-01","checkout":"2026-01-02"}}.

**Ожидаемый:** 400 — totalprice должен быть числом. **Фактический:** 200 OK, в ответе "totalprice": null. Значение молча теряется — бронь создаётся с неизвестной стоимостью; строка "сто" ведёт себя так же.

---

## BUG-07 — Отрицательный totalprice принимается

**Severity:** Major **Priority:** High **Status:** New  
**Шаги:** отправить {"firstname":"A","lastname":"B","totalprice":-100,"depositpaid":true,"bookingdates":{"checkin":"2026-01-01","checkout":"2026-01-02"}}.

**Ожидаемый:** 400 — стоимость не может быть отрицательной. **Фактический:** 200 OK, "totalprice": -100.

---

## BUG-08 — checkout раньше checkin принимается

**Severity:** Major **Priority:** High **Status:** New  
**Шаги:** отправить {"firstname":"A","lastname":"B","totalprice":100,"depositpaid":true,"bookingdates":{"checkin":"2026-05-01","checkout":"2026-01-02"}}.

**Ожидаемый:** 400 — дата выезда должна быть позже даты заезда. **Фактический:** 200 OK, бронь создана с выездом раньше заезда.

---

## BUG-09 — Прошедшая дата заезда принимается

**Severity:** Major **Priority:** Medium **Status:** New  
**Шаги:** создать бронь с "checkin":"2020-01-01", "checkout":"2020-01-02".

**Ожидаемый:** 400 — нельзя бронировать прошедшие даты. **Фактический:** 200 OK.

---

## BUG-10 — Неверные учётные данные возвращают 200

**Severity:** Major **Priority:** High **Status:** New  
**Шаги:** отправить {"username":"admin","password":"wrong"} на POST /auth.

**Ожидаемый:** 401 Unauthorized. **Фактический:** 200 OK, тело {"reason":"Bad credentials"}. Код 200 для отказа ломает проверку успеха на клиенте; пустое тело ведёт себя так же.

---

## BUG-11 — Пустое значение в обязательном поле принимается

**Severity:** Minor **Priority:** Medium **Status:** New  
**Шаги:** отправить {"firstname":"","lastname":"B",...}.

**Ожидаемый:** 400 — пустая строка не является валидным именем. **Фактический:** 200 OK, бронь создана с пустым именем.

---

## BUG-12 — Нет ограничения длины имени

**Severity:** Minor **Priority:** Low **Status:** New  
**Шаги:** отправить firstname длиной 300 символов.

**Ожидаемый:** 400 — превышена максимальная длина поля. **Фактический:** 200 OK, все 300 символов сохранены и возвращены в ответе.

---

## BUG-13 — Несуществующая дата принимается и искажается

**Severity:** Critical **Priority:** High **Status:** New  
**Шаги:** отправить {"firstname":"A","lastname":"B","totalprice":10,"depositpaid":true,"bookingdates":{"checkin":"2026-13-45","checkout":"2026-13-50"}}.

**Ожидаемый:** 400 — 13-й месяц и 45-е число не существуют. **Фактический:** 200 OK, даты искажены в ответе до "checkin":"0NaN-aNNaN-aN...". Календарной валидации нет, в хранилище попадают некорректные данные.

---

## BUG-14 — 500 при null в totalprice

**Severity:** Major **Priority:** Medium **Status:** New  
**Шаги:** отправить {"firstname":"A","lastname":"B","totalprice":null,"depositpaid":true,...}.

**Ожидаемый:** 400 — totalprice обязателен и должен быть числом. **Фактический:** 500 Internal Server Error.

---

## Сводка

По severity дефекты распределились так: два Critical — BUG-06 и BUG-13; десять Major — BUG-01, 02, 03, 04, 05, 07, 08, 09, 10 и 14; два Minor — BUG-11 и BUG-12. API не валидирует типы, значения и обязательность полей, поэтому ошибки ввода дают 500 либо запись некорректных данных. Наиболее приоритетны BUG-06 и BUG-13 (искажение данных) и BUG-10 (неверный код авторизации).

## Маппинг в Test IT

При переносе в Test IT ID соответствует автоинкременту или External ID, заголовок — полю Name, а предусловия, шаги, ожидаемый и фактический результат маппятся в Preconditions, Steps, Expected result и Actual result. Severity и Priority сохраняются одноимённо, Status — это Status (New/Open/Fixed и т. д.), примечание уходит в Description или Comments.
