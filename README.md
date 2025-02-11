# Пет-проект по симуляции алгоритмической торговли в реальном времени

В проекте реализована симуляция алгоритмической торговли (без реальной торговли) на данных в реальном времени.

Проект включает в себя:
- получение данных по websocket'у биржи,
- анализ данных в Spark и генерации торгового сигнала,
- построение хранилища в Clickhouse для хранения данных,
- [бэктестинг](https://en.wikipedia.org/wiki/Backtesting) торгового сигнала на исторических данных,
- визуализацию логов и, непостредственно, симуляции результатов торговли в Grafana.

# Описание

Данный проект использует открытые данные [Deribit websocket](https://docs.deribit.com/?python#json-rpc-over-websocket) как источник.

В частности, для анализа используются данные по [Limit Order Book](https://en.wikipedia.org/wiki/Central_limit_order_book) - [ссылка на API](https://docs.deribit.com/?python#public-get_order_book_by_instrument_id).

Для общения между сервисами используется Redis Streams.

Визуализация эвентов происходит в Grafana.

# Roadmap

- [x] Websocket Connector
- [ ] Processing Engine
- [ ] Portfolio Manager
  - [ ] Backtesting
  - [ ] P/L Calculation
     
# Инстументарий

* [![Python][Python]][Python-url]
* [![Redis][Redis]][Redis-url]
* [![Clickhouse][Clickhouse]][Clickhouse-url]
* [![Grafana][Grafana]][Grafana-url]

<!-- MARKDOWN LINKS & IMAGES -->
<!-- https://www.markdownguide.org/basic-syntax/#reference-style-links -->
[Python]: https://img.shields.io/badge/Python-3776AB?logo=python&logoColor=fff
[Python-url]: https://www.python.org/
[Redis]: https://img.shields.io/badge/Redis-%23DD0031.svg?logo=redis&logoColor=white
[Redis-url]: https://redis.io/
[Clickhouse]: https://img.shields.io/badge/ClickHouse-FFCC01?logo=clickhouse&logoColor=000
[Clickhouse-url]: https://clickhouse.com/
[Grafana]: https://img.shields.io/badge/Grafana-F46800?logo=grafana&logoColor=fff
[Grafana-url]: https://grafana.com/
