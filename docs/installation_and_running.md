# Installation and Running

CompGenerator is developed on Ubuntu, running under Windows Subsystem for Linux. It should work fine in any unix-style Python 3.x environment, but no promises.

## 1 Prerequisites

CompGenerator uses Python 3.6 or later, and relies on the open source ReportLab module for PDF file generation and graphics capabilities. Install Python 3.6 or later as appropriate for your operating system (I trust you can google how to do this) and install ReportLab with:

`pip install reportlab`

from whatever command line environment you're using.

## 2 Installation

To install CompGenerator:

1. Clone this repository from GitHub to a local directory
2. Make a symlink from somewhere in your command line's `PATH` variable to CompGenerator.py. For example:

`ln -s ~/repos/CompGenerator/CompGenerator.py /usr/local/bin/CompGenerator.py`

3. If necessary for your operating system, give `execute` permissions to CompGenerator.py and/or the link to it.


# Running CompGenerator

You can adapt CompGenerator to your particular workflow, but here is a best-practices flow you can start out with.

1. Make a competition directory for all your materials for the comp you are helping organize. CompGenerator uses a few different input files and generates three separate PDF output files, so it is nice to have these contained in their own directory. Trying to organize multiple competitions in the same directory would quickly become a quagmire of input and output files.
2. Copy the existing config file and badge template image from CompGenerator's `samples/` directory into your competition directory.
3. Edit the config file to provide the specific information for your competition (the comp name, events, etc.)
4. Using a spreadsheet program of your choice, edit your competitor assignments until you are happy, then export them to a .CSV file in your competition directory. Note that various other WCA tools (including the WCA website) can generate a .CSV file of your competitors and their events to get you started.
5. Run CompGenerator from the command line to generate all the PDFs you need:

  `CompGenerator.py -c my_comp_config.json`

6. Preview the output PDF files to check for mistakes.
7. Print the PDF files, making sure to print the badges double-sided. If you cannot print double-sided, that's ok, but you're in for extra work to match up the back-sides with the front-sides when you stuff the badge sleeves.
8. Cut the printed pages into individual badges and scorecards.

In practice, you will do steps 1 and 2 once for each competition, then iterate over steps 3-6 until you're happy with the results. Only at the end will you print and cut all the materials.

# 4. Running CompGenerator

After editing your config file and exporting your competitor assignment file from your spreadsheet of choice, and creating your badge design template image, generating the PDF files for your badges and scorecards is easy:

1. Go to your command line environment and change to the directory where your input files are
2. Run CompGenerator as:

`CompGenerator.py -c 'name_of_your_config_file'`

Note that this invocation relies on CompGenerator being in your `PATH`, as described above. If you've chosen to install it differently, you can figure out how to invoke it.

The output PDF files will be created in the directory where you invoke CompGenerator.

It is recommended that you review your output files with any Adobe Acrobat Reader or another PDF reader to check for mistakes before printing.

CompGenerator also supports a `--generate` or `-g` flag to tell it specifically which items to generate. This is useful if you tweak something and want to re-generate only one output PDF. The `-g` flag takes a string containing any of:
* "all", to re-generate everything. This is the default.
* "scorecards", to re-generate the round 1 scorecards
* "blanks", to re-generate scorecards for subsequent rounds and other blank scorecards, as specified in the config file
* "badges", to re-generate the competitor badges.

For example, you could specify `-g 'badges blanks'` to re-generate the badges and the blank scorecards, but not the round 1 scorecards.
