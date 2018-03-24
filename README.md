# multilanguage Rabi-Ribi display
* MIT-licensed, 2017/02/19, ed@irc.rizon.net
* https://ocv.me/stuff/md_rbrb.png
* https://ocv.me/stuff/md_rbrb.mp4


# usage
* install `mecab.exe`: http://taku910.github.io/mecab/#win
* open a terminal: WIN+R cmd
* install md_rbrb: `pip install md_rbrb`
* run md_rbrb: `md_rbrb` (or maybe `python -m md_rbrb`)
* visit http://127.0.0.1:8086/the.html

if you are running md_rbrb from the source code directory, disregard all the above (except for the mecab part) and just run `start-md_rbrb.bat`

# how it works
* it attaches to rabiribi.exe and uses hardcoded memory addresses to read out the currently visible dialogue line from the process memory
* on each new line it parses the game's dialogue file from disk and reads out the japanese and english variant of said line
* an httpd offers a document which displays the current dialogue line and autorefreshes to load new lines


# maintainers
if there's a new version of rabi-ribi and this script has died, open up the following file for reference along with cheatengine: `C:\Program Files (x86)\Steam\steamapps\common\Rabi-Ribi\localize\event\story_en.rbrb`

* enter a new dialogue scene ingame (do not advance past first line)
* CTRL-F the dialogue line in story_en.rbrb, you'll see its block ID right above the search result
* do a 4byte search for that ID, you should get 2 results (either is fine)
* if more than 1 result then progress through that dialogue scene until you enter a new one, then do another search for the new block ID, repeat until just 2 results
* do a pointerscan on one of the hits, grab the lowest result with 0 offset, **this is ADR_BLOCK_ID**
* still without advancing the dialogue do another 4byte search for 0, then move one line ahead ingame and search for 1, then one more line and search for 2 etc until there's just one result, pointerscan that and grab the lowest result with 0 offset, **this is ADR_BLOCK_POS**

note that if the dialogue box goes away for a camera pan or whatever then you have to start over since that makes it go back to 0, so do this with a dialogue scene that goes on for a bit uninterrupted


# changelog

* 2017/02/19: v1.0 for Rabi-Ribi v1.75
