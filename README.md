## yt-comments-py

A Python script trying to retrieve all YouTube comments by using (already) deprecated [YouTube API v2](https://developers.google.com/youtube/2.0/developers_guide_protocol).
The script doesn't fetch the comments written via Google+, which usually means that the comments posted as a reply aren't retrieved.
The script uses [requests](http://docs.python-requests.org/) module to send HTTP requests.

The default output is an HTML file containing all retrieved comments, their authors, timestamps and links to authors' profiles.
Specifiers like `-d` and `-D` disable timestamps and profile links, respectively.
The alternative to HTML-formatted output is a plaintext file (`-p`) containing only the authors, timestamps and the comments.
The default filename is `comments-YOUTUBE_ID.html` (or `*.txt`), which can be overridden with `-o` option.
The script accepts both `YOUTUBE_ID` (`-y`) and URLs (`-u`) (regular, short, mobile, embedded etc).

### Usage

Help printout:
```
$ python main.py --help
usage: main.py [-h] [-u [string]] [-y [string]] [-l [N]] [-o [string]] [-v]
               [-f] [-a] [-d] [-p] [-D] [-E] [-n]

Dump youtube comments to a file.

optional arguments:
  -h, --help            show this help message and exit
  -u [string], --url [string]
                        URL of the video
  -y [string], --youtube-id [string]
                        YouTube video ID
  -l [N], --limit [N]   number of comments (default: all)
  -o [string], --output [string]
                        name of the output file (default: comments-ID.txt)
  -v                    enable verbose mode
  -f                    rewrite output file
  -a                    append to output file (plaintext only)
  -d                    disable timestamps
  -p                    print as plaintext
  -D                    disable links (HTML only)
  -E                    embed video (HTML only)
  -n                    get number of comments (doesn't generate the file)
```

### Examples

Get the number of comments (`-n`) given `YOUTUBE_ID` (`-y`):
```
$ python main.py -y dxBvUqLs_eU -n
The video with ID dxBvUqLs_eU has 2117 comments.
```

Get all comments, given the link to the video (`-u`), overwrite already existing file (`-f`), embed video into the HTML file (`-E`) and use verbose mode (`-v`):
```
$ python main.py -f -u https://www.youtube.com/watch?v=Mp-vBR66fHM -Ev
There are 18 comment(s) for this video in total.
18 out of 18 comments written.
Wrote 18 comments to comments-Mp-vBR66fHM.html.
```

Get latest 15 comments (`-l`), given `YOUTUBE_ID` (`-y`); save as plaintext (`-p`) without timestamps (`-d`) and use verbose mode (`-v`):
```
$ python main.py -f -l 15 -y dxBvUqLs_eU -pvd
There are 2117 comment(s) for this video in total.
15 out of 15 comments written.
Wrote 15 comments to comments-dxBvUqLs_eU.txt.
```
