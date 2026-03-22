# Playerok Universal
[![telegram](https://img.shields.io/badge/telegram-%D0%BA%D0%B0%D0%BD%D0%B0%D0%BB-blue?style=for-the-badge&logo=telegram)](https://t.me/alexeyproduction)
[![modules](https://img.shields.io/badge/%F0%9F%A7%A9%20%D0%BC%D0%BE%D0%B4%D1%83%D0%BB%D0%B8-%D0%B1%D0%BE%D1%82%D0%B0-green?style=for-the-badge)](https://t.me/alexey_production_bot)
[![python](https://img.shields.io/badge/python-3.12.x-yellow?style=for-the-badge&logo=python&link=https%3A%2F%2Fimg.shields.io%2Fbadge%2Ftelegram-%25D0%25BA%25D0%25B0%25D0%25BD%25D0%25B0%25D0%25BB-blue%3Fstyle%3Dfor-the-badge%26logo%3Dtelegram)](https://www.python.org/downloads/release/python-3119/)
[![stars](https://img.shields.io/badge/dynamic/json?url=https%3A%2F%2Fapi.github.com%2Frepos%2Falleexxeeyy%2Fplayerok-universal&query=%24.stargazers_count&style=for-the-badge&label=stars&color=43d433&logo=github)](https://github.com/alleexxeeyy/playerok-universal/stargazers)
[![forks](https://img.shields.io/badge/dynamic/json?url=https%3A%2F%2Fapi.github.com%2Frepos%2Falleexxeeyy%2Fplayerok-universal&query=%24.forks_count&style=for-the-badge&label=forks&color=%236c70e6&logo=github)](https://github.com/alleexxeeyy/playerok-universal/forks)

Современный бот-помощник для Playerok 🤖🟦

---

## 🗺️ Навигация
- [Функционал бота](#-функционал)
- [Установка бота](#%EF%B8%8F-установка)
- [Полезные ссылки](#-полезные-ссылки)
- [Для разработчиков](#-для-разработчиков)

## 🔧 Функционал
### 🤖💬 Telegram бот с полным управлением
- Настройка любого параметра из конфига в пару действий
- Просмотр статистики бота и профиля аккаунта
- Управление ивентами бота

### ⚙️ Широкий спектр возможностей
- Система модулей (плагины, подключаемые к боту)
- Вечный онлайн на сайте
- Авто-восстановление предметов
- Авто-поднятие предметов
- Авто-выдача товаров
- Авто-вывод средств
- Авто-подтверждение сделок
- Приветственное сообщение
- Пользовательские команды
- Пользовательская авто-выдача
- Команда `!продавец` для вызова продавца в чат
- Редактирование и включение/отключение каждого сообщения
- Уведомления в TG о новых сообщениях, заказах, отзывах и т.д.

### 🌐 Более продвинутое
- Подключение к прокси HTTPS IPv4
- Настройка интервалов запросов

## ⬇️ Установка
1. Скачайте [последнюю Release версию](https://github.com/alleexxeeyy/playerok-universal/releases/latest) и распакуйте в любое удобное для вас место
2. Убедитесь, что у вас установлен **Python версии 3.12.x** (на других версиях работа бота не гарантируется). Если не установлен, сделайте это, перейдя по ссылке https://www.python.org/downloads/release/python-31210/ (при установке нажмите на пункт `Add to PATH`)
3. Откройте `install_requirements.bat` и дождитесь установки всех необходимых для работы библиотек, а после закройте окно
4. Чтобы запустить бота, откройте запускатор `start.bat`
5. После первого запуска вас попросят настроить бота для работы

[Возникли проблемы с установкой? Нажми на меня](https://telegra.ph/FunPay-Universal--chastye-oshibki-i-ih-resheniya-08-26)

## 📚 Для разработчиков

Модульная система помогает внедрять в бота дополнительный функционал, сделанный энтузиастами. По сути, это же, что и плагины, но в более удобном формате.
Вы можете создавать свой модуль, опираясь на [шаблонный](.templates/forms_module).

<details>
  <summary><strong>📌 Основные ивенты</strong></summary>

  ### Ивенты бота (BOT_EVENT_HANDLERS)

  Ивенты, которые выполняются при определённом действии бота.

  | Ивент | Когда вызывается | Передающиеся аргументы |
  |-------|------------------|------------------------|
  | `ON_MODULE_ENABLED` | При включении модуля | `Module` |
  | `ON_MODULE_DISABLED` | При выключении модуля | `Module` |
  | `ON_INIT` | При инициализации бота | `-` |
  | `ON_PLAYEROK_BOT_INIT` | При инициализации (запуске) Playerok бота | `PlayerokBot` |
  | `ON_TELEGRAM_BOT_INIT` | При инициализации (запуске) Telegram бота | `TelegramBot` |

  ### Ивенты Playerok (PLAYEROK_EVENT_HANDLERS)

  Ивенты, получаемые в слушателе событий в Playerok боте.

  | Ивент | Когда вызывается | Передающиеся аргументы |
  |-------|------------------|------------------------|
  | `EventTypes.CHAT_INITIALIZED` | Чат инициализирован | `PlayerokBot`, `ChatInitializedEvent` |
  | `EventTypes.NEW_MESSAGE` | Новое сообщение в чате | `PlayerokBot`, `NewMessageEvent` |
  | `EventTypes.NEW_DEAL` | Создана новая сделка (когда покупатель оплатил товар) | `PlayerokBot`, `NewDealEvent` |
  | `EventTypes.NEW_REVIEW` | Новый отзыв по сделке | `PlayerokBot`, `NewReviewEvent` |
  | `EventTypes.DEAL_CONFIRMED` | Сделка подтверждена | `PlayerokBot`, `DealConfirmedEvent` |
  | `EventTypes.DEAL_ROLLED_BACK` | Продавец оформил возврат сделки | `PlayerokBot`, `DealRolledBackEvent` |
  | `EventTypes.DEAL_HAS_PROBLEM` | Пользователь сообщил о проблеме в сделке | `PlayerokBot`, `DealHasProblemEvent` |
  | `EventTypes.DEAL_PROBLEM_RESOLVED` | Проблема в сделке решена | `PlayerokBot`, `DealProblemResolvedEvent` |
  | `EventTypes.DEAL_STATUS_CHANGED` | Статус сделки изменён | `PlayerokBot`, `DealStatusChangedEvent` |
  | `EventTypes.ITEM_PAID` | Пользователь оплатил предмет | `PlayerokBot`, `ItemPaidEvent` |
  | `EventTypes.ITEM_SENT` | Предмет отправлен (продавец подтвердил выполнение сделки) | `PlayerokBot`, `ItemSentEvent` |

</details>

<details>
  <summary><strong>📁 Строение модуля</strong></summary>  
  
  </br>Модуль - это папка, внутри которой находятся важные компоненты. Вы можете изучить строение модуля, опираясь на [шаблонный модуль](.templates/forms_module), но стоит понимать, что это лишь пример, сделанный нами.

  Обязательные константы хендлеров:
  | Константа | Тип | Описание |
  |-----------|-----|----------|
  | `BOT_EVENT_HANDLERS` | `dict[str, list[Any]]` | В этом словаре задаются хендлеры ивентов бота |
  | `PLAYEROK_EVENT_HANDLERS` | `dict[EventTypes, list[Any]` | В этом словаре задаются хендлеры ивентов Playerok |
  | `TELEGRAM_BOT_ROUTERS` | `list[Router]` | В этом массиве задаются роутеры модульного Telegram бота  |

  Обязательные константы метаданных:
  | Константа | Тип | Описание |
  |-----------|-----|----------|
  | `PREFIX` | `str` | Префикс |
  | `VERSION` | `str` | Версия |
  | `NAME` | `str` | Название |
  | `DESCRIPTION` | `str` | Описание |
  | `AUTHORS` | `str` | Авторы |
  | `LINKS` | `str` | Ссылки на авторов |

  Также, если модуль требует дополнительных зависимостей, в нём должен быть файл зависимостей **requirements.txt**, которые будут сами скачиваться при загрузке всех модулей бота.

  #### 🔧 Пример содержимого:
  Обратите внимание, что метаданные были вынесены в отдельный файл `meta.py`, но импортируются в `__init__.py`.
  Это сделано для избежания конфликтов импорта в дальнейшей части кода модуля.

  **`meta.py`**:
  ```python
  from colorama import Fore, Style

  PREFIX = f"{Fore.LIGHTCYAN_EX}[test module]{Fore.WHITE}"
  VERSION = "0.1"
  NAME = "test_module"
  DESCRIPTION = "Тестовый модуль. /test_module в Telegram боте для управления"
  AUTHORS = "@alleexxeeyy"
  LINKS = "https://t.me/alleexxeeyy, https://t.me/alexeyproduction"
  ```

  **`__init__.py`**:
  ```python
  from playerokapi.listener.events import EventTypes
  from core.modules_manager import Module, disable_module

  from .plbot.handlers import on_playerok_bot_init, on_new_message, on_new_deal
  from .tgbot import router
  from .tgbot._handlers import on_telegram_bot_init
  from .meta import *
  

  _module: Module = None


  def set_module(module: Module):
      global _module
      _module = module

  def get_module():
      return _module
  
  async def on_module_enabled(module: Module):
      try:
          set_module(module)
          print(f"{PREFIX} Модуль подключен и активен")
      except:
          await disable_module(_module.uuid)
  

  BOT_EVENT_HANDLERS = {
      "ON_MODULE_ENABLED": [on_module_enabled],
      "ON_PLAYEROK_BOT_INIT": [on_playerok_bot_init],
      "ON_TELEGRAM_BOT_INIT": [on_telegram_bot_init]
  }
  PLAYEROK_EVENT_HANDLERS = {
      EventTypes.NEW_MESSAGE: [on_new_message],
      EventTypes.NEW_DEAL: [on_new_deal],
      # ...
  }
  TELEGRAM_BOT_ROUTERS = [router]
  ```

</details>

<details>
  <summary><strong>🛠️ Полезные инструменты</strong></summary>  
  
  ### 📝 Настроенные врапперы файлов конфигурации и файлов данных
  Вместо того, чтобы лишний раз мучаться с файлами конфигурациями, написанием кода для управлениями ими, мы подготовили для вас готовое решение.
  У бота есть уже настроенные классы в файлах [`settings.py`](settings.py) и [`data.py`](data.py)

  #### Как это работает?
  Допустим, вы хотите создать файл конфигурации в своём модуле, для этого вам нужно будет создать файл `settings.py` в корне папки модуля.
  Содержимое `settings.py` должно быть примерно следующим:
  ```python
  import os
  from settings import (
      Settings as sett,
      SettingsFile
  )


  CONFIG = SettingsFile(
      name="config", #  название файла конфигурации
      path=os.path.join(os.path.dirname(__file__), "module_settings", "config.json"), #  путь к файлу конфигурации (в данном случае относительно папки модуля)
      need_restore=True, #  нужно ли восстанавливать конфиг
      default={
          "bool_param": True,
          "str_param": "qwerty",
          "int_param": 123
      } #  стандартное содержимое файла
  )

  DATA = [CONFIG]


  class Settings:
    
      @staticmethod
      def get(name: str) -> dict:
          return sett.get(name, DATA)

      @staticmethod
      def set(name: str, new: list | dict) -> dict:
          return sett.set(name, new, DATA)
  ```

  Файл конфигурации задаётся с помощью датакласса `SettingsFile`, который в свою очередь, передаётся в массив `DATA`.
  
  Далее, получить данные из конфига или сохранить данные в конфиг можно вот так:
  ```python
  from . import settings as sett

  config = sett.get("config") #  получаем конфиг
  print(config["bool_param"]) # -> True
  print(config["str_param"]) #  -> qwerty
  print(config["int_param"]) #  -> 123
  config["bool_param"] = False
  config["str_param"] = "uiop"
  config["int_param"] = 456
  sett.set("config", config) #  задаём конфигу новое значение
  ```

  Задавая конфигу новое значение, оно сразу записывается в его файл. Также и при получении, берутся актуальные данные из файла.

  Описание аргументов датакласса `SettingsFile`:
  | Аргумент | Описание |
  |----------|----------|
  | `name` | Название файла конфигурации, которое будем использовать при получении и записи |
  | `path` | Путь к файлу конфигурации |
  | `need_restore` | Нужно ли восстанавливать конфиг? Допустим, в стандартное значение конфига у вас добавились новые данные, а в уже созданном **ранее** файле конфигурации они отсутствуют. Если параметр включен, скрипт будет сверять текущие данные конфига со стандартными указанными, и если в текущих данных не будет того или иного ключа, который есть в стандартном значении, он автоматически добавится в конфиг. Так же, если тип значения ключа стандартного конфига не соответствует существующему (например, в файле **строковый** тип, а в стандартном значении **числовой**), также этот ключ в текущем конфиге будет заменён на стандартное значение |
  | `default` | Стандартное значение файла конфигурации |


  </br>Точно также устроен и файл данных, но он нужен для хранения информации, собранной самим скриптом, а не указанной пользователей.
  Например, вы хотите создать файл данных в своём модуле, для этого вам нужно будет создать файл `data.py` в корне папки модуля.
  
  Содержимое `data.py` должно быть примерно следующим:
  ```python
  import os
  from data import (
      Data as data,
      DataFile
  )


  LATEST_EVENTS_TIMES = DataFile(
      name="new_forms", #  название файла данных
      path=os.path.join(os.path.dirname(__file__), "module_data", "new_forms.json"), #  путь к файлу данных (в данном случае относительно папки модуля)
      default={} #  стандартное содержимое файла
  )

  DATA = [LATEST_EVENTS_TIMES]


  class Data:

      @staticmethod
      def get(name: str) -> dict:
          return data.get(name, DATA)

      @staticmethod
      def set(name: str, new: list | dict) -> dict:
          return data.set(name, new, DATA)
  ```

  Здесь всё аналогично файлу конфигурации, только служит для другой задачи.


  ### 🔌 Удобное управление состояниями модуля
  Используя методы из `core/modules.py`, можно удобно включать/выключать/перезагружать текущий модуль.
  Для того, чтобы это сделать, нужно прежде всего получить UUID текущего запущенного модуля, который генерируется при его инициализации.
  
  Например, в файле `__init__.py` можно делать так:
  ```python
  # import ...


  _module: Module = None


  async def set_module(module: Module):
      global _module
      _module = module

  def get_module():
      return _module
  

  BOT_EVENT_HANDLERS = {
      "ON_MODULE_ENABLED": [set_module],
      # ...
  }
  # ...
  ```

  А потом в любом удобном месте управлять модулем:
  ```python
  from core.modules import enable_module, disable_module, reload_module

  from . import get_module


  await disable_module(get_module().uuid) #  выключает модуль
  await enable_module(get_module().uuid) #  включает модуль
  await reload_module(get_module().uuid) #  перезагружает модуль
  ```

</details>

<details>
  <summary><strong>❗ Примечания</strong></summary>

  </br>Функционал Telegram бота написан на библиотеке aiogram 3, система внедрения пользовательского функционала Telegram бота работает на основе роутеров, которые сливаются с основным, главным роутером бота.
  И так, как они сливаются воедино, могут возникнуть осложнения, если, например Callback данные имеют идентичное название. Поэтому, после написания функционала Telegram бота для модуля, лучше переименуйте
  эти данные уникальным образом, чтобы они не совпадали с названиями основного бота или дополнительных подключаемых модулей.

</details>


## 🔗 Полезные ссылки
- Разработчик: https://github.com/alleexxeeyy (в профиле есть актуальные ссылки на все контакты для связи)
- Telegram канал: https://t.me/alexeyproduction
- Telegram бот для покупки официальных модулей: https://t.me/alexey_production_bot
