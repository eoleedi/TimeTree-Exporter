# Changelog

## [0.6.1](https://github.com/eoleedi/TimeTree-Exporter/compare/v0.6.0...v0.6.1) (2025-07-03)


### Bug Fixes

* add missing VTimeZone cal component &  vDatetime TZID param ([#113](https://github.com/eoleedi/TimeTree-Exporter/issues/113)) ([6ea8293](https://github.com/eoleedi/TimeTree-Exporter/commit/6ea8293a1d4f4317da0d52870ad15f300c76bfe5))
* add the missing required prodid and version property ([#112](https://github.com/eoleedi/TimeTree-Exporter/issues/112)) ([7d43e0a](https://github.com/eoleedi/TimeTree-Exporter/commit/7d43e0a978176c9873f85ced059b22ae67be5a36))

## [0.6.0](https://github.com/eoleedi/TimeTree-Exporter/compare/v0.5.1...v0.6.0) (2025-06-29)


### Features

* password with echo ([f3c6841](https://github.com/eoleedi/TimeTree-Exporter/commit/f3c6841b4362a24f8bfcda349a60bd4db7560be2))


### Bug Fixes

* run coverage with poetry ([8d7753d](https://github.com/eoleedi/TimeTree-Exporter/commit/8d7753d75cd60a86ce5f653ad5635a24235cf171))
* use 3.14.0-beta.3 on lint and test ([7a1a31c](https://github.com/eoleedi/TimeTree-Exporter/commit/7a1a31cf7a05eb5060aeb82d5c41740c8886257e))

## [0.5.1](https://github.com/eoleedi/TimeTree-Exporter/compare/v0.5.0...v0.5.1) (2025-04-10)


### Miscellaneous Chores

* release 0.5.1 (timestamp hotfix) ([d2222eb](https://github.com/eoleedi/TimeTree-Exporter/commit/d2222eb48397275f08e3dc1182933933638b7c22))

## [0.5.0](https://github.com/eoleedi/TimeTree-Exporter/compare/v0.4.1...v0.5.0) (2025-04-10)


### Features

* support calendar code input (for automations) ([#83](https://github.com/eoleedi/TimeTree-Exporter/issues/83)) ([163be70](https://github.com/eoleedi/TimeTree-Exporter/commit/163be70d2b109cb3b9754d09738a847e1f8c65b3))
* support passing credential with environment variables (for automations) ([#82](https://github.com/eoleedi/TimeTree-Exporter/issues/82)) ([bb701f4](https://github.com/eoleedi/TimeTree-Exporter/commit/bb701f46179c01c728b2c51e82e2bae1b9143ba0))


### Bug Fixes

* migrate from eoleedi/timetree-exporter to eoleedi/tap ([#78](https://github.com/eoleedi/TimeTree-Exporter/issues/78)) ([ea5a0a8](https://github.com/eoleedi/TimeTree-Exporter/commit/ea5a0a8986a5072ae2bb2c9b09341336110488de))
* poetry --without dev ([#84](https://github.com/eoleedi/TimeTree-Exporter/issues/84)) ([d7e7d05](https://github.com/eoleedi/TimeTree-Exporter/commit/d7e7d05dca55f54c5be8b1dca8a66413832337de))


### Documentation

* add homebrew installation method and improve clarity ([49a85ef](https://github.com/eoleedi/TimeTree-Exporter/commit/49a85ef86b202c1dbd735eca73b4ec658f07b3b8))
* add informative badges ([d7d0875](https://github.com/eoleedi/TimeTree-Exporter/commit/d7d0875d512b122a9bb5cd0b3add3f83608b9ef3))
* ignore row order as it's a property for timetree notes ([3fdb415](https://github.com/eoleedi/TimeTree-Exporter/commit/3fdb4157e9e4cf5f307476fd0d18ad99ed9fdc29))
* improve readability ([fdf7281](https://github.com/eoleedi/TimeTree-Exporter/commit/fdf72817529bdbbf25578cb5175dad3aef824dbf))
* more badges ([d0c90cf](https://github.com/eoleedi/TimeTree-Exporter/commit/d0c90cfd955b00f0efec4cbd49b04437949043d7))

## [0.4.1](https://github.com/eoleedi/TimeTree-Exporter/compare/v0.4.0...v0.4.1) (2024-12-01)


### Bug Fixes

* add abbr option -e for --email ([344b959](https://github.com/eoleedi/TimeTree-Exporter/commit/344b959c351ae8c2cb0cc922b80330be80ab4145))

## [0.4.0](https://github.com/eoleedi/TimeTree-Exporter/compare/v0.3.1...v0.4.0) (2024-12-01)


### Features

* automate login and fetch ([8c076e4](https://github.com/eoleedi/TimeTree-Exporter/commit/8c076e4426cf419a0ffb71d1bce41542cbfa695e))
* pass email by param ([cd549d2](https://github.com/eoleedi/TimeTree-Exporter/commit/cd549d2f947e0eb1818c2bad6ca3078a792d2c5d))


### Bug Fixes

* check alarms and recurrences none & add support for public calendar ([65bbcfc](https://github.com/eoleedi/TimeTree-Exporter/commit/65bbcfc2a3668a29b26825c4eb4fd29ae2a7ef1c))
* default saving path to current working directory ([b909a0c](https://github.com/eoleedi/TimeTree-Exporter/commit/b909a0c5a7f34f58fdd5ca7a5f66388381069925))
* filter out deactivated calendars ([c7bdf90](https://github.com/eoleedi/TimeTree-Exporter/commit/c7bdf90b71c6bcfc189ba9b95fe00dd08acc2b5b))
* improve login stability ([bf978bc](https://github.com/eoleedi/TimeTree-Exporter/commit/bf978bc1575236f4a903682b5f524d6931b2f801))
* remove irrelavent info of cal id ([618b233](https://github.com/eoleedi/TimeTree-Exporter/commit/618b233e78167c983b88c6ac21e71f3a90d7732a))
* return None if events can't be found ([b34b136](https://github.com/eoleedi/TimeTree-Exporter/commit/b34b1362f1010c578491816cd027f02f1d012d43))
* typo, last-modify should be last-modified ([2f77e92](https://github.com/eoleedi/TimeTree-Exporter/commit/2f77e925ea7b755b7be17534263c5bfbd6058ee9))
* use Union for python 3.9 compatability ([fa37615](https://github.com/eoleedi/TimeTree-Exporter/commit/fa37615a1d15cc50be9841a7a9e86912e3398d95))


### Reverts

* support public calendar events ([c9b75ba](https://github.com/eoleedi/TimeTree-Exporter/commit/c9b75bad8b25d9e958b3705445689177c7bee144))


### Documentation

* remove requirements as it is specified in requirements.txt ([507922e](https://github.com/eoleedi/TimeTree-Exporter/commit/507922eb6226c4fbb2e109b949e8c9503dc3546b))
* update README ([feaba4d](https://github.com/eoleedi/TimeTree-Exporter/commit/feaba4d1925aa4cc8883f54df8cc2829f41cb678))

## [0.3.1](https://github.com/eoleedi/TimeTree-Exporter/compare/v0.3.0...v0.3.1) (2024-07-17)


### Bug Fixes

* alerts are not properly implemented (fix [#39](https://github.com/eoleedi/TimeTree-Exporter/issues/39)) ([#41](https://github.com/eoleedi/TimeTree-Exporter/issues/41)) ([20859de](https://github.com/eoleedi/TimeTree-Exporter/commit/20859dec779bd397799ad3b7ff27667d94aa4836))
* use zoneinfo instead of dateutil.tz to solve TZID=CEST not recognized by google cal issue ([fbae55e](https://github.com/eoleedi/TimeTree-Exporter/commit/fbae55ea49f1f4889afa04f0fbbd35c794017996))


### Documentation

* formatting ([f53a1ae](https://github.com/eoleedi/TimeTree-Exporter/commit/f53a1ae421ef620bbfcbee361fa34062f9945a68))

## [0.3.0](https://github.com/eoleedi/TimeTree-Exporter/compare/v0.2.3...v0.3.0) (2024-04-20)


### Features

* parse category and skip memo ([#33](https://github.com/eoleedi/TimeTree-Exporter/issues/33)) ([0166f6f](https://github.com/eoleedi/TimeTree-Exporter/commit/0166f6f53284927b89a9a830e830f9d8318877e9))


### Bug Fixes

* add __version__ attribute in the package ([d3ed38f](https://github.com/eoleedi/TimeTree-Exporter/commit/d3ed38f67cf73c9f15025f2078d5454b4c372132))


### Reverts

* add version in attribute in package ([ec0960b](https://github.com/eoleedi/TimeTree-Exporter/commit/ec0960b686b8e290209f89427a4d815911ac139b))

## [0.2.3](https://github.com/eoleedi/TimeTree-exporter/compare/v0.2.2...v0.2.3) (2024-04-10)


### Documentation

* move assets into docs folder ([2931fb2](https://github.com/eoleedi/TimeTree-exporter/commit/2931fb212f2e78f89ba849ee6510b237c5372db3))

## [0.2.2](https://github.com/eoleedi/TimeTree-exporter/compare/v0.2.1...v0.2.2) (2024-04-09)


### Bug Fixes

* define main function in __main__.py to match the script ([#28](https://github.com/eoleedi/TimeTree-exporter/issues/28)) ([24cceba](https://github.com/eoleedi/TimeTree-exporter/commit/24ccebafee8198f8acb0862b722c0c63182bd845))


### Documentation

* update Changelog's URL ([05e9d58](https://github.com/eoleedi/TimeTree-exporter/commit/05e9d58282cd9657d749aaea542dc3b13554f401))

## [0.2.1](https://github.com/eoleedi/TimeTree-exporter/compare/v0.2.0...v0.2.1) (2024-04-09)


### Bug Fixes

* use now as dtstamp ([#24](https://github.com/eoleedi/TimeTree-exporter/issues/24)) ([36c2d23](https://github.com/eoleedi/TimeTree-exporter/commit/36c2d2392bf964de9c8823b23b24f8802162923b))

## [0.2.0](https://github.com/eoleedi/TimeTree-exporter/compare/v0.1.0...v0.2.0) (2024-04-09)


### Features

* map parent_id to iCal's RELATED-TO ([#15](https://github.com/eoleedi/TimeTree-exporter/issues/15)) ([6780cbe](https://github.com/eoleedi/TimeTree-exporter/commit/6780cbea0d907135605a30363ccdf5b7ea467b47))


### Bug Fixes

* accept negative timestamp on all platform ([#23](https://github.com/eoleedi/TimeTree-exporter/issues/23)) ([f2bf2f7](https://github.com/eoleedi/TimeTree-exporter/commit/f2bf2f7c342275f3beb3a3af3406c063929efab2))
* Discard TimeTree's Birthday Event ([#17](https://github.com/eoleedi/TimeTree-exporter/issues/17)) ([aa407ba](https://github.com/eoleedi/TimeTree-exporter/commit/aa407ba468e8f1396fd75373094aec3535ffbeb5))

## 0.1.0 (2024-04-06)


### Features

* argparse ([#12](https://github.com/eoleedi/TimeTree-exporter/issues/12)) ([1eae588](https://github.com/eoleedi/TimeTree-exporter/commit/1eae588f96e462dc12f9c5998c88b5582c25e0d5))
* created & last-modify ([fab8d76](https://github.com/eoleedi/TimeTree-exporter/commit/fab8d76c380c175cc4b7e8cba6fbc740bafe31f6))
* first commit - basic title, time, and alert function ([bac0eca](https://github.com/eoleedi/TimeTree-exporter/commit/bac0ecab5f9d778f9e5113c988cbbcf024367600))
* geo (location lat & lon) ([3547100](https://github.com/eoleedi/TimeTree-exporter/commit/3547100430ab817aea98937e6e8ab4e3cc33fea3))
* note and url ([61adb88](https://github.com/eoleedi/TimeTree-exporter/commit/61adb887f35d1d456b610a6ac19bcf35b5b96438))
* recurrences ([5c37911](https://github.com/eoleedi/TimeTree-exporter/commit/5c37911b584ba022f2114340612ee5572d8ec265))


### Bug Fixes

* full day event & timezone issue ([41467ab](https://github.com/eoleedi/TimeTree-exporter/commit/41467ab0942c8a5ded425bbe73ca44de62481d56))
* write to file after parsing all the files ([bc0fd7f](https://github.com/eoleedi/TimeTree-exporter/commit/bc0fd7f20c12410cf2e548b4c419f89a775a5845))


### Documentation

* add detailed description & remove the API limitation ([edeea3a](https://github.com/eoleedi/TimeTree-exporter/commit/edeea3aacfa64acaf5479912350c219941845702))
* add detailed instructions and info ([70c1e89](https://github.com/eoleedi/TimeTree-exporter/commit/70c1e89ec8a6b7172919f02c37ca54964953f911))
* add newline ([cc5275a](https://github.com/eoleedi/TimeTree-exporter/commit/cc5275a33a01bf1c67db22ed01b5e7402fcf17c2))
* add recommendation and remove in-development warning ([776d5f2](https://github.com/eoleedi/TimeTree-exporter/commit/776d5f271b8127c724f8d3be03e54e1ab41e52b1))
* bump icalendar from 5.0.11 to 5.0.12 ([a934c7b](https://github.com/eoleedi/TimeTree-exporter/commit/a934c7bdc53b8206ef7e37af7af3a0585a5d0abc))
* finish all day ([e23021e](https://github.com/eoleedi/TimeTree-exporter/commit/e23021e24cc9f038bdc070eea530f331bb3e1fde))
* fix typo ([248b669](https://github.com/eoleedi/TimeTree-exporter/commit/248b669c7027f37035778385d38902ec569ddf70))
* update document for pip installation method ([83cfaea](https://github.com/eoleedi/TimeTree-exporter/commit/83cfaea4ec55ad38836e9cd7c11896343b1915f9))
* use absolute path for images ([0bf9e33](https://github.com/eoleedi/TimeTree-exporter/commit/0bf9e33da0e2afe8ae84b085e07357b47ade1080))
