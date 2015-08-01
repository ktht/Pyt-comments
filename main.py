from comment_fetcher import CommentFetcher as CF
from comment_fetcher import CommentPrinter as CP
from comment_fetcher import Common
import argparse
import sys

if __name__ == '__main__':

    # parse command line arguments
    parser = argparse.ArgumentParser(description='Dump youtube comments to a file.')
    parser.add_argument('-u', '--url',        action='store',                           \
                        metavar='string', type=str, nargs='?', help="URL of the video")
    parser.add_argument('-y', '--youtube-id', action='store',                           \
                        metavar='string', type=str, nargs='?', help="YouTube video ID")
    parser.add_argument('-l', '--limit',      action='store',      default=sys.maxsize, \
                        metavar='N',      type=int, nargs='?', help='number of comments ' + \
                                                                    '(default: all)')
    parser.add_argument('-o', '--output',     action='store',                           \
                        metavar='string', type=str, nargs='?', help='name of the output file ' + \
                                                                    '(default: comments-ID.txt)')
    parser.add_argument('-v',                 action='store_true', default=False,       \
                                                               help='enable verbose mode')
    parser.add_argument('-f',                 action='store_true', default=False,       \
                                                               help='rewrite output file')
    parser.add_argument('-a',                 action='store_true', default=False,       \
                                                               help='append to output file ' + \
                                                                    '(plaintext only)')
    parser.add_argument('-d',                 action='store_true', default=False,       \
                                                               help='disable timestamps')
    parser.add_argument('-p',                 action='store_true', default=False,       \
                                                               help='print as plaintext')
    parser.add_argument('-D',                 action='store_true', default=False,
                                                               help='disable links (HTML only)')
    parser.add_argument('-E',                 action='store_true', default=False,       \
                                                               help='embed video (HTML only)')
    parser.add_argument('-n',                 action='store_true', default=False,       \
                                                               help='get number of comments ' + \
                                                                    '(doesn\'t generate the file)')
    args = parser.parse_args()

    # consistency check 101
    verbose = args.v
    use_the_force = args.f
    append = args.a
    disable_timestamps = args.d
    disable_links = args.D
    print_as_plaintext = args.p
    enable_embed_video = args.E
    print_info_only = args.n
    limit = args.limit
    filename = args.output
    yt_id = args.youtube_id
    yt_url = args.url

    if limit < 1:
        Common.handle_wrong_cmdargs("Number of requested comments must be >=1.", \
                                    parser.print_usage)
    elif yt_id is None and yt_url is None:
        Common.handle_wrong_cmdargs("You must give either URL or YouTube-ID.", \
                                    parser.print_usage)
    elif yt_id is not None and yt_url is not None:
        Common.handle_wrong_cmdargs("You gave both URL and YouTube-ID. Make up your mind.", \
                                    parser.print_usage)
    elif yt_url is not None and not CF.is_valid_url(yt_url):
        Common.handle_wrong_cmdargs("Invalid URL.", \
                                    parser.print_usage)
    elif append and use_the_force:
        Common.handle_wrong_cmdargs("Conflicting flags: append (-a) and overwrite (-f).", \
                                    parser.print_usage)
    elif append and not print_as_plaintext:
        Common.handle_wrong_cmdargs("Append mode for HTML files not supported.", \
                                    parser.print_usage)
    
    # verify the YouTube-ID/URL correctness before deleting and/or creating any files
    cf = CF.CommentFetcher()
    cf.set_limit(limit)
    try:
        if yt_id is not None:
            cf.set_yt_id(yt_id)
        else:
            cf.set_yt_id_from_url(yt_url)
        cf.initialize()
    except:
        Common.handle_wrong_cmdargs("Invalid YouTube URL or ID.", \
                                    parser.print_usage)
    
    if print_info_only:
        sys.stdout.write("The video with ID " + cf.get_yt_id() + \
                         " has " + str(cf.get_total_nof_comments()) + " comments.\n")
        sys.exit(0)
    
    cp = CP.CommentPrinter(filename, cf.get_yt_id())
    cp.set_append(append)
    cp.set_force_overwriting(use_the_force)
    cp.set_disable_timestamps(disable_timestamps)
    cp.set_disable_links(disable_links)
    cp.set_print_as_plaintext(print_as_plaintext)
    cp.set_action_on_error(parser.print_usage)
    cp.set_enable_embed_video(enable_embed_video)
    cp.set_total_nof_comments(cf.get_total_nof_comments())
    cp.set_req_nof_comments(min(limit, cf.get_total_nof_comments()))
    
    cp.create_file()
    
    Common.print_if_verbose("There are " + str(cf.get_total_nof_comments()) + \
                            " comment(s) for this video in total.", verbose)
    
    nof_comments = 0
    cp.open()
    while (cf.has_more()):
        cf.process()
        comments = cf.get_comments()
        for comment in comments:
            cp.write(comment)
        
        nof_comments += len(comments)
        Common.print_if_verbose ("\r\x1b[K" + str(nof_comments) + \
                                 " out of " + str(min(cf.get_total_nof_comments(), limit)) + \
                                 " comments written.", verbose, add_newline=False, flush=True)
        cf.clear()
    cp.close()
        
    Common.print_if_verbose ("\nWrote " + str(nof_comments) + " comments to " + \
                             cp.get_filename() + ".", verbose)
