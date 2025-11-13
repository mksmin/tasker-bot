# Changelog

## [Unreleased]
### Added
- Контракт в rabbit service для частичного обновления настроек аффирмаций
- Команда для владельца `/jobs` для получения списка задач планировщика
- Сообщение пользователю о превышении длины аффирмации
### Fix
- Ошибка TelegramBadRequest когда пользователь изменял настройки отправки в MiniApp и одновременно через кнопку

## [v1.1.0] - 2025-10-31
### Added
- Возможность отправлять сообщения пользователям от имени владельца
- Поддержка настройки конфигурации через YAML
- Новое поле `secure` для конфигурации RabbitMQ
- Временное поле `owner_tg_id` для фильтрации команд владельца
  ([Issue #11](https://github.com/mksmin/tasker-bot/issues/11), [PR #14](https://github.com/mksmin/tasker-bot/pull/14))

## [v1.0.1] - 2025-10-30
### Fixed
- Обработка `TelegramForbidden`: задача теперь удаляется при ошибке `forbidden`.
  ([PR #10](https://github.com/mksmin/tasker-bot/pull/10))
