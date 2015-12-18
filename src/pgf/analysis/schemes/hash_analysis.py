# -*- coding: utf-8 -*- 
# DO NOT REMOVE THE LINE ABOVE!

'''
This module provides the class to analyse leaked password hashes.
:author: Robin Flume
:contact: robin.flume@rub.de
'''

import re
import os
import time
from pgf.log.logger import Logger
from pgf.analysis.schemes.scheme_template import AnalysisScheme


class HashAnalysis(AnalysisScheme):
    ''' Analysis class for hashed password leaks.

    :param label: Label of the current job
    :param pws_multi: Dict of passwords/hashes (key) and as values another dict of two counters. 
    One for the occurrences of the pw/hash in the leak ('occ') and one to count the lookups ('lookups')
    by the analysis module (^=amount of duplicately generated candidate)
    :param pw_counter: Counter of overall passwords in the leak
    :param error_counter: Amount parsing errors
    :param jtr_pot_file: '.pot' file of JtR to parse for cracked candidates.
    :param output_file: Path to the output file.
    :param progress_file: Path to the progress file
    :param plot_file: Path to the plot file
    :param analysis_interval: Analysis interval to update the progress file.
    '''
    def __init__(self, label, pws_multi, pw_counter, error_counter, jtr_pot_file, output_file, progress_file, plot_file, analysis_interval):
        ''' Generator.
        '''
        # Initiate logger
        self.logger = Logger()
        self.logger.basicConfig('DEBUG')        # set logger level to DEBUG

        self.logger.debug('Starting Hash Analysis')

        self.label = label

        self.jtr_pot_file = jtr_pot_file
        self.output_file = output_file
        self.progress_file = progress_file
        self.plot_file = plot_file

        self.analysis_interval = analysis_interval
        self.interval_counter = 0

        self.pws_multi = pws_multi                  # Dict to store the passwords from the file including an occurence-counter for each password
        self.pw_counter = pw_counter                # counter for the amount of passwords (hashes) in the leak
        self.pws_unique_counter = 0                 # counter for the amount of unique passwords (hashes) in the leak
        self.guesses = 0                            # counter for the candidates
        self.cracked_counter = 0                    # counter for the no. of cracked passwords (multi)
        self.error_counter = error_counter          # counter for the errors occuring during the file-parsing
        self.cracked_pws = {}                       # Dict to store the cracked passwords and the number of guesses to crack the pw
        self.x_axis_values = list()                 # List to store the intervals for the plot file

        # Definitions of regular expressions to parse the JtR status lines
        self.guesses_re = re.compile('[0-9]*p')
        self.cracked_counter_re = re.compile('^[0-9]*')

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
        with open(path, 'a') as f:                                      # open file
            if type(lines) is list:                                     # list of lines passed
                for line in lines:                                      # iterate through lines in the list
                    if not line.endswith('\n'):
                        line = '%s\n' % line                            # append newline char
                    f.write(line) 
            else:
                line = lines                                            # single line (string) passed
                if not line.endswith('\n'):
                    line = '%s\n' % lines                               # append newline char
                f.write(line)


    def parse_x_axis_values(self):
        ''' Parse the values for the x-axis of the plot.
        '''
        with open(self.plot_file, 'r') as f:
            header_line = f.readline()                                  # read first line of plot file
        temp = header_line.split(',')
        temp.pop(0)                                                     # pop 'Categories'
        temp.pop(0)                                                     # pop 0
        for value in temp:
            self.x_axis_values.append(int(value))


    def update_plot_file(self, percentage):
        ''' Appends the provided value (percentage) to the last line of the plotfile.
        '''
        with open(self.plot_file, 'r') as f:
            lines = f.readlines()
        last_line = lines[len(lines)-1][:-1]  #.replace('\n', '')       # get last line and remove '\n'
        last_line_new = "%s,%s\n" % (last_line, "%.3f" % percentage)    # append value to last line in file
        lines[len(lines)-1] = last_line_new                             # update last line
        with open(self.plot_file, 'w') as f:                            # write lines back to file
            for line in lines:
                f.write(line)


    def process_status_line(self, line):
        ''' Processes the status lines of JtR.
        Received lines will look like this: '736g 4008p 0:00:00:04  152.0g/s 828.0p/s 828.0c/s 885086C/s carama..marcia'
        
        :param line: ONE status line, received by the analysos.py.exeute() method.
        '''
        # parse amount of processed candidates
        temp = self.guesses_re.findall(line)[0]                         # get '4008p'
        temp = temp[:-4] + '000'                                         # remove p and replace 8 by 0 (and resepctively '4' and '12')
        self.guesses = int(temp)                                        # cast '4000' to int
        try:
            # parse amount of cracked pws
            self.cracked_counter = int(self.cracked_counter_re.findall(line)[0])
        except ValueError:
            self.logger.debug("A parsing error occured for JtR terminal-line <%s>" % line)
        # calculate the percentage of cracked passwords BEFORE entire block is processed
        percentage_cracked = float(self.cracked_counter)/float(self.pw_counter)*100
        try:
            if self.guesses == self.x_axis_values[0]:
                self.update_plot_file(percentage_cracked)               # update plotfile
                self.x_axis_values.pop(0)                               # remove value already written value for
        except IndexError:      # silently ignore 'Index Out of Range' errors if more candidates are generated than specified for the x_axis of the plotfile
            pass
        # update progress_file
        if self.guesses >= (self.analysis_interval * self.interval_counter):
            self.interval_counter += 1
            # write the current status into the file '[output_file]_progress.txt'
            status_line = '%d,%d,%7.3f\n' % (self.guesses, self.cracked_counter, percentage_cracked)
            self.write_line_to_file(self.progress_file, str(status_line))


    def process_candidates(self):
        ''' Required only for plaintext analysis.
        '''
        pass


    def parse_jtr_pot_file(self):
        ''' Parse the PGF.pot file of JtR to determine which passwords have been cracked.
        '''
        with open(self.jtr_pot_file, 'r') as f:
            for line in f:
                splitline = line.split(':')
                pw = ':'.join(splitline[1:])[:-1]                       # get last element of split-list ('pw\n') and remove '\n'
                self.cracked_pws[pw] = 0                                # add the candidate and a 0 for its guessing no. as not guessing-no. can be determined from the '.pot' file
                if len(self.cracked_pws) == self.cracked_counter:       # only read the cracked amount of pws from the jtr pot file
                    break


    def count_unique_hashes(self):
        ''' Counts the total amount of unique hashes in the leak.
        '''
        self.pws_unique_counter = 0                                     # reset prior to counting
        for _, value in self.pws_multi.items():
            if value['occ'] == 1:
                self.pws_unique_counter += 1


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

        # iterate through all cracked pws (and the counters per pw)
        for pw in self.cracked_pws.iterkeys():
            length_counter += len(pw)                   # add length of pw to counter
            # add (no. of found chars in pw * counter of pw occurrance) to the counters
            letters_counter += len(letters_re.findall(pw))
            digits_counter += len(digits_re.findall(pw))
            symbols_counter += len(symbols_re.findall(pw))

        # calc. the average(s)
        try:
            self.avg_length = float(length_counter) / float(self.cracked_counter)
            self.avg_letters = float(letters_counter) / float(self.cracked_counter)
            self.avg_digits = float(digits_counter) / float(self.cracked_counter)
            self.avg_symbols = float(symbols_counter) / float(self.cracked_counter)
        except ZeroDivisionError:           # no pw cracked --> ignore error as average values will stay 0
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
        ''' Generates, edits and self.logger.debugs the analysis results.
        '''
        self.logger.debug("Generating analysis results. This may take a while!")

        self.parse_jtr_pot_file()           # parse pot file of JtR
        self.count_unique_hashes()          # call analysis function prior to printing the result below
        self.categorize_pws()               # call analysis function prior to printing the results below
        self.calc_average_chars()           # call analysis function prior to printing the results below

        output = list()                     # list of lines to write to the output file

        output.append("\n")
        output.append("**** **** **** **** RESULTS OF <%s> **** **** **** ****" % self.label)
        output.append("")
        output.append("         Total hashes: %15s" % '{:,}'.format(self.pw_counter))
        output.append("        Unique hashes: %15s" % '{:,}'.format(self.pws_unique_counter))
        output.append("      Multiple hashes: %15s" % '{:,}'.format(len(self.pws_multi) - self.pws_unique_counter))
        output.append("       Parsing errors: %15s" % '{:,}'.format(self.error_counter))
        output.append("")
        output.append("        Total guesses: %15s" % '{:,}'.format(self.guesses))
        output.append("")
        output.append("            Uncracked: %15s" % '{:,}'.format(self.pw_counter - self.cracked_counter))
        output.append("")
        percentage_unique = (float(len(self.cracked_pws))/float(self.pw_counter)) * 100
        output.append("       Cracked hashes: %15s (%6.3f%%) (Multiple occurences cannot be determined from JtR output!)" % ('{:,}'.format(self.cracked_counter), percentage_unique))
        output.append("-->  [a-Z           ]: %15s" % '{:,}'.format(self.only_letters_counter))
        output.append("-->  [     0-9      ]: %15s" % '{:,}'.format(self.only_digits_counter))
        output.append("-->  [          !?&%%]: %15s" % '{:,}'.format(self.only_symbols_counter))
        output.append("-->  [a-Z  0-9      ]: %15s" % '{:,}'.format(self.letters_digits_counter))
        output.append("-->  [a-Z       !?&%%]: %15s" % '{:,}'.format(self.letters_symbols_counter))
        output.append("-->  [     0-9  !?&%%]: %15s" % '{:,}'.format(self.digits_symbols_counter))
        output.append("-->  [a-Z  0-9  !?&%%]: %15s" % '{:,}'.format(self.letters_digits_symbols_counter))
        output.append("")
        output.append("      Averages per pw:")
        output.append("               length: %15.2f" % self.avg_length)
        output.append("              letters: %15.2f" % self.avg_letters)
        output.append("               digits: %15.2f" % self.avg_digits)
        output.append("              symbols: %17.4f" % self.avg_symbols)
        output.append("\n")

        # write analysis results to file
        self.write_line_to_file(self.output_file, output)

        # print analysis results
        for line in output:
            print line

        # run analysis plugins if existent
        self.execute_analysis_plugins()
