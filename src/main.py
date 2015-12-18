#!/usr/bin/env python

''' This script starts the Password Guessing Framework.
:author: Robin Flume
:contact: robin.flume@rub.de
:author: Fabian Langer
:contact: fabian.langer@rub.de
'''
import os
import timeit
import shutil
import json
from subprocess import Popen, PIPE
from collections import OrderedDict
from math import fmod
from pgf.log.logger import Logger
from pgf.execution.executor import Executor
from pgf.initiation.confighelper import ConfigHelper


def final_processing(logger, script_name):
    ''' Runs the shell script provided by the parameter 'final_processing' in the 'DEFAULT' section of the 'run.ini' file. 
    If the value is 'None', no final processing will be done.
    '''
    try:
        if script_name is not None:
            logger.debug("Starting the final processing of the progress files as defined in <%s>." % script_name)
            script_name = "./%s" % script_name
            results_path = '%s' % os.path.abspath('./results/')
            sh_final_processing = [script_name, str(results_path), 'testrun_results.eps', '10mio Guesses Against the Gmail Leak (trained w/ rockyou leak)']
            path = r'./scripts/'
            p_final_processing = Popen(sh_final_processing, cwd=path, stdin=PIPE, stdout=PIPE, stderr=PIPE)
            out, err = p_final_processing.communicate()
            print out
            print err
        else:
            logger.debug("Final processing skipped! No script name provided!")
    except Exception, e:
        logger.error("An error occured in method <final_processing>: <%s>" % str(e))


def result_backup(dest_dir, timestamp_uuid):
    ''' Copy all created output files to [dest_dir].

    :param timestamp_uuid: String of timestamp and uuid to prepend to the jobs.json during backup.
    '''
    if not dest_dir.endswith('/'):
        dest_dir = "%s/" % dest_dir
    if not os.path.isdir(dest_dir):
        print "Backup directory not found!"
        exit(-1)
    src_dir = os.path.abspath('./results')
    src_files = os.listdir(src_dir)
    for filename in src_files:
        filepath = os.path.join(src_dir, filename)
        if (os.path.isfile(filepath)):
            shutil.copy(filepath, dest_dir)
            if filename == 'jobs.json':
                os.chdir(dest_dir)
                os.rename(filename, '%s_%s' % (timestamp_uuid, filename))
#             if filename != 'log.txt':
#                 os.remove(filepath)                # remove file from './pgf/results' after backing it up


def main():
    ''' Starts the Password Guessing Framework.

    :requires: a configuration file named "run.ini" in the directory "[...]/Password Guessing Framework/configfiles/"
    '''

    runtimes = OrderedDict()                        # dict to store the runtimes of each job
    start = timeit.default_timer()

    # Initiate logger
    logger = Logger()
    logger.basicConfig('DEBUG')                     # set logger level to DEBUG

    # Initiate ConfigHelper instance
    ch = ConfigHelper('./configfiles/run.ini', logger=logger)

    # parse jobs from 'run.ini'
    job_queue = ch.parse_jobs()
    job_counter = 0                                 # helper to get corrent job-object from json file at the end of each job run

    # Clear 'PGF.log' file in te JtR directory to reset it
    # The path of the logfile will be generated and stored while parsing the jobs thus the get
    # it from the first job in the list
    job_queue[0].clear_jtr_log()


    # iterate through the job queue
    while len(job_queue) > 0:
        logger.debug("Remaining jobs: %2d\n\n" % len(job_queue))
        job = job_queue.pop(0)      # get first job in queue

        job_start = timeit.default_timer()
        logger.debug("Starting Job <%s>" % job.label)

        # Clear 'PGF.pot' and 'PGF.rec' files in te JtR directory to reset hashing state for each job
        job.clear_jtr_pot_rec()
        
        # Preparation is called from the config helper

        # Executor instance
        executor = Executor(job)
        executor.execute()

        # Analysis is called from the executor as it is run as a subprocess!

        # calc runtime of the current job
        job_end = timeit.default_timer()
        job_runtime = job_end - job_start
        job_human_runtime = ("%2dd:%2dh:%2dm:%2ds" % ((job_runtime/86400),
                                                      (fmod(job_runtime,86400)/3600),
                                                      (fmod(job_runtime,3600)/60),
                                                      (fmod(job_runtime,60))
                                                      ))
        with open(job.output_file, 'a') as output_file:                     # write runtime of the current job the according outfile
            output_file.write("\nRuntime: '%s':  %s" % (job.label, job_human_runtime))

        # job finished!
        logger.debug("---------------- JOB <%s> DONE! --------------------------\n" % job.label)
        logger.debug("Runtime: %28s: %s\n" % (job.label, job_human_runtime))

        # add runtime to list of job-runtimes
        runtimes[job.label] = job_human_runtime

        # Write Runtime of curent job into jobs.json
        with open('./results/jobs.json', 'r') as f:
            json_obj = json.load(f)
            json_obj['jobs'][job_counter]['runtime'] = job_human_runtime
        with open('./results/jobs.json', 'w') as f:
            f.write(json.dumps(json_obj, sort_keys=True, indent=4))
        job_counter += 1


    # **** **** WHILE LOOP ENDS HERE! **** ****


    # calc runtime of PGF
    end = timeit.default_timer()
    runtime = end - start
    human_runtime = ("%3dd:%2dh:%2dm:%2ds" % ((runtime/86400),
                                              (fmod(runtime,86400)/3600),
                                              (fmod(runtime,3600)/60),
                                              (fmod(runtime,60))
                                              ))

    logger.debug("---------------- ALL JOBS PROCESSED! --------------------------\n")

    # Run the shell script processing the progress files
    final_processing(logger, ch.get_option('DEFAULT', 'final_processing'))

    # print summery of job runtimes
    logger.debug("Job-Runtimes:")
    for label, rt in runtimes.iteritems():
        logger.debug("%37s: %s" % (label, rt))
    logger.debug("Overall Runtime:%s%s\n" % (22*' ', human_runtime))
    logger.debug("PGF closed.")

    # backup all created files AT LAST STEP!
    result_backup(ch.get_option('DEFAULT', 'backup_dir'), ch.get_timestamp_uuid())


if __name__ == '__main__':
    main()