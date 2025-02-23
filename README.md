# Pet Project On HFT Simulation

The project implements a simulation of algorithmic trading (without actual trading) on real-time data.

The project includes:
- receiving data via the exchange's WebSocket,
- data analysis in PySpark and generating a trading signal,
- building a MongoDB storage for data retention,
- [backtesting](https://en.wikipedia.org/wiki/Backtesting) the trading signal on historical data,
- visualization of logs and the trading simulation results in Grafana.

# About The Project

This project uses open data from the [Deribit websocket](https://docs.deribit.com/?python#json-rpc-over-websocket) as a source.

In particular, data on [Limit Order Book](https://en.wikipedia.org/wiki/Central_limit_order_book) is used - [API link](https://docs.deribit.com/?python#public-get_order_book_by_instrument_id).

Redis Streams are used for communication between services.

Visualization of events takes place in Grafana.

# Roadmap

- [x] Websocket Connector
- [ ] Processing Engine
- [ ] Portfolio Manager
  - [ ] Backtesting
  - [ ] P/L Calculation
     
# Built With

* [![Python][Python]][Python-url]
* [![Redis][Redis]][Redis-url]
* [![MongoDB][MongoDB]][MongoDB-url]
* [![Grafana][Grafana]][Grafana-url]

[Python]: https://img.shields.io/badge/Python-3776AB?logo=python&logoColor=fff
[Python-url]: https://www.python.org/
[Redis]: https://img.shields.io/badge/Redis-%23DD0031.svg?logo=redis&logoColor=white
[Redis-url]: https://redis.io/
[MongoDB]: https://img.shields.io/badge/MongoDB-%234ea94b.svg?logo=mongodb&logoColor=white
[MongoDB-url]: https://www.mongodb.com/
[Grafana]: https://img.shields.io/badge/Grafana-F46800?logo=grafana&logoColor=fff
[Grafana-url]: https://grafana.com/
