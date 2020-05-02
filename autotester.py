#!/usr/bin/env python3

import os

script_dir = os.getcwd() # Todo finish dir finding


def getFilesList(dir, pattern):
	files_list = []
	os.system('ls {0}/{1} > {0}/ls_out.txt'.format(dir, pattern))
	with open('{0}/ls_out.txt'.format(dir) , 'r') as ls_out:
		files_list = [trimDirFromPath(path) for path in ls_out.read().split()]
	os.system('rm {0}/ls_out.txt'.format(dir))
	return files_list

def removeExtension(file_name):
	i = file_name.rfind('.')
	if (i==-1):
		return file_name
	return file_name[:i]

def trimDirFromPath(path):
	i = path.rfind('/')
	if (i==-1):
		return path
	return path[i+1:]

def removeDups(l):
	return list(dict.fromkeys(l))

def getQuestionsInDir(dir):
	return [removeExtension(f_name) for f_name in getFilesList(dir, 'q*.asm')]

def getTestsList(dir):
	return removeDups([ removeExtension(f_name) for f_name in getFilesList(dir, 'test*')])

def createPrebuildFile(hw, q, test):
	test_dir = '{0}/{1}/{2}'.format(script_dir, hw, q)

	with open('{0}/test.asm'.format(script_dir), 'w') as prebuild:
		prebuild.write('.global _start\n')
		
		with open('{0}/{1}.in'.format(test_dir, test), 'r') as input_file:
			prebuild.write('{0}\n'.format(input_file.read()))
		with open('{0}.asm'.format(q), 'r') as sol_file:
			prebuild.write('{0}\n'.format(sol_file.read()))
		
		prebuild.write('_start:\n')
		
		with open('{0}/fun_call.asm'.format(test_dir) ) as call_file:
			prebuild.write('{0}\n'.format(call_file.read()))
		with open('{0}/mem_print.asm'.format(script_dir) ) as mem_print_file:
			prebuild.write('{0}\n'.format(mem_print_file.read()))
		with open('{0}/exit.asm'.format(script_dir) )as exit_file:
			prebuild.write('{0}\n'.format(exit_file.read()))


def getLabelMap(mem_start_address, expected_out):
	map = {str(mem_start_address):'AAT_out', '0':'NULL'}
	current_address = mem_start_address
	lines = expected_out.split('\n')
	for line in lines:
		i = line.find(' ')
		label = line[:i]
		if (i != 0 ):
			map[str(current_address)] = label[:-1]
		j = line.find(' ', i+1)
		tp = line[i+1:j]
		data = line[j+1:]

		if (tp == '.ascii'):
			current_address += (len(data) -2)
		if (tp == '.int'):
			current_address += ((data.count(',')+1)*4)
		if (tp == '.quad'):
			current_address += ((data.count(',')+1)*8)
	
	return map

def parseOutputFile(hw, q, test):
	parsed_output = ''
	expected_out = ''
	with open('{0}/{1}/{2}/{3}.out'.format(script_dir, hw, q, test), 'r') as expected_out_file:
		expected_out = expected_out_file.read()
	with open('{0}/test.out'.format(script_dir), 'rb' ) as out_file:
		mem_start_address = int.from_bytes(out_file.read(8), 'little', signed=True)
		label_map = getLabelMap(mem_start_address, expected_out)
		lines = expected_out.split('\n')[:-1]
		for line in lines:
			i = line.find(' ')
			label = line[:i]
			j = line.find(' ', i+1)
			tp = line[i+1:j]
			data = line[j+1:]
			parsed_output = parsed_output + label + ' ' + tp + ' '

			if (tp == '.int'):
				byte_count = (data.count(',')+1)*4
				parsed_output = parsed_output + str(int.from_bytes(out_file.read(4), 'little', signed=True) )
				i = 4
				while i<byte_count:
					parsed_output = parsed_output + ', ' + str(int.from_bytes(out_file.read(4), 'little', signed=True) )
					i += 4

			if (tp == '.quad'):
				comma_count = data.find(',')
				label_flag = (comma_count == -1 and (not data.isnumeric()))

				first_value = str(int.from_bytes(out_file.read(8), 'little', signed=True) )
				if (label_flag):
					first_value = label_map[first_value]
				parsed_output = parsed_output + first_value
				byte_count = (comma_count+1)*8
				i = 8
				while i<byte_count:
					parsed_output = parsed_output + ', ' + str(int.from_bytes(out_file.read(8), 'little', signed=True) )
					i += 8

			if (tp == '.ascii'):
				byte_count = len(data) - 2
				parsed_output = parsed_output + ('"{0}"\n'.format(str(out_file.read(byte_count)) ) )
			
			parsed_output = parsed_output + '\n'
	return parsed_output


def performTest(hw, q, test):
	createPrebuildFile(hw, q, test)
	test_asm_file = '{0}_{0}.asm'.format(q, test) 
	if (os.system('as {0}/test.asm -o {0}/test.o'.format(script_dir)) != 0):
		print('		assembler: FAILURE')
		print('		{0} - FAILED'.format(test) )
		return False
	print('		assembler: SUCCESS' )
	if (os.system('ld {0}/test.o -o {0}/test.exe'.format(script_dir)) !=0):
		print('		linker: FAILURE')
		print('		{0} - FAILED'.format(test) )
		return False
	print('		linker: SUCCESS' )
	if (os.system('{0}/test.exe > {0}/test.out'.format(script_dir)) != 0):
		print('		execute: FAILURE' )
		print('		{0} - FAILED'.format(test) )
		return False
	print('		execute: SUCCESS')
	
	output = parseOutputFile(hw, q, test)
	if (output == ''):
		print('		output parsing: FAILURE' )
		print('		{0} - FAILED'.format(test) )
		return False
	print('		output parsing: SUCCESS' )
	with open('{0}/test.parsed_out'.format(script_dir), 'w') as parsed_out:
		parsed_out.write(output)
	
	os.system('diff {0}/test.parsed_out {0}/{1}/{2}/{3}.out > {0}/test.diff_out'.format(script_dir, hw, q, test))

	os.system('cp {0}/test.parsed_out {0}/{1}/{2}/last_run_output/{3}.out'.format(script_dir, hw, q, test) )
	diff_out = ''
	with open('{0}/test.diff_out'.format(script_dir)) as diff_out_file:
		diff_out = diff_out_file.read()
	if (diff_out != ''):
		print('		output diff: FAILURE' )
		print('		{0} - FAILED'.format(test) )
		return False
	
	print('		output diff: SUCCESS' )
	print('		{0} - PASSED!'.format(test) )
	return True

hw = 'HW1' #TODO: add input handling

q_to_check = getQuestionsInDir(os.getcwd())

tests_count = 0
total_tests_passed = 0
for q in q_to_check:
	tests_passed = 0
	print('testing {0}:'.format(q))
	t_list = getTestsList('{0}/{1}/{2}'.format(script_dir, hw, q) )
	for test in t_list:
		print('	{0}:'.format(test))
		tests_passed +=performTest(hw, q, test)
	congrats_str = ''
	if (tests_passed == len(t_list)):
		congrats_str = ' - well done!'
	print('{0} passed {1} tests out of {2}{3}\n'.format(q, tests_passed, len(t_list), congrats_str))
	tests_count += len(t_list)
	total_tests_passed += tests_passed

miztayen_str = ''
if (total_tests_passed == tests_count):
	miztayen_str = ' - MIZTAYEN NASEE!'
print('your {0} passed {1} tests out of {2}{3}'.format(hw, total_tests_passed, tests_count, miztayen_str))
#cleanup


