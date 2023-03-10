#! /usr/bin/python
# CompGenerator -- generate scorecards, badges, group assignment PDFs for printing out.
# Uses the open source 'reportlab' library -- see docs.reportlab.com

# To Do: permit an optional fifth value in the events arrays in the config file which,
# if present, puts that event on the specified stage.

import argparse
import json
import csv
import re
from collections import defaultdict
import math

from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter

# some page drawing globals
w, h = letter
w2, h2 = w/2, h/2
m = 36

eventNames = { # Map of WCA event ids to friendly names and short-names, which are used on the scorecards and competitor schedules
    "222": ("2x2x2 Cube","2x2"),
    "333": ("3x3x3 Cube","3x3"),
    "444": ("4x4x4 Cube","4x4"),
    "555": ("5x5x5 Cube","5x5"),
    "666": ("6x6x6 Cube","6x6"),
    "777": ("7x7x7 Cube","7x7"),
    "clock": ("Clock","Clock"),
    "sq1": ("Square-1","Sq-1"),
    "333bf": ("3-Blind","3BLD"),
    "444bf": ("4-Blind","4BLD"),
    "555bf": ("5-Blind","5BLD"),
    "333fm": ("Fewest Moves","FMC"),
    "333oh": ("One Handed","OH"),
    "minx": ("Megaminx","Mega"),
    "pyram": ("Pyraminx","Pyra"),
    "skewb": ("Skewb","Skewb"),
    "333mbf": ("Multi Blind","MBLD"),
    "blank": ("","") # the "blank" event is a cheap hack that makes it easier to implement printing blank, just-in-case scorecards,"").
    }

def show_help():
    print("""Comp Generator -- generate printable PDFs for WCA competition scorecards and competitor badges.
    Can print double-sided badges with personalized competitor schedules. Uses a json config file to specify
    everything. See the README.md file for full documentation.""")

def load_config(config_file):
    with open(config_file, "r") as fin:
        try:
            cfg = json.loads(fin.read())
        except ValueError: # includes JSONDecoderError
            print("Error loading config file. Make sure config file is a valid JSON file.")
            exit()
    if "custom_events" in cfg.keys():
        for _e in cfg["custom_events"]:
            eventNames[_e[0]] = tuple(_e[1:])
    return cfg

# helper for load_data() that sanity-checks an assignment string to make sure that
# the assignment doesn't have multiple roles for the same group (e.g. C1;R1)
def validate_assignment(who, event, assn):
    used = []
    for chunk in assn.split(";"):
        group = chunk[-1] # last character should be the group number
        if group in used:
            print(f"Warning: {who} has simultaneous assignments for {eventNames[event]}: {assn}")
        else:
            used.append(group)
    return

# to-do: as a robustness feature, we should check all the keys for each person in assignments,
# and for the keys that are events, uppercase the value. That way people don't have to capitalize
# the CJRS roles in their spreadsheet, which would be good, because other parts of the code
# expect capitals for those things.
def load_data(config):
    raw_data = []
    with open(config["assignments"], "r") as fin:
        reader = csv.reader(fin)
        for row in reader:
            raw_data.append(row)
    assignments = {}
    header = raw_data[0]

    # make a per-person dictionary of assignments 
    for i in range(1,len(raw_data)):
        who = raw_data[i][0] # the person's name
        _ = {"Number": str(i)} # temporary dict for the person's data. "Number" is their competitor number
        for j in range(1,len(header)): # here we need to associate the columns with event information from the header row, not the events list from the config file, because the order could be different.
            _[header[j]] = raw_data[i][j] # store the assignment
            validate_assignment(who, header[j], _[header[j]]) # print a warning if the assignment is not good. We'll still use it, but warn the user.
        assignments[who] = _
    return assignments

# generates output PDF filenames. compname is the name of the competition, while content is
# whatever material will be in this PDF file
def get_filename(compname, content):
    c1 = compname.split(" ") # split everything into individual words
    c2 = content.split(" ")
    return "_".join(c1+c2)+".pdf" # join the with _ and put .pdf on the end.

# helper that returns the competing group sub-portion of an assignment string
def group_of(assn):
    try:
        g = re.search("C\d", assn)[0]
    except: # we shouldn't ever hit this exception because we're only calling group_of from places where assn should already be a competitor's assignments, but you never know.
        g = f"Error: no group present in assignment string '{assn}'"
    return g

