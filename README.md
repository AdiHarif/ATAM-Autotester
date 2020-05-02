# ATAM-Autotester
automated testing script for Technion ATAM class (234118)


this script is for ATAM students to check their homework assignments. 

in order to use the script (currently only compatible with HW1):
    1) boot the vm image, taken from the class website (tested on VMware image)
    2) clone the repository 
    3) copy all asm files you would like to test to the repo. 
        * please keep all files with their original names and use submition format, with only text section for your writen code and nothing else
    4) use the terminal to run autotester.py from the main folder only
    5) after running the script, all of your programs outputs will be under the "last_run_output" folder of each question  

to add your tests to the repo, please push your files to "test-adding" branch with well formated files as explained below
each question has its own directory, just put your files there.

input files format:
    .section .data
    AAT_input:
    <variable-declerations>
    AAT_out:
    <variable-declerations>
    AAT_io_end:

output files format:
    <variable-declerations>

* <variable-declerations> is in the same format as declaring variables in gas, for example - a: .int 42
* the only variable types currently supported are .ascii, .int, .quad
* the only numeric base currently supported for variables is decimal 
* the declerations in the output file must match the output section of the input file, in labels and types (not values), in order to parse the output correctly
* the output files must end with an empty line 
* all of the output memory section of the test (from AAT_out to AAT_io_end), and all of it, will be compared with the programs output to determine whether the test passed or not 
* in the output file, all line without a label should start with a single space before the type decleration
* output files should not contain ant empty lines, except fo rthe last line


writen by Adi Harif, dedicated for all the awsome CS students in the Technion, enjoy <3
