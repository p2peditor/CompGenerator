# CompGenerator

CompGenerator is a python script that generates competitor badges and scorecards for use in speedcubing competitions. It is for comp organizers who are comfortable working with text files and a unix-style command line environment.

You give CompGenerator information about your competition, and it gives you PDF files of your competitor badges and scorecards. Print them and run them through a paper cutter, and you're done.

Competitor badges are printed 9 to a sheet, two-sided, sized to fit 2.25x3.5 inch badge holder sleeves such as [these](https://www.amazon.com/dp/B083BHCTVZ). The front side shows your competition's logo, competition name, and competitor name. The back side shows the competitor's individual round-1 schedule and helping group assignments.

Scorecards are printed 4 to a sheet of standard US letter paper. CompGenerator will generate all your round-1 scorecards based on the competitor information you supply. It can print scorecards for subsequent rounds and finals too, but will leave the names blank. You write those in by hand once you know who made it into round 2, etc. CompGenerator can also make extra scorecards with blanks for the competitor name and/or event, because you never know when you might need to write up a scorecard during the competition.

CompGenerator offers many options for how scorecards and badges are generated and convenience features to make your job easier and to improve the overall competition experience. See [docs/overview.md](docs/overview.md) for a complete list of CompGenerator's capabilities.

For examples of what CompGenerator can do, see the input files and corresponding PDF output files in the [samples/](samples/) directory.
