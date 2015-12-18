'''
:author: Fabian Langer
:contact: fabian.langer@rub.de

:author: Robin Flume
:contact: robin.flume@rub.de

'''

import time
import sys
from subprocess import Popen, PIPE

class Executor(object):
    ''' This class executes the password guesser(s).
    '''

    def __init__(self, job):
        ''' Generator.
        '''
        self.job = job
        self.logger = job.logger


    def execute(self):
        ''' Starts the execution module depending on the content of the password file.
        Either the guesser is started and it's generated password candidates analyzed, or, if the content are hash values,
        also John the Ripper is used to hash the candidates for a comparison of the guesses and the passwords from the file.

        :requires: All shell scripts have to be in the '/scripts/' directory of the PGF and also need to be executable! Use the command '(sudo) chmod +x [skript]' to make them all executable!
        '''
        # subprocess 1: --> GUESSER GENERATES PW CANDIDATES
        self.logger.debug('Starting Password Guesser!')
        sh_guess = ['./%s' % str(self.job.sh_guess), self.job.training_file, str(self.job.max_guesses)]
        path = r'./scripts/'
        p_guesser = Popen(sh_guess, cwd=path, stdin=PIPE, stdout=PIPE, stderr=sys.stderr)


        # subprocess 2: --> JtR HASHES PW CANDIDATES FOR COMPARISION
        p_john_hash = None
#         if self.job.filetype == 'hashvalues':         # not working, as filetype is determined in analysis.py (subprocess)
        if 'hash' in self.job.pw_format:                # workaround for line above
            if self.job.max_guesses is not None:
                cmd = './pgf/execution/stopper.py %s' % str(self.job.max_guesses)
            else:
                cmd = './pgf/execution/stopper.py %s' % str(self.job.terminate_guessing)
            cmd_stopper = [cmd]
            path = r'./'
            self.logger.debug('Starting the Stopper!')
            p_stopper = Popen(cmd_stopper, cwd=path, stdin=p_guesser.stdout, stdout=PIPE, stderr=PIPE, shell=True)

            cmd = str(self.job.jtr_command)
            cmd_john = [cmd]
            path = str(self.job.jtr_dir)
            self.logger.debug('Starting John the Ripper for the hash evaluation!')
            self.logger.debug(str(self.job.jtr_command))
            #TODO: 'shell=True' highly discouraged. Other option? Without 'shell=True': --> Error 'no such file or directory!'
            p_john_hash = Popen(cmd_john, cwd=self.job.jtr_dir, stdin=p_stopper.stdout, stdout=PIPE, stderr=PIPE, shell=True)


        self.logger.debug('Starting analysis.py!')
        # subprocess 3: --> ANALYSIS processes candidates / JtR output
        # './pgf/analysis/analysis.py' needed in command so value of "path" can be './', otherwise logger error when writing to logfile!
        cmd_analysis = ['./pgf/analysis/analysis.py',
                        str(self.job.label),
                        str(self.job.pw_format),
                        str(self.job.pw_file),
                        str(p_guesser.pid),
                        str(self.job.analysis_interval),
                        str(self.job.terminate_guessing),
                        str(self.job.jtr_pot_file),
                        str(self.job.output_file),
                        str(self.job.progress_file),
                        str(self.job.plot_file)]
        path = './'
        if p_john_hash is None:
            # JtR IS NOT RUNNING (plaintext input) --> piping stdout-pipe of guesser directly to analysis
            p_analysis = Popen(cmd_analysis, cwd=path, stdin=p_guesser.stdout, stdout=sys.stdout, stderr=sys.stderr)
        else:
            # JtR IS RUNNING (hash input) --> piping stdout-pipe of JtR to analysis
            # --> EXPLANATION: 'p_john_hash.stderr' is used as stdin as the status lines of JtR (printed with the '--external=AutoStatus' command).
            #     These lines are printed via the std.err pipe of John. Stdout is used to pritn the cracked passwords.
            p_analysis = Popen(cmd_analysis, cwd=path, stdin=p_john_hash.stderr, stdout=sys.stdout, stderr=sys.stderr) 


        # wait for JtR to finish cracking
        if p_john_hash is not None:
            # read lines from Johns output pipe in order be able to (relevantly) read only it's stderr pipe (status lines)
            while p_john_hash.poll() is None:
                _ = p_john_hash.stdout.readline()
            self.logger.debug("John the Ripper has finished cracking!")

        # wait for the guesser to terminate
        p_guesser.wait()
        self.logger.debug('Password guessing is done!')

        # wait for the analysis module to terminate
        p_analysis.wait()
        self.logger.debug('Analysis is done!')
