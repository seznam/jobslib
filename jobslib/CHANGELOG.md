# Jobslib

## [2.5.0] - 2020-04-15 09:55 - Jan Seifert <jan.seifert@firma.seznam.cz>
### Fixed
- Do not exit with code 0 when error (SDOP-1363)

## [2.4.0] - 2020-04-14 11:00 - Josef Florian <josef.florian@firma.seznam.cz>
### Added
- consul timeout (DOP-3335)

## [2.3.0] - 2020-03-17 15:46 - Jan Seifert <jan.seifert@firma.seznam.cz>
### Changed
- limit `ujson` dependency

## [2.2.0] - 2020-03-10 09:00 - Jozef Juris
### Changed
- updated dependency to python-consul2 (DOP-3220)

## [2.1.0] - 2020-01-13 14:04 - Jiri Dokladal <jiri.dokladal@firma.seznam.cz>
### Fixed
- Removed ttl argument from lock refresh calls (#SDOP-1179)

## [2.0.0] - 2019-10-22 08:35 - Jan Seifert <jan.seifert@firma.seznam.cz>
### Changed
- improve refreshing of the one instance lock
### Fixed
- `jobslib.oneinstance.consul.ConsulLock.get_lock_owner_info` method
### Incompatible changes between 2.x and 1.x
- removed `ttl` parameter from `jobslib.oneinstance.BaseLock.refresh` method
- `jobslib.oneinstance.consul.ConsulLock.get_lock_owner_info` returns **dict**
  or **None** if information of the lock owner is not available

## [1.3.0] - 2019-09-23 12:00 - Alan Stolc <alan.stolc@firma.seznam.cz>
### Added
- JOB_STATUS_KILLED metric (#SDOP-533)

## [1.2.2] - 2019-08-02 10:25 - Jan Seifert <jan.seifert@firma.seznam.cz>
### Fixed
- Fix name of the logger

## [1.2.1] - 2019-05-21 15:00 - Alan Stolc <alan.stolc@firma.seznam.cz>
### Changed
- Expired lock log message (#SDOP-103)

## [1.2.0] - 2019-03-25 09:29 - Jan Seifert <jan.seifert@firma.seznam.cz>
### Added
- keep lock during sleeping interval
### Changed
- use semantic versioning

## [1.1.1] - 2019-03-19 10:00 - Josef Florian <josef.florian@firma.seznam.cz>
### Fixed
- method `get_lock_owner_info`

## [1.1.0] - 2019-02-27 14:35 - Jan Seifert <jan.seifert@firma.seznam.cz>
### Added
- run interval option
- use objectvalidator library

## [1.0.8] - 2019-02-08 08:34 - Jan Seifert <jan.seifert@firma.seznam.cz>
### Changed
- Add OneInstanceWatchdogError on public API

## [1.0.7] - 2018-02-04 12:00 - Alan Stolc <alan.stolc@firma.seznam.cz>
### Added
- lock release on SIGINT and SIGTERM

## [1.0.6] - 2018-12-12 15:52 - Ondra Voves <ondrej.voves@firma.seznam.cz>
### Fixed
- fix bad env validation for influxdb

## [1.0.5] - 2018-12-11 16:52 - Ondra Voves <ondrej.voves@firma.seznam.cz>
### Fixed
- timstamp as string to numeric because influxwrapper

## [1.0.4] - 2018-12-11 16:36 - Ondra Voves <ondrej.voves@firma.seznam.cz>
### Fixed
- Add password to influx config.
- Safely metrics.

## [1.0.3] - 2018-12-11 13:36 - Ondra Voves <ondrej.voves@firma.seznam.cz>
### Added
- Metrics.

## [1.0.2] - 2018-12-11 13:36 - Ondrej Voves <ondrej.voves@firma.seznam.cz>
### Fixed
- add szn-doporucovani-influxdb-wrapper to setup.py

## [1.0.1] - 2018-12-06 13:36 - Ondrej Voves <ondrej.voves@firma.seznam.cz>
### Fixed
- Destroy lock session if aquire fail.

## [1.0.0] - 2018-08-14 13:36 - Jan Seifert <jan.seifert@firma.seznam.cz>
- First version of the Jobslib
