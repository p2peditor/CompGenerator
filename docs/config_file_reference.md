# Config File Reference

The config file tells CompGenerator everything it needs to know in order to make scorecards and badges for you. This includes:
* Information about your competition -- stages, events, cutoff times, etc.
* Where to find assignments for your competitors
* The template for your competitor badges and how you want them laid out.

This file is a [.JSON file](https://www.json.org/json-en.html), consisting of a dictionary with _key:value_ pairs that provide all of CompGenerator's settings. The settings are loosely grouped into:
* Information about your competition as a whole
* Information about your competitors
* Options for how badges and scorecards should be drawn
* Settings for round 2 and later scorecards.

See the `samples` directory for a config file example.

## 1 Competition Information

Competition information is given by three key:value pairs, called `"competition"`, `"stages"`, and `"events"`.

### 1.1 Competition Name
The `"competition"` key gives the name of your competition:

  `"competition": "Fargo Flyin' Fingers 2023"`

### 1.2 Stages at Your Venue
If the solving stations at your venue are separated into different stages, different rooms, or different areas for whatever reason, the `"stages"` key allows you to specify a dictionary that names each stage, gives a shorthand form for it, and how many solving stations the stage has. For example:

  `"stages": {"Red":["R", 6], "Blue":["B", 6]}`

This denotes that the competition is using two stages, called "Red" and "Blue", with shorthands "R" and "B", and 6 solving stations each. Within the event and group designations present in your competitor assignments file, CompGenerator will distribute the competitors as evenly as possible across the available stages.

You can direct CompGenerator to put events on specific stages if you like; see the documentation for the `events` key, below.

If your competition is not using multiple stages, you can omit the `"stages"` key entirely, or specify it as an empty dictionay (`{}`).

### 1.3 Events at Your Competition
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

### 1.4 Custom Events and Non-English Event Names
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

Note that the designators of events in your `"events"` key, the column headers in your competitor assignments file (see below), and the designators in your `"custom_events"` (if any), must all match.

## 2 Competitor Information

All information relating to your competitors is given by two keys, `"assignments"` and `"stars"`.

### 2.1 Competitor Assignments File
All information about each competitor's competition schedule and helping roles is stored in a separate file called the competitor assignments file, given by the `"assignments"` key. This key gives the name of a comma-separated-values (.csv) file that tells CompGenerator what you want everyone to be doing during round 1 of each event. For example:

  `"assignments": "fargo_flyin_fingers_2023_competitors.csv"`

See the [Assignments File Reference](assignments_file_reference.md) for full documentation on how to work with your competitor assignments file.

### 2.2 Marking Top-Ranked Competitors
The "stars" key gives a dictionary that maps competitor names to which events they might could set a record in (i.e. events in which they are "stars"). Scorecards for these people will be marked with a gold star in the scrambler signature area, as a reminder to scramblers to make extra-sure that the scrambles are correct. For example:

```
  "stars": {
    "Ada Ke":["333"],
    "Alan Ke":["555"],
    "Ash Black":["333","777"],
    "Braden Dillenberg":["FTO"]
  }
```

This would cause those competitors to have stars on their round-1 scorecards for the indicated events. You can omit this key or leave it empty if there are no high-level competitors at your competition, or do not wish to use this feature.

This feature is useful if you have high-level competitors at your competition who might potentially set records, and want to avoid drama or controversy over misscrambles (see https://www.youtube.com/watch?v=NFMUs_lUHpM for a summary of recent related incidents) that could invalidate a record. Scramblers should never misscramble or let an incorrect scramble go out to a competitor, but people get sloppy or carless. Marking the high-level scorecards in an obvious way helps remind scrambles to do their jobs right for the cases where it matters most.


## 3 Drawing Options for Badges

CompGenerator supports several options for configuring how it renders badges and scorecards.

### 3.1 Competitor Namebadge Information
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

## 4 General Drawing Options

The `"cut_guides"` key indicates whether CompGenerator should add thin lines to the scorecard and ID badge should be set to either `true` or `false`. The default is `false`, no lines. If you will be using a paper cutter, you likely don't need guides, though if you will be using scissors then they will be helpful.

  `"cut_guides": false`

## 5 Blank Scorecards for Round 2 and Later

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
