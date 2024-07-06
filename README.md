# ChatPay Backend

The ChatPay Backend is a Quart application that interacts with the Telegram API using Telethon, supported by a Postgres database with Alembic for migrations.

ChatPay empowers Telegram users to sell their chats (cleaned of personal data) to train AI. For a general introduction to ChatPay, please refer to the [ChatPay Organization README](https://github.com/TON-42).

## Table of Contents

- [Introduction](#introduction)
- [Features](#features)
- [Tech Stack](#tech-stack)
- [License](#license)
- [Roadmap](#roadmap)

## Introduction

The ChatPay TMA Backend is a robust service that handles the core functionalities of the ChatPay application. It connects to the Telegram API, processes and anonymizes chat data, and serves as the backbone for the ChatPay ecosystem, which includes a frontend and a website.

## Tech Stack

- **Telethon**: Python Telegram client library.
- **Telebot**: Python wrapper for the Telegram Bot API.
- **Quart**: Async web framework based on Flask.
- **Telemetry**: System for performance and user behavior monitoring.
- **Postgres DB**: Object-relational database system.
- **ReTool**: Platform for building internal tools.

## Contributing

At this moment, we are not accepting external contributions. For feedback or to report issues, please contact us at [contact@chatpay.app](mailto:contact@chatpay.app) or open an issue on GitHub.

## License

This project is licensed under the Business Source License 1.1. For full terms, please refer to the [LICENSE](./LICENSE) file.

## Contact

For any questions, please reach out to us at [contact@chatpay.app](mailto:contact@chatpay.app).

## Roadmap

- [ ] Write Raodmap for the Backend
