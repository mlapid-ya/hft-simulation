# Пет-проект по симуляции алгоритмической торговле в реальном времени

В проекте реализована симуляция алгоритмической торговли (без реальной торговли) на данных в реальном времени.

Проект включает в себя:
- [ ] получение данных по websocket'у биржи,
- [ ] анализу в Spark и генерации торгового сигнала,
- [ ] построению хранилища в Clickhouse для хранения данных,
- [ ] визуализацию логов и, непостредственно, симуляцию результатов торговли в Grafana.

# Описание

Данный проект использует открытые данные [Deribit websocket](https://docs.deribit.com/?python#json-rpc-over-websocket) как источник.

В частности, для анализа используются данные по [Limit Order Book](https://en.wikipedia.org/wiki/Central_limit_order_book) - [ссылка на API](https://docs.deribit.com/?python#public-get_order_book_by_instrument_id).

Для общения между сервисами используется Redis Streams.

Визуализация эвентов происходит в Grafana.

# Roadmap

- [ ] Websocket Connector
- [ ] Processing Engine
- [ ] Portfolio Manager