# Build lists of everybody competing in the event, what they're doing, and the
# set of competing groups in that event (which comes from the assignments file)
# This is a helper used by round robin and single-staging. 
def get_people_groups(assignments, event, return_groups=True):
    people = []        # competitors in this event
    role_strings = []  # roles they have
    for who in assignments.keys():
        roles = assignments[who][event]
        if "C" in roles:
            people.append(who)
            role_strings.append(roles)
    # Given a set of role strings, boil them down to a dict where the keys are the group
    # substrings (E.g. "C1", "C2", "C3") and the values are how many people were assigned to
    # that group
    groups = defaultdict(lambda: 0)
    for s in role_strings:
        groups[group_of(s)] += 1
    if return_groups:
        return (people, groups)
    else:
        return people

# helper that inserts a stage tag into an assignments string.
def assign_one_stage(assn, tag):
    chunks = assn.split(";") # break the assignment into chunks so we can find the C chunk and rewrite it easily.
    for i in range(len(chunks)):
        if chunks[i][0] == "C":
            chunks[i] = "C" + tag + chunks[i][1] # rewrite it to insert the stage tag
    return ";".join(chunks) # put the chunks back together and return the result.


# This routine handles the case where group sizes are small and all groups can be assigned
# to individual stages in such a way that stages aren't wasted.
# This is a greedy allocation algorithm that iterates over the stages in descending order of size,
# assigning to each the largest available group that will fit, detecting failure and end conditions along the way
def single_staging(config, groups, event):
    stages = [config["stages"][_] for _ in config["stages"]] # Get the list of stage [tag,size] arrays
    stages.sort(reverse=True, key=lambda x: x[1]) # descending sort by the size
    
    (people, groups) = get_people_groups(assignments, event)
    group_stages = {}     # this dict will map competing groups onto whichever stage they fit on.
    done = False
    while not done:
        failed = False
        for s in stages:
            cap = s[1]      # Get the size of the stage
            # Find the biggest group that can fit on this stage:
            best_size = -1  # sentinal 'no group' values
            best_group = None
            for g in groups: # this gets us a key that is a "C1" type string
                if groups[g] > best_size and groups[g] <= cap: # If this group fits on s but is bigger than the previous best
                    best_size = groups[g] # then record the size
                    best_group = g        # and the key
            # If we found one, then map it to that stage and take it out of the list of groups
            if best_group is not None:
                group_stages[best_group] = s[0] # Map the group to a stage tag
                del groups[g] # take this group out of the list of groups to be assigned
                if len(groups) == 0: # and if that was the last group, then we're done
                    done = True
                    break
            # but if we failed to find one, then abort
            else:
                failed = done = True
                break
    if failed:
        return False # this will trigger round_robin_staging as a fallback.
    else: # we succeeded, so do the actual group assignments as per group_stages
        for who in people:
            assn = assignments[who][event] # convenience variable
            assignments[who][event] = assign_one_stage(assn, group_stages[group_of(assn)])
        return True # this will tell assigned_stages that we succeeded

# Assign stages for a given event according to what the config file dictated
def assigned_staging(config, assignments, event):
    stage = config["events"][event][4] # this is guaranteed to exist because assign_stages had to check for it in order to know to call this mode
    stage_tag = config["stages"][stage][0] # get the stage tag
    people = get_people_groups(assignments, event, return_groups=False)
    for who in people:
        assignments[who][event] = assign_one_stage(assignments[who][event], stage_tag)

# Deals competitors in each competing group onto each stage in round-robin fashion.
def round_robin_staging(config, assignments, event, stage_tags, num_stages):
    # get lists of everybody competing in the event, what they're doing, and what groups there are
    (people, groups) = get_people_groups(assignments, event)
    for g in groups:            # for this group
        stage = 0                   # initialize the stage index
        for who in people:          # loop over all the people
            if g in assignments[who][event]:  # and find the ones in this group
                assignments[who][event] = assign_one_stage(assignments[who][event], stage_tags[stage])
                stage = (stage + 1) % num_stages   # increment the stage index for next time

# This assigns competing stages to all competitors for round 1 of all events. It determines
# which stage assignment mode to use, then calls a helper to do that mode of assignment.
def assign_stages(config,assignments):
    # First, build a list of the stage short-identifiers. We'll need it later.
    stage_tags = [ config["stages"][_][0] for _ in config["stages"].keys() ]
    num_stages = len(stage_tags)
    # Next, loop over all the events in the comp
    for event in config["events"].keys():
        # If the config file specified a valid stage, then do assigned staging.
        if len(config["events"][event]) == 5 and config["events"][event][4] in config["stages"]:
            assigned_staging(config, assignments, event)
        # else try single-staging, but if it fails, default to round-robin.
        else:
            if single_staging(config, assignments, event) is False:
                round_robin_staging(config, assignments, event, stage_tags, num_stages)


