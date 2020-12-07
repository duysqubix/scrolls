# Contributing to the Unofficial Elder Scrolls Mud

UESM utilizes GitHub's issue tracking for both issues/bug as well as newly implemented features.

To see a list of planned features head over to the [issues](https://github.com/duysqubix/scrolls/issues), folks are more than welcome to create
new unplanned feature requests.

## Ways to Contribute


### Documentation

Help with documenting the code is greatly appreciated. To be honest, at this point I have dedicated my time to functionality
of code and severly neglected documentation. That is something I will continously be working on, but any amount of contribution in this
arena is welcomed; small typos to new documentation is appreciated. At UESM, we follow the same documenting [guidelines](https://github.com/evennia/evennia/blob/master/CODING_STYLE.md#doc-strings) as followed in Evennia.


### Forking Repo

There are loads of planned [features](https://github.com/duysqubix/scrolls/issues) still needing to be done. The most elegant way to contribute code to create a fork of this repository and make your changes to that.

Once you have a fork set up, you can not only work on your own game in a separate branch, you can also commit your fixes to UESM itself. Make separate branches for all UESM additions you do - don't edit your local master or develop branches directly. It will make your life a lot easier. If you have a change that you think is suitable for the main UESM repository, you issue a Pull Request. This will let UESM devs know you have stuff to share. Bug fixes and features should generally be done against the dev branch of Evennia. Upon approval and a successful code review, it will be merged with master.


### Clean Install
The base of Scrolls uses evennia development as the main upstream (this will change once evennia 1.0 comes out then all code will be merged with master) 
for the time being , pull against both evennia development and scrolls development.

The following steps outline how to get a working copy of the Scrolls running on your machine.

1. Install evennia (as outlined [here](https://github.com/evennia/evennia/wiki/Getting-Started))
2. `cd evennia; git checkout development; pip install -e .`
3. `cd scrolls; evennia start`
4. Log into the game and run the following commands
5. `@py self.attrs.level.value = 205`
6. `@py self.location.key = 1`
7. `zone set [your_name] void`



Check out the [roadmap][roadmap] for a high level view of future planned features to get the game to a stable and playable state.

[roadmap]: https://github.com/duysqubix/scrolls/blob/master/ROADMAP.md
