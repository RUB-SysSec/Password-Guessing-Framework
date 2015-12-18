# -*- coding: utf-8 -*- 
# DO NOT REMOVE THE LINE ABOVE!

'''
This module provides the class to analyse plaintext passwords.
:author: Robin Flume
@conatct: robin.flume@rub.de
'''

import re
import os
import time
from pgf.log.logger import Logger
from pgf.analysis.schemes.scheme_template import AnalysisScheme

class PlaintextAnalysis(AnalysisScheme):
    ''' Analysis class for plaintext password leaks.

    :param label: Label of the current job
    :param pws_multi: Dict of passwords/hashes (key) and as values another dict of two counters. 
    One for the occurrences of the pw/hash in the leak ('occ') and one to count the lookups ('lookups')
    by the analysis module (^=amount of duplicately generated candidate)
    :param pw_counter: Counter of overall passwords in the leak
    :param error_counter: Amount parsing errors
    :param output_file: Path to the output file.
    :param progress_file: Path to the progress file
    :param plot_file: Path to the plot file
    '''

    def __init__(self, label, pws_multi, pw_counter, error_counter, output_file, progress_file, plot_file):
        ''' Generator.
        '''
        # Initiate logger
        self.logger = Logger()
        self.logger.basicConfig('DEBUG')                     # set logger level to DEBUG

        self.logger.debug('Starting Plaintext Analysis')

        self.label = label

        self.output_file = output_file
        self.progress_file = progress_file
        self.plot_file = plot_file

        self.pws_multi = pws_multi              # Dict to store the passwords from the file including an occurence-counter for each password
        self.pw_counter = pw_counter            # counter for the amount of passwords in the leak
        self.pws_unique_counter = 0             # counter for the amount of unique passwords in the leak
        self.guesses = 0                        # counter for the candidates
        self.duplicate_candidates = 0           # counter for candidates that have been generated multiple times
        self.duplicate_guesses_total = 0        # counter for the total amount of dublicate lookups
        self.cracked_counter = 0                # counter for the no. of cracked passwords (multi)
        self.cracked_unique_counter = 0         # counter for the amount of cracked passwords that occured only once in the leak 
        self.error_counter = error_counter      # counter for the errors occuring during the file-parsing
        self.cracked_pws = {}                   # Dict to store the cracked passwords and the number of guesses to crack the pw
        self.x_axis_values = list()             # List to store the intervals for the plot file

        # Declaration of counters for analysis of cracked pws
        self.only_letters_counter = 0
        self.only_digits_counter = 0
        self.only_symbols_counter = 0
        self.letters_digits_counter = 0
        self.letters_symbols_counter = 0
        self.digits_symbols_counter = 0
        self.letters_digits_symbols_counter = 0

        # Declarations for the calculation of average char occurences
        self.avg_length = 0.0
        self.avg_letters = 0.0
        self.avg_digits = 0.0
        self.avg_symbols = 0.0

        # Parse the values written into the plot file by the Preparation module.
        self.parse_x_axis_values()
        # Write guesser label to file
        self.write_line_to_file(self.plot_file, "%s,0.000" % self.label)


    def write_line_to_file(self, path, lines):
        ''' Write a single line or a list of lines to the specified file.

        :param file: Path of the file to write in
        :param lines: List-type object of lines to write, or a single string
        '''
        with open(path, 'a') as f:                                  # open file
            if type(lines) is list:                                 # list of lines passed
                for line in lines:                                  # iterate through lines in the list
                    if not line.endswith('\n'):
                        line = '%s\n' % line                        # append newline char
                    f.write(line) 
            else:
                line = lines                                        # single line (string) passed
                if not line.endswith('\n'):
                    line = '%s\n' % lines                           # append newline char
                f.write(line)


    def parse_x_axis_values(self):
        ''' Parse the values for the x-axis of the plot.
        '''
        with open(self.plot_file, 'r') as f:
            header_line = f.readline()                              # read first line of plot file
        temp = header_line.split(',')
        temp.pop(0)                                                 # pop 'Categories'
        temp.pop(0)                                                 # pop 0
        for value in temp:
            self.x_axis_values.append(int(value))


    def update_plot_file(self, percentage):
        ''' Appends the provided value (percentage) to the last line of the plotfile.
        '''
        with open(self.plot_file, 'r') as f:
            lines = f.readlines()
        last_line = lines[len(lines)-1][:-1]  #.replace('\n', '')       # get last line and remove '\n'
        last_line_new = "%s,%s\n" % (last_line, "%.3f" % percentage)   # append value to last line in file
        lines[len(lines)-1] = last_line_new                             # update last line
        with open(self.plot_file, 'w') as f:                            # write lines back to file
            for line in lines:
                f.write(line)


    def process_candidates(self, candidate_block):
        ''' Starts the analysis.

        :param candidate_block: list-type collection of password candidates received by the server.
        '''
        for candidate in candidate_block:
            self.guesses += 1                                                   # increment guessing counter
            if candidate in self.pws_multi:                                     # did the candidate crack a password?
                if self.pws_multi[candidate]['lookups'] == 0:                   # password has not yet been cracked
                    self.pws_multi[candidate]['lookups'] += 1                   # increment lookup-counter --> candidate has already been received
                    self.cracked_counter += self.pws_multi[candidate]['occ']    # add the amount of occurences in the leak of the cracked pw
                    if self.pws_multi[candidate]['occ'] == 1:
                        self.cracked_unique_counter += 1                        # increment counter of cracked pws that occured uniquely
                    self.cracked_pws[candidate] = self.guesses                  # add the candidate and its guessing no. to the dict
                else:
                    self.pws_multi[candidate]['lookups'] += 1                   # increment lookup-counter --> candidate has already been received
            try:
                if self.guesses == self.x_axis_values[0]:
                    # calculate the percentage of cracked passwords BEFORE entire block is processed
                    percentage_cracked = float(self.cracked_counter)/float(self.pw_counter)*100
                    self.update_plot_file(percentage_cracked)                   # update plotfile
                    self.x_axis_values.pop(0)                                   # remove value already written value for
            except IndexError:      # silently ignore 'Index Out of Range' errors if more candidates are generated than specified for the x_axis of the plotfile
                pass

        # calculate the percentage of cracked passwords at the end of any block processing to write it to the progress file
        percentage_cracked = float(self.cracked_counter)/float(self.pw_counter)*100
        # write the current status into the file '[output_file]_progress.txt'
        status_line = '%d,%d,%7.3f\n' % (self.guesses, self.cracked_counter, percentage_cracked)
        self.write_line_to_file(self.progress_file, str(status_line))


    def parse_jtr_pot_file(self):
        ''' Required for hash analysis, but will be called from analysis.py.execute for plaintext as well.
        '''
        pass


    def count_unique_pws(self):
        ''' Counts the total amount of unique passwords in the leak.
        '''
        self.pws_unique_counter = 0                         # reset prior to counting
        for _, value in self.pws_multi.items():
            if value['occ'] == 1:
                self.pws_unique_counter += 1


    def count_duplicate_guesses(self):
        ''' Counts the amount of pw candidates which have been genereated multiple times by the guesser
        as well as the total amount of duplicates.
        '''
        for occ_lookups in self.pws_multi.itervalues():
            lu_count = occ_lookups['lookups']
            if lu_count > 1:                                # a lookup of 0 means 'pw uncracked'; 1 means 'pw_cracked'; 
                                                            # >1 means 'candidate generated AT LEAST twice'
                self.duplicate_candidates += 1              # increment counter for candidates that have been generated multiple times
                self.duplicate_guesses_total += lu_count    # add amount of duplicate lookups to the counter                                                        


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
        # Declaration of regular expressions
        only_letters_re = re.compile('^[a-zA-Z]*$')
        only_digits_re = re.compile('^[0-9]*$')
        only_symbols_re = re.compile('^[\s\%\$\^\*\@\&\/\#\!\?\_\-\+\.\,\=\:\;\'\"\<\>\(\)\{\}\[\]]*$')
        letters_digits_re = re.compile('^[a-zA-Z0-9]*$')
        letters_symbols_re = re.compile('^[a-zA-Z\s\%\$\^\*\@\&\/\#\!\?\_\-\+\.\,\=\:\;\'\"\<\>\(\)\{\}\[\]]*$')
        digits_symbols_re = re.compile('^[0-9\s\%\$\^\*\@\&\/\#\!\?\_\-\+\.\,\=\:\;\'\"\<\>\(\)\{\}\[\]]*$')
        letters_digits_symbols_re = re.compile('^[a-zA-Z0-9\s\%\$\^\*\@\&\/\#\!\?\_\-\+\.\,\=\:\;\'\"\<\>\(\)\{\}\[\]]*$')

        # Start analysis of characters in the cracked pws
        for pw in self.cracked_pws.iterkeys():
            if only_letters_re.search(pw):
                self.only_letters_counter += 1
                continue
            if only_digits_re.search(pw):
                self.only_digits_counter += 1
                continue
            if only_symbols_re.search(pw):
                self.only_symbols_counter += 1
                continue
            if letters_digits_re.search(pw):
                self.letters_digits_counter += 1
                continue
            if letters_symbols_re.search(pw):
                self.letters_symbols_counter += 1
                continue
            if digits_symbols_re.search(pw):
                self.digits_symbols_counter += 1
                continue
            if letters_digits_symbols_re.search(pw):
                self.letters_digits_symbols_counter += 1
                continue


    def calc_average_chars(self):
        ''' Calculates the average of the following per cracked pw:
        --> letters
        --> digits
        --> symbols
        '''
        #  Declaration of regular expressions
        letters_re = re.compile('[a-zA-Z]')
        digits_re = re.compile('[0-9]')
        symbols_re = re.compile('[\s\%\$\^\*\@\&\/\#\!\?\_\-\+\.\,\=\:\;\'\"\<\>\(\)\{\}\[\]]')

        # Counter declarations
        length_counter = 0
        letters_counter = 0
        digits_counter = 0
        symbols_counter = 0
        occ_counter = 0

        # iterate through all cracked pws (and the counters per pw)
        for pw in self.cracked_pws.iterkeys():
            occ_counter = self.pws_multi[pw]['occ']
            length_counter += len(pw) * occ_counter                                     # add length of pw to counter
            letters_counter += len(letters_re.findall(pw)) * occ_counter    
            digits_counter += len(digits_re.findall(pw)) * occ_counter
            symbols_counter += len(symbols_re.findall(pw)) * occ_counter

        # calc. the averages
        try:
            self.avg_length = float(length_counter) / float(self.cracked_counter)
            self.avg_letters = float(letters_counter) / float(self.cracked_counter)
            self.avg_digits = float(digits_counter) / float(self.cracked_counter)
            self.avg_symbols = float(symbols_counter) / float(self.cracked_counter)
        except ZeroDivisionError:                                                       # no pw cracked --> ignore error as average values will stay 0
            pass


    def execute_analysis_plugins(self):
        ''' Searches the 'analysis_plugins' folder for scripts to execute along with the default analysis modules.
        '''
        try:
            plugins = os.listdir(os.path.abspath('./analysis_plugins'))
            temp = list(plugins)
            for script in temp:
                if script[0] == '_':
                    self.logger.debug("The analysis-plugin <%s> will be skipped." % script)
                    plugins.remove(script)                                          # skip files with filename starting with '_'
            if len(plugins) > 0:
                self.logger.debug("Executing %d analysis plugins..." % len(plugins))
                for script in plugins:
                    self.logger.debug("Starting plugin <%s>" % script)
                    path = os.path.abspath('./analysis_plugins/%s' % script)
                    execfile(path,{'self_name':script,
                                   'label':self.label,
                                   'pws_multi':self.pws_multi,
                                   'pw_counter':self.pw_counter,
                                   'pws_unique_counter':self.pws_unique_counter,
                                   'guesses':self.guesses,
                                   'cracked_counter':self.cracked_counter,
                                   'cracked_pws':self.cracked_pws, 
                                   'output_file':self.output_file
                                   })
            else:
                self.logger.debug("No analysis plugins found.")
        except Exception, e:
            self.logger.debug(str(e))


    def gen_report(self):
        ''' Generates, edits and prints the analysis results.
        '''
        self.logger.debug("Generating analysis results. This may take a while!")

        self.count_duplicate_guesses()  # count duplicate candidates and guesses
        self.count_unique_pws()         # call analysis function prior to printing the result below
        self.categorize_pws()           # call analysis function prior to printing the results below
        self.calc_average_chars()       # call analysis function prior to printing the results below

        output = list()                 # list of lines to write to the output file

        # append lines to the list
        output.append("\n")
        output.append("**** **** **** **** RESULTS OF <%s> **** **** **** ****" % self.label)
        output.append("")
        output.append("         Total passwords: %15s" % '{:,}'.format(self.pw_counter))
        output.append("        Unique passwords: %15s" % '{:,}'.format(self.pws_unique_counter))
        output.append("      Multiple passwords: %15s" % '{:,}'.format(len(self.pws_multi) - self.pws_unique_counter))
        output.append("          Parsing errors: %15s" % '{:,}'.format(self.error_counter))
        output.append("")
        output.append("           Total guesses: %15s" % '{:,}'.format(self.guesses))
        output.append("Duplicate cand. (unique): %15s" % '{:,}'.format(self.duplicate_candidates))
        output.append("  Total dupl. candidates: %15s (incremented by x if candidate was generated x times by the guesser!)" % '{:,}'.format(self.duplicate_guesses_total))
        output.append("")
        output.append("           Uncracked pws: %15s" % '{:,}'.format(self.pw_counter - self.cracked_counter))
        output.append("")
        percentage_unique = (float(self.cracked_unique_counter)/float(self.pws_unique_counter)) * 100
        output.append("    Cracked pws (unique): %15s (%6.3f%%)" % ('{:,}'.format(self.cracked_unique_counter), percentage_unique))
        percentage_total = (float(self.cracked_counter)/float(self.pw_counter)) * 100
        output.append("     Cracked pws (total): %15s (%6.3f%%) (incremented by x if pw occurred x times in the leak!)" % ('{:,}'.format(self.cracked_counter), percentage_total))
        output.append("  -->   [a-Z           ]: %15s" % '{:,}'.format(self.only_letters_counter))
        output.append("  -->   [     0-9      ]: %15s" % '{:,}'.format(self.only_digits_counter))
        output.append("  -->   [          !?&%%]: %15s" % '{:,}'.format(self.only_symbols_counter))
        output.append("  -->   [a-Z  0-9      ]: %15s" % '{:,}'.format(self.letters_digits_counter))
        output.append("  -->   [a-Z       !?&%%]: %15s" % '{:,}'.format(self.letters_symbols_counter))
        output.append("  -->   [     0-9  !?&%%]: %15s" % '{:,}'.format(self.digits_symbols_counter))
        output.append("  -->   [a-Z  0-9  !?&%%]: %15s" % '{:,}'.format(self.letters_digits_symbols_counter))
        output.append("")
        output.append("         Averages per pw:")
        output.append("                  length: %15.2f" % self.avg_length)
        output.append("                 letters: %15.2f" % self.avg_letters)
        output.append("                  digits: %15.2f" % self.avg_digits)
        output.append("                 symbols: %17.4f" % self.avg_symbols)
        output.append("\n")
        output.append("\n")

        # write analysis results to file
        self.write_line_to_file(self.output_file, output)

        # print analysis results
        for line in output:
            print line
        
        # run analysis plugins if existent
        self.execute_analysis_plugins()
