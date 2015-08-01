import xml.etree.ElementTree as ET
from xml.dom import minidom
import datetime as dt
import codecs
import os

from comment_fetcher import CSSBuilder as CB
from comment_fetcher import Common

class CommentPrinter:
    
    UNDEFINED = -1
    
    def __init__(self, filename, yt_id):
        self.__filename = filename
        self.__yt_id = yt_id
        self.__total_nof_comments = CommentPrinter.UNDEFINED # HTML only
        self.__set_req_nof_comments = CommentPrinter.UNDEFINED # HTML only
        self.__filehandle = None
        
        self.__print_as_plaintext = False # default: HTML
        self.__disable_timestamps = False
        self.__disable_links = False # False == HTML only
        self.__use_the_force = False
        self.__enable_embed_video = False # HTML only
        
        self.__verbose = False
        self.__action = None
        self.__css_styles = []
    
    def set_disable_timestamps(self, disable_timestamps):
        self.__disable_timestamps = disable_timestamps
    
    def set_disable_links(self, disable_links):
        self.__disable_links = disable_links
    
    def set_print_as_plaintext(self, print_as_plaintext):
        self.__print_as_plaintext = print_as_plaintext
    
    def set_append(self, append):
        self.__append = append
    
    def set_verbose(self, verbose):
        self.__verbose = verbose
    
    def set_force_overwriting(self, use_the_force):
        self.__use_the_force = use_the_force
    
    def set_action_on_error(self, action):
        self.__action = action
    
    def set_enable_embed_video(self, enable_embed_video):
        self.__enable_embed_video = enable_embed_video
    
    def set_total_nof_comments(self, total_nof_comments):
        self.__total_nof_comments = total_nof_comments
    
    def set_req_nof_comments(self, req_nof_comments):
        self.__req_nof_comments = req_nof_comments
    
    def get_filename(self):
        return self.__filename
    
    def __construct_filename(self):
        filename = "comments-" + self.__yt_id + "."
        if self.__print_as_plaintext: filename += "txt"
        else:                         filename += "html"
        return filename
    
    def create_file(self):
        if self.__filename is None:
            self.__filename = self.__construct_filename()
        if os.path.isfile(self.__filename) and not self.__append:
            if not self.__use_the_force:
                Common.handle_wrong_cmdargs("File " + self.__filename + " already exists. " + \
                                            "Use -f to overwrite or -a to append.", self.__action)
            else:
                try:
                    os.remove(self.__filename)
                    Common.print_if_verbose ("Deleted file " + self.__filename + " ...", \
                                             self.__verbose)
                except: #TODO improve
                    Common.handle_wrong_cmdargs("Couldn't remove file " + self.__filename + \
                                                ". Abort.", self.__action)
        elif not os.path.isfile(self.__filename) and self.__append:
            Common.print_if_verbose("Warning: can't append to " + self.__filename + \
                                    " as it doesn't exist", self.__verbose)
    
    def open(self):
        mode = 'a+' if self.__append else 'w+'
        if self.__filename is None:
            Common.handle_wrong_cmdargs("Error -- no filename given.", self.__action)
        try:
            self.__filehandle = codecs.open(self.__filename, mode, encoding='utf-8')
            if self.__use_the_force:
                Common.print_if_verbose("Creating " + self.__filename + " ...", self.__verbose)
        except:
            Common.handle_wrong_cmdargs("Error on creating/writing to the file.", self.__action)
        
        if self.__filehandle is not None and not self.__print_as_plaintext:
            self.__add_html_header()
    
    def close(self):
        if self.__filehandle is not None:
            if not self.__print_as_plaintext:
                self.__add_html_footer()
            self.__filehandle.close()
    
    def __build_css(self):
        general_css = CB.CSSBuilder("*")
        general_css.add("font-family", "Roboto,arial,sans-serif")
        general_css.add("font-size",   "13px")
        self.__css_styles.append(general_css)
        
        author_css = CB.CSSBuilder(".author")
        author_css.add("font-weight",     "600")
        author_css.add("display",         "inline")
        author_css.add("color",           "#167ac6")
        author_css.add("word-break",      "break-all")
        author_css.add("text-decoration", "none")
        author_css.add("font-size",       "100%")
        author_css.add("float",           "left")
        author_css.add("margin-right",    "10px") # padding clickable :(
        self.__css_styles.append(author_css)
        
        shared_css = CB.CSSBuilder(".shared")
        shared_css.add("font-style", "italic")
        shared_css.add("font-size",  "100%")
        shared_css.add("display",    "inline")
        shared_css.add("float",      "right")
        shared_css.add("padding-left", "10px")
        self.__css_styles.append(shared_css)
        
        table_css = CB.CSSBuilder("table")
        table_css.add("margin-bottom", "20px")
        table_css.add("display",       "block")
        table_css.add("text-align",    "left");
        self.__css_styles.append(table_css)
        
        td_date_css = CB.CSSBuilder("td.date")
        td_date_css.add("font-size", "11px")
        td_date_css.add("color",     "#767676")
        td_date_css.add("display",   "inline-block")
        self.__css_styles.append(td_date_css)
        
        info_comment_css = CB.CSSBuilder(".info_comment")
        info_comment_css.add("font-size",      "13px")
        info_comment_css.add("text-transform", "uppercase")
        info_comment_css.add("font-weight",    "600")
        info_comment_css.add("color",          "#666")
        info_comment_css.add("word-spacing",   "10px")
        info_comment_css.add("letter-spacing", "1px")
        info_comment_css.add("margin",         "10px")
        self.__css_styles.append(info_comment_css)
        
        td_comment_css = CB.CSSBuilder("td.comment")
        td_comment_css.add("padding-left", "10px")
        td_comment_css.add("font-size",    "100%")
        td_comment_css.add("white-space",  "pre-wrap")
        td_comment_css.add("overflow",     "hidden")
        td_comment_css.add("word-wrap",    "break-word")
        self.__css_styles.append(td_comment_css)
        
        gplus_css = CB.CSSBuilder("a.gplus")
        gplus_css.add("background",      "#d34836")
        gplus_css.add("color",           "#ffffff")
        gplus_css.add("border-radius",   "2px")
        gplus_css.add("text-decoration", "none")
        gplus_css.add("font-size",       "9px")
        gplus_css.add("display",         "inline")
        gplus_css.add("float",           "left")
        self.__css_styles.append(gplus_css)
        
        body_css = CB.CSSBuilder("body")
        body_css.add("text-align", "center")
        self.__css_styles.append(body_css)
        
        page_wrap_css = CB.CSSBuilder("#page-wrap")
        page_wrap_css.add("width",  "600px")
        page_wrap_css.add("margin", "0 auto")
        self.__css_styles.append(page_wrap_css)
    
    def __add_html_header(self):
        self.__filehandle.write("<!DOCTYPE html>\n" + \
                                "  <html lang=\"en\">\n" + \
                                "    <head>\n" + \
                                "    <meta charset=\"utf-8\">\n" + \
                                "    <title>Comments for " + self.__yt_id + "</title>\n" + \
                                "    <style>\n")
        
        # CSS shnizzle
        if len(self.__css_styles) == 0:
            self.__build_css()
        for css in self.__css_styles:
            self.__filehandle.write(css.to_string())
        
        self.__filehandle.write("    </style>\n" + \
                                "  </head>\n" + \
                                "<body>\n")
        
        self.__filehandle.write("<div id=\"page-wrap\">\n")
        
        if self.__enable_embed_video:
            iframe = "<iframe width=\"500\"" + \
                             "height=\"325\"" + \
                             "src=\"https://www.youtube.com/embed/" + self.__yt_id + \
                                   "?modestbranding=1" + \
                                   "&autohide=1" + \
                                   "&iv_load_policy=3" + \
                                   "\"" + \
                             "frameborder=\"0\"" + \
                             "allowfullscreen" + \
                     "></iframe>\n"
            self.__filehandle.write("  " + iframe + "\n")
        
        if self.__total_nof_comments != CommentPrinter.UNDEFINED and \
           self.__req_nof_comments != CommentPrinter.UNDEFINED:
            comment_info = ET.Element("div", {"class": "info_comment"})
            comment_info_text = "loaded "
            if self.__total_nof_comments == self.__req_nof_comments:
                comment_info_text += str(self.__total_nof_comments)
            else:
                comment_info_text += str(self.__req_nof_comments) + "/" + \
                                     str(self.__total_nof_comments)
            comment_info.text = comment_info_text
            
            self.__filehandle.write(self.__html_prettify(comment_info))
        
        self.__filehandle.flush()
        
    
    def __add_html_footer(self):
        self.__filehandle.write("</div>\n" + \
                                "</body>\n" + \
                                "</html>")
        self.__filehandle.flush()
    
    def __parse_date(self, date):
        date_obj = dt.datetime.strptime(date, "%Y-%m-%dT%H:%M:%S.000Z")
        return date_obj
    
    def __print_plaintext(self, comment):
        self.__filehandle.write(comment.author + "\n")
        
        if not self.__disable_timestamps:
            publish_date_obj = self.__parse_date(comment.publish_date)
            mod_date_obj = self.__parse_date(comment.mod_date)
            self.__filehandle.write("on " + publish_date_obj.strftime("%d-%m-%Y %H:%M:%S "))
            if publish_date_obj != mod_date_obj:
                self.__filehandle.write("(last edited on " + \
                                 mod_date_obj.strftime("%d-%m-%Y %H:%M:%S") + ") ")
        
        if comment.content is not None:
            self.__filehandle.write("said:\n" + comment.content)
        else:
            self.__filehandle.write("shared on Google+")
        self.__filehandle.write("\n---------------------------------\n")
        
        self.__filehandle.flush()
    
    def __html_prettify(self, html_node):
        html_string = ET.tostring(html_node, 'utf-8')
        reparsed = minidom.parseString(html_string)
        html_pretty_string = reparsed.toprettyxml(indent="  ")
        # removes xml BS minidom generates (first row)
        html_pretty_string = html_pretty_string[html_pretty_string.find('\n')+1:]
        
        return html_pretty_string
    
    def __print_html(self, comment):
        table = ET.Element("table")
    
        author_row = ET.SubElement(table, "tr")
        author_column = ET.SubElement(author_row, "td")
        
        if not self.__disable_links:
            if comment.channel_id is not None and \
               comment.channel_id != "UC__NO_YOUTUBE_ACCOUNT__":
                author_text = ET.SubElement(author_column, "a", \
                    {"class": "author",                                                \
                     "href":  "https://www.youtube.com/channel/" + comment.channel_id, \
                     "title": "YouTube channel: " + comment.author})
                author_text.text = comment.author
            else:
                author_text = ET.SubElement(author_column, "div", {"class": "author"})
                author_text.text = comment.author
            
            if comment.gplus_id is not None:
                gplus_div = ET.SubElement(author_column, "a", \
                            {"href":  "https://plus.google.com/" + comment.gplus_id, \
                             "class": "gplus",                                       \
                             "title": "Google+ profile: " + comment.author})
                gplus_div.text = "G+"
        else:
            author_text = ET.SubElement(author_column, "div", {"class": "author"})
            author_text.text = comment.author
        
        if not self.__disable_timestamps:
            date_row = ET.SubElement(table, "tr")
            date_column = ET.SubElement(date_row, "td", {"class": "date"})
            
            publish_date_obj = self.__parse_date(comment.publish_date)
            mod_date_obj = self.__parse_date(comment.mod_date)
            date_str = publish_date_obj.strftime("%d-%m-%Y %H:%M:%S")
            if publish_date_obj != mod_date_obj:
                date_str += " (last edited on " + \
                            mod_date_obj.strftime("%d-%m-%Y %H:%M:%S") + ")"
            date_column.text = date_str
        
        if comment.content is not None:
            content_row = ET.SubElement(table, "tr")
            content_column = ET.SubElement(content_row, "td", {"class": "comment"})
            content_column.text = comment.content
        else:
            author_shared = ET.SubElement(author_column, "div", {"class": "shared"})
            author_shared.text = " shared on Google+"
        
        self.__filehandle.write(self.__html_prettify(table))
        self.__filehandle.flush()
    
    def write(self, comment):
        if self.__print_as_plaintext:
            self.__print_plaintext(comment)
        else:
            self.__print_html(comment)