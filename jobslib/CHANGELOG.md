# Jobslib

## [1.2.0rc2] - 2019-03-25 09:29 - Jan Seifert <jan.seifert@firma.seznam.cz>
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