# Draws one subdivided box for a "row" on a scorecard. Includes solve rows,
# header rows, etc. Draws the box at the origin; caller must translate first.
def drawScorecardRow(c, cw, hu, vu, h, linePositions=None, labels=None, isStar=False, fs=12):
    c.rect(0,0,cw,h*vu,stroke=1,fill=0) # The outer box of the row
    if linePositions is not None:
        for x in linePositions:
            c.line(x*hu,0,x*hu,h*vu)
    if labels is not None: # put labels where desired
        fudge = fs/6.0
        for l in labels:
            c.drawCentredString(l[0]*hu,fudge+(h*vu-fs)/2.0,l[1])
    if isStar and linePositions is not None:
        centerX = (linePositions[0]+linePositions[1])*hu / 2.0 # middle of the scrambler signature space.
        centerY = (h/2.0)*vu
        p = c.beginPath()
        # generate the points of the star
        for i in range(0, 10):
            theta = i*(36/57.2957798) - (18/57.2957798) # every 10 degrees, offset so the star is right-side up.
            r = 0.17*h*vu * (1 + i%2) # toggle between inner and outer radius
            x = centerX + r*math.cos(theta)
            y = centerY + r*math.sin(theta)
            if i == 0:
                p.moveTo(x,y)
            else:
                p.lineTo(x,y)
        p.close()
        # draw and fill the path and reset the color back to back
        c.setFillColorRGB(1.0,1.0,0.2) # opaque Yellow
        c.setStrokeColorRGB(0,0,0)
        c.drawPath(p, fill=1)
        c.setFillColorRGB(0,0,0) # opaque black

def draw_one_scorecard(c, comp, who, wcaid, number, event, round, group, stage, solves, attempts, cutoff, limit):
    global config, w, h, w2, h2, m
    border = 0.375*72
    c.saveState()
    c.translate(border,border)

    cw = w2-2*border # card width; width of usable horizontal part of the card
    ch = h2-2*border # card height
    hu = cw / 14 # define 14 units across the width
    vu = ch / 19 # define 19 units down the height
    vr = vu * 0.8334 # vertical row (vr) height is 5/6ths of a unit. This is a hack to squeeze in an E2 row into the earlier design.

    c.setFont("Helvetica", 12)  # font for the solve numbers
    linePositions = [1,2.5,11,12.5] # grid positions for the vertical lines

    # figure out if this competitor needs a star on their scorecards.
    isStar = ("stars" in config) and ((who in config["stars"] and event in config["stars"][who]) or (wcaid in config["stars"] and event in config["stars"][wcaid]))

    # The idea here is that each row consists of a call to drawScorecardRow
    # follows by a vertical translate to account for that row's height. Each
    # thing is responsible for "consuming" its own height out of the State
    # by translating upward an appropriate amount. We're drawing the scorecard
    # from the bottom up.

    # draw the extras rows
    drawScorecardRow(c, cw, hu, vr, 2, linePositions, [(0.5,"E2")], isStar, 12)    
    c.translate(0,2*vr)
    drawScorecardRow(c, cw, hu, vr, 2, linePositions, [(0.5,"E1")], isStar, 12)    
    c.translate(0,2*vr)
    # and its label
    c.drawCentredString(cw/2,0.5*vu-4,"---- Extra or Provisional Solves ----")
    c.translate(0,vu)

    # draw the 5 solve lines, from the bottom up
    for s in range(5,0,-1):
        if s <= solves: # skip rows for short events.
            drawScorecardRow(c, cw, hu, vu, 2, linePositions, [(0.5,str(s))], isStar, 12)    
        c.translate(0,2*vu)
        if attempts is not None and s == attempts+1: # if this event has a cutoff, display it
            c.setFont("Helvetica",8)
            c.drawCentredString(cw/2, 2, f"{attempts} attempt{'s' if attempts > 1 else ''} to get ≤ {cutoff}")
            c.translate(0,0.5*vu)
            c.setFont("Helvetica",12)

    # draw the header row above the solves
    drawScorecardRow(c, cw, hu, vu, 1, linePositions, [
        (1.75,"S"),(6.75,f"Result (DNF if ≥ {limit})"),(11.75,"J"),(13.25,"C")
    ], False, 12)    
    c.translate(0,1.2*vu)

    # Draw the competitor row
    drawScorecardRow(c, cw, hu, vu*0.8, 1, [4.5], [(2.25,wcaid),(8.25,who),(13,number)], False, 12)
    c.translate(0,vu)

    # skip up a little bit and draw the round, group, and stage
    if stage == "":
        c.drawCentredString(cw/2,0.5*vu-6,f"Round {round} | Group {group}")
    else:
        c.drawCentredString(cw/2,0.5*vu-6,f"Round: {round} | Group: {group} | Stage: {stage}")
    c.translate(0,0.8*vu)

    # draw the event
    c.setFont("Helvetica-Bold",16)
    c.drawCentredString(cw/2, .75*vu-8, eventNames[event][0]) # uses the friendly-name of the event
    c.translate(0,1.25*vu)

    # and finish off with the competition name
    c.setFont("Helvetica",12)
    c.drawCentredString(cw/2,0.5*vu-6,comp)
    c.restoreState()

