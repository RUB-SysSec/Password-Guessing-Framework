# Change Log
All notable changes to this project will be documented in this file.
This project adheres to [Semantic Versioning](http://semver.org/).

## [Unreleased]
### Added
- A more convenient way to configure the framework via the run.ini
- Comply to PEP 8 style guide for Python codes

## [0.0.1] - 2015-12-18
### Added
- Initial upload of the framework
- Main modules: Preparation, Execution, Analysis
- Inputformats: plaintext_pure, plaintext_withcount, hash_pure, and parser_template
- Analysis schemes: plaintext_analysis (case A), hash_analysis (case B), and scheme_template
- Guesser Wrapper Scripts: John the Ripper in Markov mode, OMEN, PCFG, and PRINCE
- Post processing module (Push-based notifications)
- Python plugin engine and template class
- New plugins to calculate the Partial Guessing Entropy (alpha-guesswork) + functionality to store correctly guessed passwords
- Dynamic visualization module via Highcharts JS + Python web server
- Static visualization via Gnuplot shell script
- External modules: Logger (log) by Senko Rasic and confighelper class (initiation)

[Unreleased]: https://github.com/RUB-SysSec/Password-Guessing-Framework/compare/v0.0.1...HEAD
[0.0.1]: https://github.com/RUB-SysSec/Password-Guessing-Framework/compare/v0.0.1...HEAD