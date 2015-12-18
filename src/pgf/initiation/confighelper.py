'''
:author: Robin Flume
:contact: robin.flume@rub.de
'''

import ConfigParser
import ast
import os
import datetime
import json
from pgf.initiation.job import Job
from pgf.preparation.preparation import Preparation


class ConfigHelper(object):
    ''' Helper class to parse a configuration file and provide the values to other classes.

    :param path: Absolute path to the configuration file.
    :param logger: Logger-instance
    '''

    def __init__(self, path, logger=None):
        ''' Constructor.
        '''
        if not os.path.isfile(path):
            raise IOError("The path <%s> does not point to a file!" % path)
        self.logger = logger
        self.cp = ConfigParser.ConfigParser()               # create ConfigParser instance
        self.cp.read(path)                                  # parse the config file
        # Preparation instance
        self.preparation = Preparation(logger,
                                       self.get_option('DEFAULT', 'plot_max_x_axis'),
                                       self.get_option('DEFAULT', 'plot_amount_values_x_axis'))
        self.timestamp = self.preparation.timestamp         # get timestamp that is prepended to the other output files
        self.uuid = self.preparation.uuid_


    def parse_jobs(self):
        ''' Parses the run.ini file and creates the jobs to be processed by the framework accordingly.
        Also the 'jobs.json' file is created here.

        :return: List of 'Job' objects.
        '''
        self.logger.debug("Parsing jobs...")
        queue = []
        for section in self.cp.sections():          # each sections defines a Job! The Section [DEFAULT] is silently ignored!
            job = Job(self.logger)
            job.set_label(section)                  # use section-name as label for the job
            job.set_sh_guess(self.get_option(section, 'sh_guess'))
            sh_guess_path = os.path.abspath("./scripts/%s" % job.sh_guess)
            # get lines from the password guesser script to parse it into the jobs.json file
            sh_content = ''
            with open(sh_guess_path, 'r') as guesser_script:
                for line in guesser_script:
                    if (line[0] != '\n'):
                        line = line.replace('\n','')
                        sh_content = "%s, [%s]" % (sh_content, line)
                sh_content = sh_content[2:]         # remove leading '...'
            job.set_sh_content(sh_content)
            job.set_training_file(self.get_option(section, 'training_file'))
            job.set_pw_file(self.get_option(section, 'pw_file'))
            job.set_pw_format(self.get_option(section, 'pw_format'))
            job.set_analysis_interval(self.get_option(section, 'analysis_interval'))
            job.set_terminate_guessing(self.get_option(section, 'terminate_guessing'))
            job.set_max_guesses(self.get_option(section, 'max_guesses'))
            job.set_output_file(self.get_option(section, 'output_file'))
            # setup jtr
            jtr_dir = self.get_option(section, 'jtr_dir')
            jtr_session = self.get_option(section, 'jtr_session_name')
            job.set_jtr_input_format(self.get_option(section, 'jtr_input_format'))
            job.setup_jtr(jtr_dir, jtr_session)
            # execute the Preparation module for the currently parsed job
            self.preparation.execute(job)
            queue.append(job)                       # add job to queue
        # serialize jobs to json file
        self.serialize_jobs_to_json(queue)
        #return job queue
        return queue


    def get_option(self, section, option):
        ''' Returns the value for the provided option parsed from the given section.
        Value will be evaluated if possible, else it will be returned as string.

        :param section: Name of the section
        :param option: Name of the parameter to parse

        :return: Evaluated Value (String, "None", "True", "False", List, etc.)
        '''
        value = self.cp.get(section, option)
        try:
            value = ast.literal_eval(value)
        except ValueError:                          # silently ignore errors and return string-type
            pass
        except SyntaxError:                         # silently ignore errors and return string-type
            pass
        return value


    def serialize_jobs_to_json(self, queue):
        ''' Serializes the job queue of the current run into the 'jobs.json' in the directory "./utils/visualization/dynamic/backend/"
        to be processed by the visualization module.

        :param queue: Job queue
        '''
        abs_path = os.path.abspath("./results/jobs.json")
        queue_length = len(queue)
        with open(abs_path, 'w') as json_file:
            json_file.write('{\n')
            json_file.write('"name" : "jobs",\n')
            date = datetime.date.today()
            json_file.write('"date" : "%s.%s.%s",\n' % (date.day, date.month, date.year))
            json_file.write('"number_of_jobs" : "%d",\n' % queue_length)
            json_file.write('"plot_file" : "%s",\n' % self.preparation.plot_file)
            json_file.write('"jobs" : [\n')
            for job in queue:
                json_file.write(json.dumps(job.prepare_for_json(), sort_keys=True, indent=4))
                queue_length -= 1
                if queue_length > 0:
                    json_file.write(',\n')
                else:
                    json_file.write(']\n')
            json_file.write('}')
        return

    def get_timestamp_uuid(self):
        ''' Returns a string consisting of '[timestamp]_uuid' to prepend it to the jobs.json file during backup of the result files.
        The UUID is the one that is also used for the plot.csv file.
        '''
        return "%s_%s" % (self.timestamp, self.uuid)
