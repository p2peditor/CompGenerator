# Overview

CompGenerator is a python script that generates competitor badges and scorecards for use in speedcubing competitions. It is for comp organizers who are comfortable working with text files and a unix-style command line environment.

You give CompGenerator information about your competition, and it gives you PDF files of your competitor badges and scorecards. Print them and run them through a paper cutter, and you're done.

Competitor badges are printed 9 to a sheet, two-sided, sized to fit 2.25x3.5 inch badge holder sleeves such as [these](https://www.amazon.com/dp/B083BHCTVZ). The front side shows your competition's logo, competition name, and competitor name. The back side shows the competitor's individual round-1 schedule and helping group assignments.

Scorecards are printed 4 to a sheet of standard US letter paper. CompGenerator will generate all your round-1 scorecards based on the competitor information you supply. It can print scorecards for subsequent rounds and finals too, but will leave the names blank. You write those in by hand once you know who made it into round 2, etc. CompGenerator can also make extra scorecards with blanks for the competitor name and/or event, because you never know when you might need to write up a scorecard during the competition.


# 1. Events and Custom Events

Out of the box, CompGenerator recognizes and supports all the official WCA events. These are referenced in your config file and your competitor assignments file by the official WCA designators for those events. For example, `333` for 3x3 and `333mbf` for 3x3 multi-blind.

CompGenerator can also support custom, unofficial, and "exhibition" events with the same functionality as official events. All it needs is to be told the designator, full name, and short name for the event. See the [Config File Reference](config_file_reference.md) for details on custom events.

# 2. CompGenerator Features

# 2.1 Scorecards

CompGenerator will automatically use the information you provide about your events and custom events--what format the event is using, cutoff and limit times, and any stage information--to configure the scorecards appropriately.

Round 1 scorecards will include:
* The competition name
* The event
* The competitor's name, competing group, and assigned stage
* Lines to write in the solve attempt results
* Cutoff and time limit information
* E1 and E2 lines for extra attempts
* "Star" markers for high profile competitors (see below)

# 2.2 Competitor Badges

CompGenerator produces two-sided badges, where the front side shows whatever artwork or other badge design you provide, and the back side shows the competitor's schedule.

The front side will include:
* The competition name
* The competitor's name
* The competitor's WCA ID (if available)

The back side will include:
* The person's competitor number (either assigned automatically or drawn from your assignmetns file)
* The competition name
* The competitor's name
* a table of events showing the person's competitng and helping assignments for each event
* A key that gives the stage indicators (if you have stages), and the explanation of what the C/J/R/S indicators mean.

# 2.3 Helper Badges

CompGenerator supports producing badges for people who are not competing but have volunteered to do helper roles. Just add these people to your competitor assignments file and assign roles to them for each event, just as you would for anybody else, only without any `C` competitor assignments. CompGenerator will automatically detect people with no competitor assignments, and will include a "Helper" notation on their badge.

The back side for helper badges is the same as for competitors, except there will be no competing assignments.

# 3. Staging

Staging refers to the practice of dividing the solving stations at a competition into groups called "stages". This is at the organizer's discretion. Typically, stages are given colors such as "red" or "blue", and the physical solving stations have colored tablecloths to match. For competitions in larger physical spaces, dividing the solving stations into stages can greatly improve the logistics of running each round.

CompGenerator does not force you to use stages. If your config file provides stage information, then CompGenerator will use that information to distribute competitors in each competing group to the stages in one of three different methods: Round-Robin, Assigned, or Single Staging.

## 3.1 Round-Robin Staging

The default method is "round robin", where the competitors in a competing group are distributed evenly among the available stages. Think of it like dealing cards: the competitors are the cards, and they get "dealt" out in round-robin fashion to each stage. This ensures that the stages are as evenly filled as possible, so each stage should complete the competing group at about the same time.

For example, if you have 50 people competing in 3x3 group 1, and you have three stages called "Red", "Blue", and "Green", CompGenerator will assign 17 people to Red, 17 to Blue, and 16 to Green.

CompGenerator will use this method in most situations, because typically the number of competitors in a group is greater than the total number of solving stations at the competition.

## 3.2 Assigned Staging

Assigned staging does not put specific competitors on specific stages, but puts events on the stages you dictate. If you want a particular event to take place on a single, specific stage, you can specify the stage for that event in your config file. See the documentation above for the `events` key of the config file. All competitors, regardless of what competing group they are in or how many people are competing, will be assigned to the stage you specify in the config file. Events that are not assigned to a specific stage will be assigned using Round Robin or Single Staging, as appropriate.

## 3.3 Single Staging

If a particular event has a small number of people competing, then each competing group might fit on a single stage. That is, there might be a way to assign the groups to the stages such that the number of people in the group is no larger than the number of solving stations on the stage. This can provide two efficiency benefits in running the competition: One, it allows you to use fixed seating so competitors do not have to move back and forth between the competitor waiting area and the solving stations. Two, it allows competing groups to run in parallel on multiple stages instead of one group having to finish before the next group starts.

For example, Suppose you have two stages, Red and Blue, with 6 solving stations each. Suppose you have 22 people competing in 7x7. If you define four competing groups, (C1, C2, C3, and C4) in your assignments file with 6, 6, 5, and 5 competitors each, then you see how C1 and C2 could run in parallel on the Red and Blue stages with fixed seating, and likewise C3 and C4.

CompGenerator will automatically detect this type of situation and use single staging where possible.

Presently, it is not possible to disable single staging so as to force CompGenerator to use round robin. Assigned staging, however, will always override single staging.

# 4. General Suggestions

## 4.1 Roles Assignments
Part of a comp organizer's job is to create a good competition experience for competitors. Carelessly assigning roles can make for a poor experience. It will not always be possible to assign roles such that everyone has a great experience, but here are some good practices to follow:

* Avoid assigning someone a helping role for the group immediately before their competing group. If you do, then you won't give that person any time to warm up for their group, and asks them to compete when they might still be hot and sweaty or out of breath from running.
* Avoid over-assigning the same person to many jobs in many events. If you do, then they will have less time to socialize with their cubing friends, which will make the competition less enjoyable for them overall.
* Assign some helping roles to each competitor. Competitors need to understand that helping the competition run smoothly is part of their job as a participant in the comp.
* Avoid assigning first-time competitors to any helper roles besides judging. New people should go to at least a few competitions to get the feel for how a round should be run before being asked to serve as a runner or scrambler.

# 4.2 Selecting Scramblers and Runners

A good competition depends very heavily on the behavior and performance of the people scrambling the puzzles and running puzzles to and from the scrambling station. Competition organizers should assign these roles with some care.

Review your list of registered competitors, looking for people who you know to be competent, mature enough, and physically capable of performing the roles.

A good scrambler is someone who is a high-level competitor in their event (i.e. regularly makes it to the final round), and who you know to have a responsible disposition. That is, you want someone you can trust to both scramble accurately, and to fix any mis-scrambles rather than just sending them out due to laziness.

A good runner is someone who understands the flow of a group, who understands competitors' needs to be clearly directed to scrambling stations, who can accurately read and pronounce the names of competitors as their turns come up, and who can speak loudly enough to be heard over the general background noise of a competition. Young children, though they are the future of cubing, generally do not have these capabilities. Rely on your older cubers, or at the very least people who have attended several competitions in the past.

# 4.3 Assigning Roles to Delegates

Delegates at the competition are important people. Not merely because they are delegates, but because they have the knowledge and authority to make judgments about any situations that occur during the competition.

While delegates often make very good scramblers and runners, if possible it is better not to assign them any helper roles during the competition. They are expected to help out anyway, but they need to be available to adjudicate any situations that arise (notably, decisions on whether to apply +2s and other penalties). You don't want your competition to fall behind schedule because the delegates were busy doing other things.

Delegates are virtually always also competitors in the event. This, plus the need for delegates to be available to handle situations that arise means that you should not put all your delegates in the same competing group of a given event. Spread them out so that at least one delegate is always free to manage the competition.