# Maps a stage's shorthand form, like "R" or "B", back to its full name, like "Red" or "Blue"
def get_stage_name(shorthand):
    _ret = f"Error: stage name not found for shorthand {shorthand}"
    for stage_name in config["stages"].keys():
        if config["stages"][stage_name][0] == shorthand:
            _ret = stage_name
    return _ret

# generates the round 1 scorecards, with names
def generate_scorecards(config, assignments):
    global w, h, w2, h2, m
    c = canvas.Canvas(get_filename(config["competition"],"scorecards"), pagesize=letter)
    quadrants = [
        [0,  h2],
        [w2, h2],
        [0,   0],
        [w2,  0] ]
    # iterate over events in this comp
    for event in config["events"].keys():  # this will be an event id, like "333"
        card_count = 0        
        solves, attempts, cutoff, limit = config["events"][event][0:4] # the slice at the end skips a stage assignment, if present
        # iterate over everybody
        for who in sorted(assignments.keys()):
            # See if this person is competing in this event
            if "C" in assignments[who][event]:
                wcaid = assignments[who]["WCA ID"]
                number = assignments[who]["Number"]
                junk = assignments[who][event]
                if "stages" in config.keys(): # whether we do or don't have stages affects how to parse out the group number
                    group = junk[junk.index("C")+2]
                    stage = get_stage_name(junk[junk.index("C")+1]) # map the stage's shorthand string back to its full name
                else:
                    group = junk[junk.index("C")+1]
                    stage = ""
                c.saveState()
                # Determine which page quadrant to go in -- TO DO: generalize to a configurable number of scorecards per page. Right now is hard coded for 4
                q = card_count % 4
                # translate to the origin for this scorecard
                c.translate(quadrants[q][0], quadrants[q][1])
                # draw the card:
                draw_one_scorecard(c, config["competition"], who, wcaid, number, event, 1, group, stage, solves, attempts, cutoff, limit)
                c.restoreState()
                if q == 3: # that was the last card on the page
                    if config["cut_guides"] is True:
                        c.line(w2,0,w2,h)
                        c.line(0,h2,w,h2)
                    c.showPage()
                card_count += 1
        if (card_count % 4) != 0: # if we didn't just finish a page
            if config["cut_guides"] is True: # very not-DRY, I know...
                c.line(w2,0,w2,h)
                c.line(0,h2,w,h2)
            c.showPage()
    c.save()
    print(f"Saving scorecards to: {get_filename(config['competition'],'scorecards')}")

# This is kind of a poorly named routine, since it does cards for second..final rounds and completely blank cards by means of a "blank" event hack.
# Here, interpret "blank" to mean "missing the competitor name, event name, or both"
def generate_blank_scorecards(config):
    global w, h, w2, h2, m
    c = canvas.Canvas(get_filename(config["competition"],"scorecard blanks"), pagesize=letter)
    quadrants = [
        [0,  h2],
        [w2, h2],
        [0,   0],
        [w2,  0] ]
    amounts = config["scorecard_blanks"]
    for event in sorted(amounts.keys()): # for each event that we want blanks for
        if event == "blank":
            solves, attempts, cutoff, limit = config["events"]["333"][0:4] # blank scorecards get the same settings as 3x3. This is a reasonable default.
        else:
            solves, attempts, cutoff, limit = config["events"][event][0:4]
        for round in amounts[event]:     # and for each round in that event that we want blanks for
            num = amounts[event][round]  # Get the number of blanks requested in the config file
            for i in range(num):         # and loop over that many blanks. This is very non-DRY with the logic in generate_scorecards
                c.saveState()
                q = i % 4
                c.translate(quadrants[q][0], quadrants[q][1])
                draw_one_scorecard(c, config["competition"], "", "", "", event, round, "__", "", solves, attempts, cutoff, limit)
                c.restoreState()
                if q == 3: # that was the last card on the page
                    if config["cut_guides"] is True:
                        c.line(w2,0,w2,h)
                        c.line(0,h2,w,h2)
                    c.showPage()
            if (num % 4) != 0: # weirdo user asked for a partial page at the end
                c.showPage()
    c.save()
    print(f"Saving blank scorecards to: {get_filename(config['competition'],'scorecard blanks')}")

