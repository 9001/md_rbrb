# multilanguage Rabi-Ribi display
* MIT-licensed, 2017/02/19, ed@irc.rizon.net
* https://ocv.me/stuff/md_rbrb.png -- screenshot
* https://ocv.me/stuff/md_rbrb.mp4 -- video
* https://pypi.org/project/md_rbrb/ -- download


# usage
* install `mecab.exe` with **UTF-8 dictionary charset**: http://taku910.github.io/mecab/#win
* open a terminal: `WIN+R` `cmd`
* install md_rbrb: `pip install md_rbrb`
* run md_rbrb: `md_rbrb` (or maybe `python -m md_rbrb`)
* visit http://127.0.0.1:8086/

if you are running md_rbrb from the source code directory, disregard all the above (except for the mecab part) and just run `start-md_rbrb.bat`


# how it works
* it attaches to rabiribi.exe and uses hardcoded memory addresses to read out the currently visible dialogue line from the process memory
* on each new line it parses the game's dialogue file from disk and reads out the japanese and english variant of said line
* an httpd offers a document which displays the current dialogue line and autorefreshes to load new lines


# maintainers
if there's a new version of rabi-ribi and this script has died, open up the following file for reference along with cheatengine: `C:\Program Files (x86)\Steam\steamapps\common\Rabi-Ribi\localize\event\story_en.rbrb`

* start a new game
* tap past the first two lines of dialogue (`...` and `...?`)
* stop at the 3rd line (`Yawn...`)
* CTRL-F the dialogue line in story_en.rbrb, you'll see its block ID right above the search result
* do a 4byte search for that ID (`10000`), you'll see a couple results
* skip 3 lines ahead until just after the cutscene, then stop at the 1st line (`Wh-What is this place?`)
* do another search for the new ID (`10001`), now there's only two search results
* add the 1st result to the code list by doubleclicking it, then rightclick it in the codelist and `Pointerscan for this address`, use default settings, hit OK and Yes (it'll only take like 44kB)
* the top result will have "**Offset 0**" = `0` and the other offsets are blank, you just found `ADR_BLOCK_ID` which is the hexadecimal value under "**Base Address**"
* without advancing the dialogue, start a new 4byte search for 0, then move one line ahead ingame and search for 1, then one more line and search for 2 etc until there's just one result with green text
* pointerscan that result and grab the first result with "**Offset 0**" = `0`, that is `ADR_BLOCK_POS`

note that if the dialogue box goes away for a camera pan or whatever then you have to start over since that makes it go back to 0, so do this with a dialogue scene that goes on for a bit uninterrupted


# changelog
* 2017/03/24: v1.1 for Rabi-Ribi v1.88
* 2017/02/19: v1.0 for Rabi-Ribi v1.75
