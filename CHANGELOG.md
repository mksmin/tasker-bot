# Changelog

## [Unreleased]
### Added
- Новая фича: возможность отправлять сообщения пользователям от имени владельца
- Поддержка настройки конфигурации через YAML
- Новое поле `secure` для RabbitMQ конфигурации
([Issue #11](https://github.com/mksmin/tasker-bot/issues/11), [PR #14](https://github.com/mksmin/tasker-bot/pull/14))

## [v1.0.1] - 2025-10-30
### Fixed
- Обработка TelegramForbidden: задача теперь удаляется при ошибке forbidden. (PR #10)
