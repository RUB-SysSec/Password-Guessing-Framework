'''
:author: Fabian Langer
:contact: fabian.langer@rub.de
:author: Robin Flume
:contact: robin.flume@rub.de
'''

from pgf.exceptions.abstract_method import abstract_method

class AnalysisScheme(object):
    ''' Abstract class used for different kinds of input files.

    :param logger: Logger instance.
    :param label: Label of the current job
    :param pws_multi: Dict of passwords/hashes (key) and as values another dict of two counters. One for the occurrences of the pw/hash in the leak ('occ') and one to count the lookups ('lookups') by the analysis module (^=amount of duplicately generated candidate) 
    :param pw_counter: Counter of overall passwords in the leak
    :param error_counter: Amount parsing errors
    :param output_file: Path to the output file
    :param progress_file: Path to the progress file
    '''

    def __init__(self):
        ''' Generator.
        '''
        abstract_method(self)

    def write_line_to_file(self):
        ''' Write a single line or a list of lines to the specified file.

        :param file: Path of the file to write in
        :param lines: List-type object of lines to write, or a single string
        '''
        abstract_method(self)

    def parse_x_axis_values(self):
        ''' Parse the values for the x-axis of the plot.
        '''
        abstract_method(self)

    def update_plot_file(self):
        ''' Appends the provided value (percentage) to the last line of the plotfile.
        '''
        abstract_method(self)

    def process_candidates(self):
        ''' Starts the analysis.

        :param candidate_block: list-type collection of password candidates received by the server.
        '''
        abstract_method(self)

    def parse_jtr_pot_file(self):
        ''' Required for hash analysis, but will be called from analysis.py.execute for plaintext as well.
        '''
        abstract_method(self)

    def count_unique_pws(self):
        ''' Counts the total amount of unique passwords in the leak.
        '''
        abstract_method(self)

    def count_duplicate_guesses(self):
        ''' Counts the amount of pw candidates which have been genereated multiple times by the guesser
        as well as the total amount of duplicates.
        '''
        abstract_method(self)

    def categorize_pws(self):
        ''' Process the cracked passwords and categorize them.
        The function sorts the pws by:
        --> letters only
        --> digits only
        --> symbols only
        --> includes letters and digits
        --> includes letters and symbols
        --> includes letters, digits and symbols
        '''
        abstract_method(self)

    def calc_average_chars(self):
        ''' Calculates the average of the following per cracked pw:
        --> letters
        --> digits
        --> symbols
        '''
        abstract_method(self)

    def execute_analysis_plugins(self):
        ''' Searches the 'analysis_plugins' folder for scripts to execute along with the default analysis modules.
        Those filenames with a leading '_' will be ignored.
        '''
        abstract_method(self)

    def gen_report(self):
        ''' Generates, edits and prints the analysis results.
        '''
        abstract_method(self)
