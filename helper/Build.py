import os
import subprocess
import shutil
from os.path import isfile, join
import sys

# class BuildManager(object):
# 	def __init__(self):
# 		self.builds = []

# 	def detectBuildSettings(self):
# 		path = "./settings/"
# 		self.builds = [ Build(f) for f in os.listdir(path) if isfile(join(path,f)) and f.endswith(".mk") ]

class Build(object):
		
	def __init__(self, settingsfile):
		self.settingsfile = settingsfile
		self.result_dir = "./builds/"+settingsfile+"/"
		self.source_dir = "./hyrise/"
		self.build_dir = "./hyrise/build/"
		self.build_dir_org = "./hyrise/build_org/"
		self.log_dir = "./logs/"
		self.logfilename = self.log_dir+self.settingsfile+"_log.txt"
		self.verbose = False
		self.build_files = ["hyrise_server", "perf_regression", "libaccess.so", "libbackward-hyr.so", "libebb.so", "libftprinter-hyr.so", "libgtest-hyr.so", "libhelper.so", "libio.so", "libjson.so", "liblayouter.so", "libnet.so", "libstorage.so", "libtaskscheduler.so", "libtesting.so"]

		if not isfile("./settings/"+self.settingsfile):
			raise Exception("Settings file not existing:" + self.settingsfile)

		self.setup_build()
		self.make_all()

	def setup_build(self):
		# copy settings file
		if os.path.isfile(self.source_dir+"settings.mk"):
			os.remove(self.source_dir+"settings.mk")
		shutil.copy2("./settings/"+self.settingsfile, self.source_dir+"settings.mk")
		
		# cleanup leftover from old runs
		if os.path.exists(self.build_dir_org):
			# remove symlink
			if os.path.exists(self.build_dir[:-1]):
				os.unlink(self.build_dir[:-1])
			# move build dir_org to build
			os.rename(self.build_dir_org, self.build_dir)

		# create build folder if necessary
		if not os.path.exists(self.result_dir):
			# clean build dir so we can copy it
			self.make_clean()
			# rename build dir to build_org so we can create a symlink
			os.rename(self.build_dir, self.build_dir_org)
			# copy build dir
			shutil.copytree(self.build_dir_org, self.result_dir, symlinks=False, ignore=None)
			# create symlink to build folder
			os.symlink("."+self.result_dir, self.build_dir[:-1])
		else:
			# rename build dir to build_org so we can create a symlink
			os.rename(self.build_dir, self.build_dir_org)
			# create symlink to build folder
			os.symlink("."+self.result_dir, self.build_dir[:-1])

	def make_clean(self):
		cwd = os.getcwd()
		os.chdir(self.source_dir)
		self.print_status("Clearing build enviroment")
		proc = subprocess.Popen(["make clean"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
		(out, err) = proc.communicate()
		os.chdir(cwd)
		if self.verbose: print out

	def make_all(self):
		logfile = open(self.logfilename,"w")
		cwd = os.getcwd()
		os.chdir(self.source_dir)
		self.print_status("Building system")
		proc = subprocess.Popen(["make -j8"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
		for line in proc.stdout:
		    if self.verbose:
		    	print line
		    else:
		    	sys.stdout.write(".")
		    	sys.stdout.flush()
		    logfile.write(line)
		    logfile.flush()
		print "."
		(out, err) = proc.communicate()
		os.chdir(cwd)
		logfile.close()
		if not self.check_build_results():
			raise Exception("Something went wrong building Hyrise. Settings: " + self.settingsfile)

	def check_build_results(self):
		for f in self.build_files:
			if not os.path.isfile(self.result_dir+f):
				print "Error: Missing File " + self.result_dir+f
				return False
		return True

	def print_status(self, status):
		print self.settingsfile + ": " + status + "..."

	def log(self, command, message):
		with open(self.logfile,"a+") as f:
			f.write(command)
			f.write("\n")
			f.write("###################")
			f.write("\n")
			f.write(message)
			f.write("\n")


		 	