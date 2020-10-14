# Nice Things

macOS: Renice processes that behave poorly (we *can* have nice things!)


[begintoc]: #

# Contents

- [Requirements](#requirements)
- [Quick Start](#quick-start)
- [What Is It For?](#what-is-it-for)
- [How Does It Work?](#how-does-it-work)
- [How to Install](#how-to-install)
    - [What Will Happen?](#what-will-happen)
    - [Bare Minimum Install](#bare-minimum-install)
    - [Installing with a Periodic Schedule](#installing-with-a-periodic-schedule)
- [Customizing the Schedule](#customizing-the-schedule)
- [Customizing the Process Names](#customizing-the-process-names)
- [References](#references)

[endtoc]: #


## Requirements

- macOS (tested with 10.14.6 (Mojave))
- Access to `sudo` ("Allow user to administer this computer")
- Shell prompt


## Quick Start

    ./install.sh --with-crontab --dry-run
    nice-things --help


## What Is It For?

macOS likes to do some things---for example, Spotlight indexing---while a
Mac is turned on.  Sometimes, these activities happen while we humans want to
do other things with our Macs, but the activities are "bad neighbors" and use
too many system resources (like CPU).

If your Mac is running an anti-virus scanning program, for example, it may be
overexuberant, taking all the available CPU to get through a scan as fast as
possible.

**nice-things** helps by changing the *scheduling priority* of certain
processes to make them "less important" and give CPU time back to the things
*we* want to do.


## How Does It Work?

Summary:

```sh
$ nice-things --dry-run
[DRY-RUN] Would run:
+ sudo renice 20 -p 83244 83245 83247 83248 83249
$
```

**nice-things** does the following:

1. Find the processes whose *names* match the ones asked for.
2. Check each found process's priority.
3. If a process's priority is "too important", change its priority to make it
   less important.
4. If you want, write messages to the system log indicating what it's doing.

To do this, **nice-things** uses CLI commands called [pgrep][] (to find
matching processes), [ps][] (to find a process's priority) and [renice][] (to
change a process's priority).

If you just run **nice-things** from the command line, this happens once:

```sh
$ nice-things 
me@my-macbook-pro's password:
Oct 13 16:46:59  nice-things[86905] <Notice>: + sudo renice 20 -p 86412 86413
$
```

**nice-things** can also be run on a schedule in the background, using
[cron][] -- for example, running every minute or every 5 minutes.  This way,
**nice-things** can set the scheduling priority for processes that start when
you're not at your Mac, or when you're already in the middle of doing
something else.


## How to Install

**nice-things** comes with an installation script, called `install.sh`, which
requires a shell prompt in a Terminal window.


### What Will Happen?

You can see what `install.sh` will do without doing it by using the
`--dry-run` option:

```sh
$ ./install.sh --dry-run
me@my-macbook-pro's password:
[DRY-RUN] OK: Directory exists: /usr/local
[DRY-RUN] OK: Directory exists: /usr/local/bin
[DRY-RUN] Would install: /usr/local/bin/nice-things
[DRY-RUN] Would run:
+ sudo install -m 0755 -o 0 -g 0 bin/nice-things.sh /usr/local/bin/nice-things
$
```


### Bare Minimum Install

To install just the `nice-things` command, use:

    ./install.sh

If you want to install it somewhere besides `/usr/local/bin`, you may supply a
different prefix.  For example:

    ./install.sh --prefix /opt/nice-things


### Installing with a Periodic Schedule

To install both the `nice-things` command and the [crontab][] schedule for
periodically running in the background, use:

    ./install.sh --with-crontab

For example:

```sh
$ ./install.sh --with-crontab
me@my-macbook-pro's password:
OK: Directory exists: /usr/local
OK: Directory exists: /usr/local/bin
Installing: /usr/local/bin/nice-things
+ sudo install -m 0755 -o 0 -g 0 bin/nice-things.sh /usr/local/bin/nice-things
Retrieving root's crontab ...
Adding the following to root's crontab:
--- /path/to/temp/dir/install-nice-things.uiHuYvtC	2020-10-13 16:50:32.000000000 -0700
+++ /path/to/temp/dir/install-nice-things.dV7UZEHz	2020-10-13 16:50:32.000000000 -0700
@@ -0,0 +1,4 @@
+
+MAILTO=""
+
+* * * * * /usr/local/bin/nice-things --quiet
+ sudo crontab -u root /path/to/temp/dir/install-nice-things.dV7UZEHz
$
```

macOS may ask you something like:

> **“Terminal” would like to administer your  
> computer. Administration can include  
> modifying passwords, networking, and  
> system settings.**
>
> | Don't Allow | OK |

If you want the `crontab` changes to take effect, press **OK**.


## Customizing the Schedule

By default, `nice-things` is scheduled to run once a minute.  If you want to
change the frequency to, for example, every five minutes, you can edit root's
crontab:

    sudo crontab -u root -e

and change the first time/date field to `*/5`:

    */5 * * * * /usr/local/bin/nice-things --quiet

Then save and exit.

See the [crontab manual page][] for more information about how to customize
the schedule for a background "cron job".


## Customizing the Process Names

The default process names that **nice-things** reprioritizes are:

- iCoreService
- mdworker

You can change those by supplying a different list of process names or
patterns as command-line arguments to `nice-things`.  For example, if your
Google-based browser runs too fast for you:

    nice-things --dry-run 'Google Chrome'

That works whether you're using **nice-things** at your Bash or Zsh prompt or
as a periodic cron job.


## References

- Articles:
    - [CNet: Understanding process priority in OS X by Topher Kessler][cnet-article-priority]
    - [Wikipedia: Scheduling (computing)][wikipedia-scheduling]
- Commands:
    - [crontab manual page][crontab]
    - [pgrep manual page][pgrep]
    - [renice manual page][renice]


 [cnet-article-priority]: https://www.cnet.com/news/understanding-process-priority-in-os-x/
 [cron]: https://ss64.com/osx/cron.html
 [crontab]: https://ss64.com/osx/crontab.html
 [pgrep]: https://ss64.com/osx/pkill.html
 [ps]: https://ss64.com/osx/ps.html
 [renice]: https://linux.die.net/man/1/renice
 [wikipedia-scheduling]: https://en.wikipedia.org/wiki/Scheduling_(computing)
