# Changelog

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
