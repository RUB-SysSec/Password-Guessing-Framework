'''
:author: Robin Flume
:contact: robin.flume@rub.de
'''

import os
import time
import datetime
import uuid


class Preparation(object):
    ''' Class to generate a parser to parse the input file depending on the 'input_format' parameter in the
    configuration file.

    :param logger: Logger instance.
    :param plot_max_x_axis: Value of the maximum guesses to be performed (config param 'plot_max_x_axis') in the current PGF run.
    :param plot_amount_values_x_axis: Amount of values plotted in the graphs per job (on the x-axis).
    '''

    def __init__(self, logger, plot_max_x_axis, plot_amount_values_x_axis):
        ''' Generator.
        '''
        self.logger = logger
        self.plot_max_x_axis = plot_max_x_axis
        self.plot_amount_values_x_axis = plot_amount_values_x_axis
        ts = int(time.time())                       # get timestamp
        self.timestamp = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d_%H-%M-%S')          # convert to human readyble timestamp
        self.uuid_ = str(uuid.uuid4())[:8]                                                           # This uuid is 'self' var as it's needed in 'main.result_backup()' too
        self.plot_file_path = self.create_output_file(os.path.abspath('./results/plot.csv'), uuid=self.uuid_)        # create the [plot_uuid.csv]
        self.plot_file = os.path.basename(self.plot_file_path)
        self.init_plot_file()


    def execute(self, job):
        ''' Runs the preparation-phase.

        :param job: Job instance
        '''
        uuid_ = str(uuid.uuid4())[:8]                    # create new UUID for every job to append to the filenames
        self.logger.debug("Preparing output files for job <%s>" % job.label)
        job.set_plot_file(self.plot_file_path)          # set plot_file path
        # create the output file (csv)
        output_file = self.create_output_file(job.output_file, uuid=uuid_)
        job.set_output_file(output_file)                # update path of output file
        # create the progress file (csv)
        progress_file = self.create_output_file(job.output_file, uuid=uuid_, suffix='progress', ending='csv')
        job.set_progress_file(progress_file)            # set progress_file path
        # init progress file with (0,0,0.000)-line
        self.write_line_to_file(progress_file, '0,0,0.000')


    def create_output_file(self, path, uuid, suffix=None, ending=None):
        ''' Create the output file (csv).

        :param path: Path of the output file to be created.
        :param uuid: UUID to insert in the filename.
        :param suffix: If a suffix is provided, it will be appended to the filename of [output_file] given in the run.ini (a leading '_' is automatically added)
        :param ending: Provide a file ending other than '.csv'. Will only be taken care of if a suffix is provided as well!

        :return: The newly created filepath
        '''
        # split path up into filenme and dir
        filename = os.path.basename(path)
        dir_ = path.replace(filename, "")
        if not os.path.exists(dir_):
            os.makedirs(dir_)                                       # create directory if necessary
        if self.timestamp not in filename:
            path = "%s%s_%s" % (dir_, self.timestamp, filename)     # set timestamp leading to filename
        else:
            path = "%s%s" % (dir_, filename)
        if uuid not in path:
            path = "%s%s_%s" % (path[:path.find(filename)], uuid, filename)
        if suffix is not None:
            index = len(path)-4
            path = "%s_%s%s" %(path[:index], suffix, path[index:])
        if ending is not None:
            path = "%s%s" % (path[:-3], ending)
        f = open(path, 'w')                                         # create output file in directory
        f.close()                                                   # close (yet empty) file
        return path                                                 # return newly constructed path


    def write_line_to_file(self, path, lines):
        ''' Write a single line or a list of lines to the specified file.

        :param file: Path of the file to write in
        :param lines: List-type object of lines to write, or a single string
        '''
        with open(path, 'a') as f:                          # open file
            if type(lines) is list:                         # list of lines passed
                for line in lines:                          # iterate through lines in the list
                    if not line.endswith('\n'):
                        line = '%s\n' % line                # append newline char
                    f.write(line) 
            else:
                line = lines                                # single line (string) passed
                if not line.endswith('\n'):
                    line = '%s\n' % lines                   # append newline char
                f.write(line)                               # write and (automatically) close file (by 'with statement'


    def init_plot_file(self):
        ''' Calculate the values of the x_axis and print the header line to the plot file.
        '''
        plot_values = list()
        interval = self.plot_max_x_axis / self.plot_amount_values_x_axis
        for i in range(self.plot_amount_values_x_axis + 1):
            value = int(i*interval)
            plot_values.append(str(value))
        init_line = 'Categories,%s' % ','.join(plot_values)
        self.write_line_to_file(self.plot_file_path, init_line)         # print init line to plot file