# Returns True if the person is competing in any events.
def isCompetitor(who):
    ret = False
    assn = assignments[who]
    for event in assn.keys(): # scan through their assignments looking for any "C" assignment
        if "C" in assn[event]:
            ret = True
    return ret

# Draw a single badge front
def drawBadgeFront(c, who, wcaid):
    cfg = config["badge_config"] # convenience variable
    c.drawImage(cfg["template_image"], 0,0, 72*2.5, 72*3.5)
    nameX = cfg["name_conf"][0]
    nameY = cfg["name_conf"][1]
    nameSize = cfg["name_conf"][2]
    idX = cfg["id_conf"][0]
    idY = cfg["id_conf"][1]
    idSize = cfg["id_conf"][2]
    c.setFont("Helvetica-Bold",nameSize)
    c.drawCentredString(nameX, nameY, who)
    c.setFont("Helvetica-Bold",idSize)
    c.drawCentredString(idX, idY, wcaid)
    if not isCompetitor(who): # a "helper" is a person who is not competing in any events, but does have assignments
        helperX = cfg["helper_conf"][0]
        helperY = cfg["helper_conf"][1]
        helperSize = cfg["helper_conf"][2]
        c.setFont("Helvetica-Bold",helperSize)
        c.drawCentredString(helperX, helperY, "Helper")

# parse an assignment string into a dict of roles/groups
def parseRoles(roles):
    ret = {"C":"","H":""}
    if len(roles) == 0:
        return ret
    _l = roles.split(";")
    for elem in _l:
        if elem[0] == "C":
            ret["C"] = elem[1:] # strip off the "C" in the front, as it is redundant here
        else:
            ret["H"] = ret["H"] + elem + " "
    return ret

# Draw a single badge back
def drawBadgeBack(c, config, who, assignments):
    hu = vu = 0.25*72 # going with a straight quarter inch grid, 10x14 units
    c.rect(0,0,10*hu,14*vu,stroke=1,fill=0)

    # Draw competitor number and competition name across the top, small
    c.setFont("Helvetica", 8)
    c.drawCentredString(0.5*hu, 13.5*vu, assignments[who]["Number"])
    c.drawCentredString(5*hu, 13.5*vu, config["competition"])

    # Draw competitor's name, big
    c.setFont("Helvetica-Bold",16)
    c.drawCentredString(5*hu, 12.5*vu, who)

    # Draw the assignments grid. This has to happen before drawing the header row so the white header row text doesn't get clipped by the boxes around these scorecardRow() calls.
    # Available vertical space = 2 through 11.5, ~9.5 units
    c.saveState()
    numEvents = len(config["events"])
    rowHeight = 9.5/numEvents
    c.translate(0, (11.5-rowHeight)*vu)
    for event in config["events"]:
        roles = parseRoles(assignments[who][event]) # split the roles string into a dictionary of C and H column info.
        drawScorecardRow(c, 10*hu, hu, vu, rowHeight, [3,6.5], [(1.5,eventNames[event][1]), (4.75,roles["C"]),(8.25,roles["H"].strip())]) # this uses the short-name of the event
        c.translate(0,-rowHeight*vu)
    c.restoreState()

    # Draw table header row
    c.setFillColorRGB(0,0,0) # opaque black
    c.rect(0,11.5*vu,10*hu,0.5*vu,stroke=1,fill=1)

    c.setFont("Helvetica-Bold", 8)
    c.setFillColorRGB(1,1,1) # opaque white
    c.drawCentredString( 1.5*hu, 11.5*vu+2, "Event")
    if "stages" in config.keys():
        c.drawCentredString(4.75*hu, 11.5*vu+2, "Stage & Group")
    else:
        c.drawCentredString(4.75*hu, 11.5*vu+2, "Group")
    c.drawCentredString(8.25*hu, 11.5*vu+2, "Helping")
    c.setFillColorRGB(0,0,0) # return fill back to normal black
 
    # Draw key at the bottom
    c.setFont("Helvetica",12)
    if "stages" in config.keys():
        stage_key =  "/".join([config["stages"][_][0] for _ in config["stages"].keys()])
        stage_key = stage_key + ": "
        stage_key = stage_key + "/".join(config["stages"].keys())
        c.drawString(0.5*hu, 1.25*vu, stage_key)
    else:
        c.drawString(0.5*hu, 1.25*vu, "C: Competing")
    c.drawString(0.5*hu, 0.25*vu, "J: Judging")
    c.drawString(5.5*hu, 1.25*vu, "R: Running")
    c.drawString(5.5*hu, 0.25*vu, "S: Scrambling")

