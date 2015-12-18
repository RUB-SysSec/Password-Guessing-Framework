'''
:author: Robin Flume
:contact: robin.flume@rub.de
'''

import os

class Job(object):
    ''' This class represents a job 'to do' for the Password Guessing Framework.
    It includes the necessary configurations parsed from the file 'run.ini'.
    '''

    def __init__(self, logger):
        ''' Constructor.
        '''
        self.logger = logger
        # Initiate job attributes with 'None' ...
        self.label = None                   # [JT MyMy] without []
        self.sh_guess = None                # JTR_MARKOV.sh
        self.sh_content = None              # content of sh_file
        self.training_file = None           # /opt/pff/leaks/rockyou_training.txt
        self.pw_file = None                 # /opt/pgf/leaks/myspace_guess.txt
        self.pw_format = None               # plaintext_pure
        self.filetype = None                # plaintext / hashvalues
        self.analysis_interval = None       # 1000
        self.terminate_guessing = None      # 100000000000
        self.output_file = None             # jtr_markov_myspace_myspace.txt
        self.progress_file = None           #_progress.csv
        self.plot_file = None               # [timestamp_plot_[uuid].csv
        self.jtr_dir= None                  # /opt/pgf/john-hash/
        self.jtr_input_format = None        # raw-md5 --> john-hash will be used with parameter '--format=raw-md5'
        self.jtr_session = None             # PGF - will be set in the 'setup_jtr' method
        self.jtr_log_file = None            # PGF.log - will be set in the 'setup_jtr' method
        self.jtr_pot_file = None            # PGF.pot - will be set in the 'setup_jtr' method
        self.jtr_command = None             # ./john --stdin pw_file --session=pcfg_manager --pot=PGF --> will be set in the 'setup_jtr' method
        self.analysis_process = None


    def prepare_for_json(self):
        ''' Prepares a dictionary containing the Job attributes in order to parse it into the 'jobs.json' file for the visualization module.

        :return Dictionary containing job attributes.
        '''
        self_as_dict = dict(self.__dict__)  # Parsing into Dict-object necessaray as otherwise, next line will remove the logger also from the Job-object!
        # adapt dict for easier processing
        self_as_dict.pop('logger')
        self_as_dict.pop('plot_file')
        self_as_dict.pop('jtr_pot_file')
        self_as_dict['runtime'] = 'Pending'
        self_as_dict['output_file'] = os.path.basename(self_as_dict['output_file'])
        self_as_dict['progress_file'] = os.path.basename(self_as_dict['progress_file'])
        return self_as_dict


    # **** SETTER METHODS ****
    def set_label(self, label):
        self.label = label

    def set_sh_guess(self, sh_guess):
        self.sh_guess = sh_guess

    def set_sh_content(self, sh_content):
        self.sh_content = sh_content

    def set_pw_file(self, pw_file):
        ''' Sets the path to the password file.
        If just a filename is given in the 'run.ini' file, the path is modified to point to the default path which is
        '/opt/pgf/leaks'.
        '''
        if not '/' in pw_file:                              # pw_file is just a filename
            pw_file = '/opt/pgf/leaks/%s' % pw_file         # read the file from the default '/opt/pgf/leaks' directory
        self.pw_file = os.path.abspath(pw_file)             # resolve relative paths automatically
        if not os.path.isfile(self.pw_file):
            raise IOError("Password file not found!")
            exit(-1) #TODO: correct/good exit method?

    def set_training_file(self, training_file):
        ''' Sets the path to the password file.
        If just a filename is given in the 'run.ini' file, the path is modified to point to the default path which is
        '/opt/pgf/leaks'.
        '''
        if '/' not in training_file:                                    # training_file is just a filename
            training_file = '/opt/pgf/leaks/%s' % training_file         # read the file from the default '/opt/pgf/leaks' directory
        self.training_file = os.path.abspath(training_file)             # resolve relative paths automatically
        if not os.path.isfile(self.training_file):
            raise IOError("Training file not found!")
            exit(-1) #TODO: correct/good exit method?

    def set_pw_format(self, pw_format):
        self.pw_format = pw_format

    def set_filetype(self, filetype):
        self.filetype = filetype

    def set_analysis_interval(self, analysis_interval):
        self.analysis_interval = analysis_interval

    def set_terminate_guessing(self, terminate_guessing):
        self.terminate_guessing = terminate_guessing

    def set_max_guesses(self, max_guesses):
        self.max_guesses = max_guesses

    def set_output_file(self, output_file):
        ''' Sets the path to the output file (csv).
        If only a filename is given, the file will be created in the default 'results' folder of the PFG.
        If the path is given as a relative path it is automatically resolved int the absolute path as needed among others
        for the C-written analysis module for plaintext passwords.
        '''
        if output_file is None:
            output_file = self.label                            # use the job label as name for thhe output file if not specified
        if not '/' in output_file:                              # output_file is just a filename
            output_file = './results/%s' % output_file          # create the file in the 'results' folder of the PGF
            if not output_file.endswith('.csv') and not output_file.endswith('.txt'):
                output_file = '%s.csv' % output_file            # append file ending if not present
        self.output_file = os.path.abspath(output_file)         # resolve relative paths automatically

    def set_progress_file(self, progress_file):
        self.progress_file = progress_file

    def set_plot_file(self, plot_file):
        self.plot_file = plot_file

    def set_jtr_input_format(self, jtr_input_format):
        self.jtr_input_format = jtr_input_format

    def setup_jtr(self, jtr_dir, jtr_session_name):
        ''' Constructs paths needed to process the JtR output files.

        :param jtr_dir: Installation directory of JtR to hash the received password candidates. A check is performed wether the jtr_dir string meets the requirements of the PGF to process it correctly.
        :param jtr_session_name: Name of the session (DEFAULT: 'PGF') for JtR. The pot-file created by john will be deleted by the framework to not mix up the results of different guesser executions. Using a session solves the problem of deleting files that also include results of other, independent cracking attempts.
        '''
        # Check if 'jtr_dir' is a correct string to process by the PGF 
        if not jtr_dir.endswith('/'):
            jtr_dir = "%s%s" % (jtr_dir, '/')
        if not os.path.isdir(jtr_dir):
            raise IOError("John the Ripper directory not found or is not a directory!")
            exit(-1) #TODO: correct/good exit method?
        else:
            self.jtr_dir = jtr_dir
        # create the paths of the session files of JtR
        self.jtr_session = "%s%s" % (jtr_dir, jtr_session_name)
        self.jtr_pot_file = "%s.pot" % self.jtr_session
        self.jtr_log_file = "%s.log" % self.jtr_session
        if self.jtr_input_format is None:
            self.jtr_command = './john --external=AutoStatus --stdin "%s" --session="%s" --pot="%s"' % (self.pw_file, self.jtr_session, self.jtr_pot_file)
        else:
            self.jtr_command = './john --external=AutoStatus --stdin "%s" --format="%s" --session="%s" --pot="%s"' % (self.pw_file, self.jtr_input_format, self.jtr_session, self.jtr_pot_file)

    def clear_jtr_pot_rec(self):
        ''' Clears the '.pot' and deletes the '.rec' file in the JtR directory to guarantee that every job starts cracking at 'point 0', 
        meaning no previous cracked hash values have been saved and would be skipped.
        '''
        if 'hash' in self.pw_format:
            try:
                f = open(self.jtr_pot_file, 'w')            # clear the file instead of removing which led to "No such file"-Error
                f.close()
            except OSError, e:
                self.logger.debug("The JtR '.pot' file cannot be deleted. <%s>" % str(e))
            try:
                os.remove(self.jtr_log_file.replace('.pot', '.rec'))            # delete the rec file
            except OSError, e:
                self.logger.debug("The JtR '.rec' file could not be deleted. <%s>" % str(e))

    def clear_jtr_log(self):
        ''' Clears the '.log' file in the JtR directory to not let it grow too much with the entries of cracked hashes.
        '''
        if 'hash' in self.pw_format:
            try:
                f = open(self.jtr_log_file, 'w')            # clear the file instead of removing which led to "No such file"-Error
                f.close()
            except OSError, e:
                self.logger.debug("The JtR '.log' file could not be cleared. <%s>" % str(e))
