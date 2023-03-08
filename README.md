# CompGenerator Documentation

CompGenerator is a python script that generates competitor badges and scorecards for use in speedcubing competitions. It is for comp organizers who are comfortable working with text files and a unix-style command line environment.

You give CompGenerator information about your competition, and it gives you PDF files of your competitor badges and scorecards. Print them and run them through a paper cutter, and you're done.

Competitor badges are printed 9 to a sheet, two-sided, sized to fit 2.25x3.5 inch badge holder sleeves such as [these](https://www.amazon.com/dp/B083BHCTVZ). The front side shows your competition's logo, competition name, and competitor name. The back side shows the competitor's individual round-1 schedule and helping group assignments.

Scorecards are printed 4 to a sheet of standard US letter paper. CompGenerator will generate all your round-1 scorecards based on the competitor information you supply. It can print scorecards for subsequent rounds and finals too, but will leave the names blank. You write those in by hand once you know who made it into round 2, etc. CompGenerator can also make extra scorecards with blanks for the competitor name and/or event, because you never know when you might need to write up a scorecard during the competition.

For examples, see the input files and corresponding PDF output files in the `samples/` directory.

(TO DO: add support for creating winner certificates from a template too)

# Usage

CompGenerator is intended to be straightforward to use:

1. Edit your config file to put in any settings you want or change any defaults
2. Create an input file with all of your competitor information
3. Run CompGenerator from the command line to generate all the PDFs you need.

# 1. Setup and Installation

CompGenerator is developed on Ubuntu, running under Windows Subsystem for Linux. It should work fine in any unix-style Python 3.x environment, but no promises.

## 1.1 Prerequisites

CompGenerator uses Python 3.6 or later, and relies on the open source ReportLab module for PDF file generation and graphics capabilities. Install Python 3.6 or later as appropriate for your operating system (I trust you can google how to do this) and install ReportLab with:

`pip install reportlab`

from whatever command line environment you're using.

## 1.2 Installation Instructions

To install CompGenerator:
1. Clone this repository from GitHub to a local directory
2. Make a symlink from somewhere in your command line's `PATH` variable to CompGenerator.py. For example:

`ln -s ~/repos/CompGenerator/CompGenerator.py /usr/local/bin/CompGenerator.py`

3. If necessary for your operating system, give CompGenerator.py and/or the link to it, `execute` permissions.

# 2. Input Files

CompGenerator takes just one input file when invoked--a config file that provides information about your competition and all other settings you might want to change--and uses information from that file to find other files it needs. These include:

* A competitor assignments file in .CSV format that names all your competitors and specifies what each one will be doing during round 1 of each event.
* A competitor badge template image. A recommended size is 750x1050 pixels.

The `samples` directory has examples of all of these files.

## 2.1 Config File Format

The config file tells CompGenerator everything it needs to know about your competition and where to find information about your competitors. This file is a .JSON file, consisting of a dictionary with _key:value_ pairs that provide all of CompGenerator's settings. The settings are loosely grouped into:
* Information about your competition as a whole
* Information about your competitors
* Options for how badges and scorecards should be drawn
* Settings for round 2 and later scorecards.

See the `samples` directory for a config file example.

### 2.1.1 Competition Information

Competition information is given by three key:value pairs, called `"competition"`, `"stages"`, and `"events"`.

The `"competition"` key gives the name of your competition:

  `"competition": "Fargo Flyin' Fingers 2023"`

If the solving stations at your venue are separated into different stages, different rooms, or different areas for whatever reason, the `"stages"` key allows you to specify a dictionary that names each stage, gives a shorthand form for it, and how many solving stations the stage has. For example:

  `"stages": {"Red":["R", 6], "Blue":["B", 6]}`

This denotes that the competition is using two stages, called "Red" and "Blue", with shorthands "R" and "B", and 6 solving stations each. Within the event and group designations present in your competitor assignments file (see below), CompGenerator will distribute the competitors as evenly as possible across the available stages. (To do: If, however, the people competing in a single group can all fit on one stage, CompGenerator will put them all on the same stage so something else can happen concurrently on the other stage.)

You can direct CompGenerator to put events on specific stages if you like; see the documentation for the `events` key, below.

If your competition is not using multiple stages, you can omit the `"stages"` key entirely, or specify it as an empty dictionay (`{}`).

The `"events"` key specifies which events your competition is holding. The value of this key is a dictionary that gives a list of configuration values for each event, keyed to the event's official WCA designation. The order of values in each list is:

* The number of solves competitors will perform.
* The numer of attempts competitors have to meet or exceed the cutoff, or `null` if the event is not using a cutoff.
* The cutoff time to beat. Use `0`, `""`, or `null` if the event is not using a cutoff.
* The time limit after which competitors are automatically assigned a DNF.
* An optional stage for this event to be held on

For example:

```
  "events": {
    "333": [5,null,"","10:00"],
    "555": [5,2,"2:10","4:30"],
    "777": [3,1,"4:45","9:30", "Red"]
  }
```

In this example, the competition is holding the odd-layer cube events. The 3x3 competition is using the standard format of 5 solves, no cutoff, and a 10 minute time limit. 5x5 gives two attempts to meet or beat a 2:10 cutoff, and DNFs the competitor at 4:30. 7x7 only has 3 attempts and gives just 1 attempt versus a cutoff of 4:45, with a time limit of 9:30, and will be held solely on the "Red" stage. Competitors for 3x3 and 5x5 will, by default, be distributed among all availble stages.

The cutoff and time limit values are used to control the layout of scorecards, and will be printed on the scorecards as well for reference during the competition.

The `"custom_events"` key gives CompGenerator the designator, name, and short-name of any non-standard or exhibition events you are holding. The designator is any string you like, but MUST match the column header in your competitor assignments file for the event. The name is the fully written out name of the event. The short-name is an abbreviation that will be used on competitor badges for each person's schedule.

Its format is a list of lists-of-strings. For example, if your comp is holding three exhibition events--Face-Turning Octahedron, Team Blind, and Mirror Blocks, you could specify:

```
  "custom_events": [
    ["FTO", "Face-Turning Octahedron", "FTO"],
    ["TBLD", "Team Blind", "TBLD"],
    ["MBL", "Mirror Blocks", "MBL"]
  ]
```

You may also use the `"custom_events"` mechanism to override CompGenerator's built-in name and short-name for any official events, which you might want to do for non-English competitions:

```
  "custom_events": [
    ["pyram", "пираминкс", "пира"]
  ]
```

Note that the designators of events in your `"events"` key, the column headers in your competitor assignments file (see below), and the designators in your `"custom_events"` (if any), must agree.

### 2.1.2 Competitor Information

Competitor information is given by two keys, `"roles"` and `"assignments"`. 

The `"roles"` key gives a string that indicates what roles people at your competition may be assigned. It uses the C/J/R/S standard used by other group and scorecard generators. The default value is:

  `"roles": "CJRS"`

which indicates that participants at your comp may be assigned the Competitor (C), Judge (J), Runner (R), and Scrambler (S) roles. Omit any letters from the `"roles"` string that you are not using. E.g. if you are not using assigned runners but will be relying on volunteers, you can reduce this to `"CJS"`.

The `"assignments"` key names a comma-separated-values file that tells CompGenerator what you want everyone to be doing during round 1 of each event.

See section 2.2, below, for full details on the contents and format of this file.

The "stars" key gives a dictionary that maps competitor names or WCA IDs to which events they might could set a record in (i.e. events in which they are "stars"). Scorecards for these people will be marked with a gold star in the scrambler signature area, as a reminder to scramblers to make extra-sure that the scrambles are correct. For example:

```
  "stars": {
    "2022KEAL01":["333"],
    "2022KEAD01":["555"],
    "Ash Black":["333","777"],
    "Braden Dillenberg":["FTO"]
  }
```

This would cause those competitors to have stars on their round-1 scorecards for the indicated events. You can omit this key or leave it empty if there are no high-level competitors at your competition, or do not wish to use this feature.

This feature is useful if you have high-level competitors at your competition who might potentially set records, and want to avoid drama or controversy over misscrambles (see https://www.youtube.com/watch?v=NFMUs_lUHpM for a summary of recent related incidents). Scramblers should never misscramble or let an incorrect scramble go out to a competitor, and marking the high-level scorecards in an obvious way helps remind scrambles to do their jobs right.

### 2.1.3 Drawing Options for Badges

CompGenerator supports several options for configuring how it renders badges and scorecards.


The `badge_config` key is a dictionary that holds all badge configuration information. It should contain four sub-keys that give specifics:

```
  "badge_config": {
    "template_image": "sample_comp_badge_template.jpg",
    "name_conf":   [90, 42.5, 16],
    "id_conf":     [90, 22.25, 14],
    "helper_conf": [90, 5.25, 14]
  },
```

The `"template_image"` subkey gives the name of a .JPG or .PNG file of your badge design. This file should have an aspect ratio of 1:1.4. A resolution of 750x1050 pixels works well. The image should leave blank areas or areas with very minimal background design where the competitor's name and WCA id will go. See the example template file in the `samples/` directory.

The `"name_conf"` subkey tells CompGenerator where to position the competitor's name and how big to make it. It is a list of three values, all specified in units of "points" (1 point = 1/72nd of an inch). The first value gives the horizontal center position for the name. The second gives the vertical baseline position for the name. The third gives the point-size for the font.

The `"id_conf"` and `helper_conf` subkeys give the same information, but for the position and size of the competitor's WCA ID and the "Helper" indicator for helpers at your comp (see the Competitor Assignments File section, below, for more information on helpers).

### 2.1.4 General Drawing Options

The `"cut_guides"` key indicates whether CompGenerator should add thin lines to the scorecard and ID badge should be set to either `true` or `false`. The default is `false`, no lines. If you will be using a paper cutter, you likely don't need guides, though if you will be using scissors then they will be helpful.

  `"cut_guides": false`

### 2.1.5 Round 2 and Later Scorecards

The following settings tell CompGenerator what scorecards you want it to generate for any rounds after round 1. These are different because the names of the competitors are not known in advance--you don't know who will qualify for round 2 or finals.

One `"scorecard_blanks"` key provides all of this information. It is a dictionary whose keys are the event identifiers for any event that has more than 1 round. The values of these keys are also dictionaries, whose keys are the names of any subsequent rounds for that event, and whose values are how many scorecards you want CompGenerator to make. For example:

```
  "scorecard_blanks": {
      "333": {"2": 48, "Final": 16},
      "555": {"Final": 12},
      "777": {"Final": 12},
      "FTO": {"Final": 12},
      "blank": {"__": 20}
  }
```

In this example, the 3x3 event has a round called "2", which needs 48 scorecards, and a round called "Final" which needs 16. 5x5, 7x7, and FTO all only have one additional round called "Final", needing 12 scorecards each.

It is also helpful to have fully blank scorecards, with no event name, competitor name, or round listed, so that organizers can simply write a scorecard on-the-spot for any purpose that may arise. To support this, CompGenerator watches for a special "blank" event in the `"scorecard_blanks"` dictionary, and if it finds one, will print scorecards where the event name is left blank, the competitor name is left blank, and the round and the competing group are provided as fill-in-the-blank spots.

## 2.2 Competitor Assignments file

The competitor assignments file is a simple comma-separated-values file (.CSV) that tells CompGenerator what you want the participants at your competition to be doing during round one of each event. Supporting this style of roles-assignment, which gives the comp organizer complete control over group assignments and helping roles (versus more automated programs) is a primary motivation for the development of CompGenerator. You can create, edit, and save .CSV files using any mainstream spreadsheet program (recommended) or even just a text editor.

The first line gives the purpose of each column. Columns 1 and 2 are for the competitor's name and WCA ID. Subsequent columns give the names of your events, using the official WCA designators for each event. For example, '444' for 4x4. Custom events (see above) can use whatever abbreviation you want.

Each line after that lists one competitor and specifies what that person is doing in each event. These assignments are in C/J/R/S format, for each role of Competing/Judging/Running/Scrambling. If a competitor has multiple roles in an event, each is separated by a semicolon. Group assignments are given by adding a group number after the letter for the role. For example:

```
Name,WCA ID,333,555,777,FTO
Ada Ke,2022KEAD01,C3;J4,S1,R2,C1
Adam Dabling,2022DABL01,C4;J5,C2;J1,C1;R2,
Marcy Dabling,,J1;J2,R1;J2,J1;J2,
```

In this example, Ada Ke is competing in group 3 of 3x3, judging for group 4, and competing in group 1 of FTO. She has been assigned to scramble for group 1 of 5x5 and as a runner for group 2 of 7x7. She is competing in group 1 of FTO. Adam Dabling is competing, judging, and running for the indicated groups of 3x3, 5x5, and 7x7, but has no roles during FTO.

Marcy Dabling--presumably Adam's mother who is driving him to the competition--has no competitor assignments, but several helper assignments. CompGenerator will detect this and add a "Helper" notation to her badge. Note that the WCA website has no capability to let people sign up to be helpers for a competition. If you want helper badges, you will need to add those people manually to your assignments file, as they will not be present when you export the competitor information from the WCA website.

This CSV format looks ugly and is hard to work with in plain text, but is compatible with Microsoft Excel, Google Sheets, and any other spreadsheet program you might care to name. If possible, it is recommended to load and save these files in UTF-8 encoding to preserve any accented characters such as é or ú in competitors' names.

See also the example `sample_comp_assignments.csv` file in the `samples/` directory.

### 2.2.1 Competitor Numbers

By default, CompGenerator will assign a competitor number to each person, based on their order in your assignments file. These numbers are included on scorecards for each competitor as well as on the back side of their badge.

However, if your assignments file has a column with the string `Number` in the header row, CompGenerator will use the values in that column instead. Note that CompGenerator performs no checking of the values in this column to guarantee uniqueness or anything else.

# 3. Staging

Staging refers to the practice of dividing the solving stations at a competition into groups called "stages". This is at the organizer's discretion. Typically, stages are given colors such as "red" or "blue", and the physical solving stations have colored tablecloths to match. For competitions in larger physical spaces, dividing the solving stations into stages can greatly improve the logistics of running each round.

CompGenerator does not force you to use stages. If your config file has a `stages` key containing the names, "tags", and number of solving stations of each stage, then it will use that information to distribute competitors in each competing group to the stages in a number of different ways.

## 3.1 Round-Robin Staging

The default method is "round robin", where the competitors in a competing group are distributed evenly among the available stages. Think of it like dealing cards: the competitors are the cards, and they get "dealt" out in round-robin fashion to each stage. This ensures that the stages are as evenly filled as possible, so each stage should complete the competing group at about the same time.

For example, if you have 50 people competing in 3x3 group 1, and you have three stages called "Red", "Blue", and "Green", CompGenerator will assign 17 people to Red, 17 to Blue, and 16 to Green.

CompGenerator will use this method in most situations, because typically the number of competitors in a group is greater than the total number of solving stations at the competition.

## 3.2 Assigned Staging

If you want a particular event to take place on a single, specific stage, you can specify the stage for that event in your config file. See the documentation above for the `events` key of the config file. All competitors, regardless of what competing group they are in or how many people are competing, will be assigned to the stage you specify in the config file.

## 3.3 Single Staging

If a particular event has a small number of people competing, then each competing group might fit on a single stage. That is, there might be a way to assign the groups to the stages such that the number of people in the group is no larger than the number of solving stations on the stage. This can provide two efficiency benefits in running the competition: One, it allows you to use fixed seating so competitors do not have to move back and forth between the competitor waiting area and the solving stations. Two, it allows competing groups to run in parallel on multiple stages instead of one group having to finish before the next group starts.

For example, Suppose you have two stages, Red and Blue, with 6 solving stations each. Suppose you have 22 people competing in 7x7. If you define four competing groups, (C1, C2, C3, and C4) in your assignments file with 6, 6, 5, and 5 competitors each, then you see how C1 and C2 could run in parallel on the Red and Blue stages with fixed seating, and likewise C3 and C4.

CompGenerator will automatically detect this type of situation and use single staging where possible.

Presently, it is not possible to disable single staging so as to force CompGenerator to use round robin. Assigned staging, however, will always override single staging.

# 4. Running CompGenerator

After editing your config file and exporting your competitor assignment file from your spreadsheet of choice, and creating your badge design template image, generating the PDF files for your badges and scorecards is easy:

1. Go to your command line environment and change to the directory where your input files are
2. Run CompGenerator as:

`CompGenerator.py -c 'name_of_your_config_file'`

Note that this invocation relies on CompGenerator being in your `PATH`, as described above. If you've chosen to install it differently, you can figure out how to invoke it.

The output PDF files will be created in the same directory.

It is recommended that you review your output files with any Adobe Acrobat Reader or another PDF reader to check for mistakes before printing.

CompGenerator also supports a `--generate` or `-g` flag to tell it specifically which items to generate. This is useful if you tweak something and want to re-generate only one output PDF. The `-g` flag takes a string containing any of:
* "all", to re-generate everything. This is the default.
* "scorecards", to re-generate the round 1 scorecards
* "blanks", to re-generate scorecards for subsequent rounds and other blank scorecards, as specified in the config file
* "badges", to re-generate the competitor badges.

For example, you could specify `-g 'badges blanks'` to re-generate the badges and the blank scorecards, but not the round 1 scorecards.


# 5. General Suggestions

## 5.1 Assignments
Part of a comp organizer's job is to create a good competition experience for competitors. Carelessly assigning roles can make for a poor experience. It will not always be possible to assign roles such that everyone has a great experience, but in general, try to avoid assigning someone a helping role for the group immediately before their competing group.

For example, if you assign someone "C2;R1", you're saying they should be a runner in group 1 of some event, but then immediately compete in group 2. This gives the competitor no time to warm up for the event, and asks them to compete when they may still be hot and sweaty or out of breath from running.

Likewise, over-assigning the same person to many jobs in many events means that they will have less time to socialize with their cubing friends.

Where feasible, try to spread the work evenly and give people time to practice and socialize.

# 5.2 Selecting Scramblers and Runners

A good competition depends very heavily on the behavior and performance of the people scrambling the puzzles and running puzzles to and from the scrambling station. Competition organizers should assign these roles with some care.

Review your list of registered competitors, looking for people who you know to be competent, mature enough, and physically capable of performing the roles.

A good scrambler is someone who is a high-level competitor in their event (i.e. regularly makes it to the final round), and who you know to have a responsible disposition. That is, you want someone you can trust to both scramble accurately, and to fix any mis-scrambles rather than just sending them out due to laziness.

A good runner is someone who understands the flow of a group, who understands competitors' needs to be clearly directed to scrambling stations, who can accurately read and pronounce the names of competitors as their turns come up, and who can speak loudly enough to be heard over the general background noise of a competition. Young children, though they are the future of cubing, generally do not have these capabilities. Rely on your older cubers, or at the very least people who have attended several competitions in the past.

# 5.3 Assigning Roles to Delegates

Delegates at the competition are important people. Not merely because they are delegates, but because they have the knowledge and authority to make judgments about any situations that occur during the competition.

While delegates often make very good scramblers and runners, if possible it is better not to assign them any helper roles during the competition. They are expected to help out anyway, but they need to be available to adjudicate any situations that arise (notably, decisions on whether to apply +2s and other penalties). You don't want your competition to fall behind schedule because the delegates were busy doing other things.

Delegates are virtually always also competitors in the event. This, plus the need for delegates to be available to handle situations that arise means that you should not put all your delegates in the same competing group of a given event. Spread them out so that at least one delegate is always free to manage the competition.