# Handles the looping over a batch of 9 people, with the translation junk and the showPage() calls
def badge_page_loop(c, config, name_list, assignments, side, idx_start, idx_end):
    x0, x1, x2 = [36, 36+(2.5*72),36+(5*72)]  # set up the grid locations so they can be indexed easily
    y0, y1, y2 = [18, 18+(3.5*72),18+(7*72)]
    if side == "front":                       # front side are laid out left-to-right in rows
        origins = [
            [x0,y2],[x1,y2],[x2,y2],
            [x0,y1],[x1,y1],[x2,y1],
            [x0,y0],[x1,y0],[x2,y0]
        ]
    elif side == "back":                      # back side are laid out right-to-left in rows
        origins = [                           # this is so double-sided printing keeps the
            [x2,y2],[x1,y2],[x0,y2],          # correct back with its matching front.
            [x2,y1],[x1,y1],[x0,y1],
            [x2,y0],[x1,y0],[x0,y0]
        ]
    else:
        print("Error: 'side' parameter must be 'front' or 'back'.")
        exit()

    for i in range(idx_start, idx_end):
        who = name_list[i]
        c.saveState()
        c.translate(origins[i-idx_start][0], origins[i-idx_start][1])
        if side == "front":
            drawBadgeFront(c, who, assignments[who]["WCA ID"])  
        if side == "back":
            drawBadgeBack(c, config, who, assignments)
        c.restoreState()

def generate_badges(config,assignments):
    c = canvas.Canvas(get_filename(config["competition"], "badges"), pagesize=letter)
    name_list = list(assignments.keys()) # make a list of names so they have indexes.
    # Iterate over all the assignments in groups of 9
    for idx_start in range(0,len(name_list),9):
        idx_end = min(idx_start + 9, len(name_list))
        badge_page_loop(c, config, name_list, assignments, "front", idx_start, idx_end)
        c.showPage()
        badge_page_loop(c, config, name_list, assignments,  "back", idx_start, idx_end)
        c.showPage()
    # save the PDF file
    c.save()
    print(f"Saving badges to: {get_filename(config['competition'],'badges')}")

if __name__ == '__main__':
    # set up arg parser and parse args
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument("--config", "-c", required=True, help="JSON file of config information")
#    parser.add_argument("--winners", "-w", required=False, default=None, help="JSON file of winner information")
    parser.add_argument("--generate", "-g", required=False, default="all", help="a string specifying what you want generated: any combination of 'scorecards', 'blank', 'badges', or 'all'")
    parser.add_argument("--help", "-h", action="store_true")

    args = parser.parse_args()
    if args.help is True:
        show_help()
        exit()
    if args.config is None:
        show_help()
        print("\nError: missing config file. Use '--config' option to specify one.")
        exit()
    config = load_config(args.config)
    assignments = load_data(config)
    # check whether we need to assign competing stages to each person
    if "stages" in config.keys():
        if len(config["stages"].keys()) > 0:
            assign_stages(config, assignments)

    make_list = args.generate
    if "all" in make_list or "scorecard" in make_list:
        generate_scorecards(config, assignments)
    if "all" in make_list or "blank" in make_list:
        generate_blank_scorecards(config)
    if "all" in make_list or "badge" in make_list:
        generate_badges(config, assignments)
 
    # TO DO: support generating winner certificates. If the -w flag is specified, then
    # load_config() of that config to get the winner information,
    # and call a generate_certificates() function instead of any of the other stuff.
