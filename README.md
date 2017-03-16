Password Guessing Framework
===========================

The [Password Guessing Framework](https://password-guessing.org) is an open source tool to provide an automated and reliable way to compare password guessers. It can help to identify individual strengths and weaknesses of a guesser, its modes of operation or even the underlying guessing strategies. Therefor, it gathers information about how many passwords from an input file (password leak) have been cracked in relation to the amount of generated guesses. Subsequent to the guessing process an analysis of the cracked passwords is performed.  

By default the framework supports the following password guessers:

* [John the Ripper in Markov mode (JtR) - Narayanan et al. - 2005](https://github.com/magnumripper/JohnTheRipper)
* [Probabilistic Context Free Grammar (PCFG) - Matt Weir et al. - 2009](https://sites.google.com/site/reusablesec/Home/password-cracking-tools/probablistic_cracker)
* [Ordered Markov Enumerator (OMEN) - Markus Dürmuth et al. - 2013](https://github.com/RUB-SysSec/OMEN)
* [Probability Infinite Chained Elements (PRINCE) - Jens Steube - 2014](https://github.com/jsteube/princeprocessor)

In general though, any guesser that prints the password candidates via ```STDOUT``` can be used with the framework.  
Please note: The aforementioned password guessing / password cracking software is not part nor shipped with the framework and need to be installed separately.

Changelog
---------
Refer to [docs/CHANGELOG.md](docs/CHANGELOG.md) for more information.  
This software is under active development.  
More information on this topic can be found on the project [website](https://password-guessing.org) (www.password-guessing.org).


Dependencies
------------

The framework is written in Python 2.7 and thus requires it installed on the host system.  
In addition, the following modules have to be installed:  

* [psutils](https://pypi.python.org/pypi/psutil): We highly recommend to use [pip](https://pypi.python.org/pypi/pip) to install version 3 of the module. ```apt-get``` will only install version 1.
* [subprocess](https://docs.python.org/2/library/subprocess.html): This module is a mandatory requirement.

We have tested the framework on Ubuntu 14.04 where all the requirements are met by default.  


Installation
------------

On the project [website](https://password-guessing.org) (www.password-guessing.org) you can find a more extensive installation tutorial, a beginners' guide, use case descriptions, guesser installation tutorials, dataset descriptions, experiments, and measurement data, very soon!  

We have created the directory ```/opt/pgf``` in which we installed an instance of all guessers we run with the framework (e.g., ```/opt/pgf/prince```).  
This way, our individual configurations of the guessers wouldn't collide with other guessing instances installed on the system!  
Important to note is that John the Ripper is used for the hash evaluation in cases where hashed input is provided.  
If you consider to run John the Ripper Markov mode as password guesser, you will need two instllations on your hard disk.  
Therefor, install it in ```/opt/pgf/john-hash``` and ```/opt/pgf/john-guess```, respectively.  
The ```/opt/pgf/john-hash``` version, which is utilized as hash evaluator by the framework requires some additional care.  

IMPORTANT NOTE: You have to change two parameters in the ```john.conf``` file in your ```/opt/pgf/john-hash``` directory:  

* Currently, it is required to use the latest bleeding edge release of [John the Ripper (Jumbo Version)](https://github.com/magnumripper/JohnTheRipper)  
* Change the config parameter ```StatusShowCandidates``` to ```Y```  
* In section ```[List.External:AutoStatus]``` verify that the ```interval``` is set to ```1000```  


Configuration / Execution
-------------------------

The framework processes a queue of preconfigured "jobs" which are defined in the configuration file ```run.ini```. A job basically means the execution of a certain password guesser. The guessers are preconfigured in the shell scripts in the folder ```scripts```. The scripts execute the training command (if provided by the guesser) and the guessing command. To configure a job, you find detailed descriptions about the different parameters in the comments at the top of the ```run.ini```. Some parameters are required for all jobs, others are optional. The default values for the optional parameters can be found in the ```DEFAULT``` section of the file. Furthermore, there are a couple of special parameters which are used for features independent from any job. These parameters are also to be set in the ```DEFAULT``` section.  

Once set up, a job execution is split into 3 phases:

* Preparation: Generates the required output files with a timestamp and unique IDs to identify. Also are the session files of the JtR instance, which is used for the hash evaluation, deleted in order to guarantee that all jobs are started without any previously cracked passwords in the "cache" of JtR.  
* Execution: The execution phase starts the guesser and the analysis module and links the ```STDIN``` and ```STDOUT``` pipes of the started subprocesses.  
* Analysis: The analysis module either receives the generated password candidates directly (for plaintext leaks) or parses the terminal output of John the Ripper (hash evaluator) to gather information about the current cracking status.  

In addition to the regular framework features, we provide a web frontend which uses live data to plot guess-number graphs and shows the progress of the current job and the overall progress of the PGF run.

Before you run the framework we suggest to test the single "Guesser Wrapper Scripts", e.g., via ```./scripts/PRINCE.sh /opt/pgf/leaks/myspace_training.txt 10```.  
If you can see the generated passwords, you should give it a try to execute the framework simply by running ```python main.py```.  
If you have trouble with the "Guesser Wrapper Scripts" make sure all directories are correctly setup and check whether the scripts are executable (```chmod +x /scripts/PRINCE.sh```).  


Extension
---------

The framework is designed to be easily extendable for specific needs and use cases.  
Mainly the following components can be extended:  

* Input formats  
* Analysis capabilities (plugins)  

By default, the Password Guessing Framework supports the input formats **pure plaintext** and **pure hash**, meaning input files with one password/hash value per line. Also the widely spread **withcount** leaks can be used as input files for the framework without any adaptations. Parsers for other input formats, e.g., shadow hash files, can easily be implemented.

For the extension of analysis capabilities, the analysis module provides a method to execute plugin-code which is run after all candidates have been processed.  

![Alt text](/docs/screenshots/architecture.png?raw=true "Architecture of the PGF")

Output
------

The framework creates a couple of output files for a run in the local ```results``` folder. Besides the ```log.txt``` which includes log and debug messages, a ```jobs.json``` is created which holds information about the configured jobs of the current run. It will be overwritten for each new PGF run but when backing up the output files after a successful run, the ```jobs.json``` receives a timestamp and an unique identifier to be able to connect it with the rest of the output files of that run.  

The progress and the cracking success is written into a **CSV-file** for each guesser, respectively. The files serve on the one hand as input for the live visualization module, on the other hand they open the ability to plot detailed Guess-number graphs with **GnuPlot** or similar software after the comparision is done. The actualization interval is set to 1000 by default, meaning every 1000 candidates the file is updated with the amount of processed candidates, the amount of cracked passwords and the percentage in regard of the total passwords in the input file (leak).  


Web Frontend
------------

![Web Frontend](/docs/screenshots/webfrontend.png?raw=true "Web Frontend")

To use the optional web visualization frontend, simply follow these steps:

* Move to the working directory ```passwordguessingframework\utils\visualization\dynamic``` in the terminal.
* Make sure that the file ```webserver.py``` is executable. Use ```chmod +x webserver.py``` to make it executable if necessary.
* Use ```./webserver.py``` to start the server.
* Click the ```click_me.html``` in the directory mentioned above or navigate to "http://localhost:31338/utils/visualization/dynamic/frontend/static/index.html" in your browser directly (you can bookmark this url).
* You can easily access the web frontend on a remote machine via an SSH tunnel. (```ssh somehost -L 31338:127.0.0.1:31338```)

The frontend shows the progress of the current PGF run along with information about the cracking success, the job queue etc.

License
-------

The **Password Guessing Framework** is licensed under the MIT license.  
Please note: The dynamic visualization module utilizes the Highcharts JS (by Torstein Honsi 2014) library which is only free of use in non-commercial software projects. Refer to [docs/LICENSE](docs/LICENSE) for more information.  
