from django import template
import re, os
register = template.Library()

def index(body):
    #body=body.replace(">>","&gt;&gt;")
    #if re.findall('\d+', body[body.find("&gt;&gt;"):body.find("<br>")]) != []:
    #    post = str(re.findall('\d+', body[(body.find("&gt;&gt;")):body.find("<br>")])[0])
    #    first = body.find(post)
    #    lenght = len(post)
    #    body = body[:(first-8)] + '<span class="resp" onmouseover=show_post(' + str(post) +')><a href ="/post-' + str(post)+ '">' + body[(first-8):(first+lenght)] + "</a></span>" + body[(first+lenght):];
    if body.count("**") % 2 == 0 and body.count("**") != 0:
        tags_num = body.count("**")
        c = 0
        while c <= tags_num/2:
            body = body.replace("**","<strong>",1);
            body = body.replace("**","</strong>",1);
            c+=1
    if body.count("*") % 2 == 0 and body.count("*") != 0:
        tags_num = body.count("*")
        c = 0
        while c <= tags_num/2:
            body = body.replace("*","<i>",1);
            body = body.replace("*","</i>",1);
            c+=1
    if body.count("DEL") % 2 == 0 and body.count("DEL") != 0:
        tags_num = body.count("DEL")
        c = 0
        while c <= tags_num/2:
            body = body.replace("DEL","<strike>",1);
            body = body.replace("DEL","</strike>",1);
            c+=1
    if body.count("%%") % 2 == 0 and body.count("%%") != 0:
        tags_num = body.count("%%")
        c = 0
        while c <= tags_num/2:
            body = body.replace("%%",'<span class="spoiler">',1);
            body = body.replace("%%","</span>",1);
            c+=1
    if body.count("https://www.youtube.com/watch?v=") != 0:
        tags_num = body.count("https://www.youtube.com/watch?v=")
        while tags_num != 0:
            tag = body.find("https://www.youtube.com/watch?v=")
            body = body[:(tag+43)]+'"></iframe><br>'+body[(tag+43):]
            body = body.replace("https://www.youtube.com/watch?v=",'<br><iframe class="responsive-video" src="http://www.youtube.com/embed/')
            tags_num = body.count("https://www.youtube.com/watch?v=")
    if body.count("http://www.youtube.com/watch?v=") != 0:
        tags_num = body.count("http://www.youtube.com/watch?v=")
        while tags_num != 0:
            tag = body.find("http://www.youtube.com/watch?v=")
            body = body[:(tag+42)]+'"></iframe><br>'+body[(tag+42):]
            body = body.replace("http://www.youtube.com/watch?v=",'<br><iframe class="responsive-video" src="http://www.youtube.com/embed/')
            tags_num = body.count("http://www.youtube.com/watch?v=")
    return body;

def cut_text(body):
    body=body.replace("\r\n","<br>")
    return body;

def get_ext(filename):
    filename, ext = os.path.splitext(filename)
    return ext.lower();
	
def dec(value): # decrement operation
	return (int(value) - 1);

def inc(value): # increment operation
	return (int(value) + 1);

def minus(value1, value2):
	return (int(value1)-int(value2));

def plus(value1, value2):
	return (int(value1)+int(value2));

register.filter('index', index)
register.filter('cut_text', cut_text)
register.filter('get_ext', get_ext)
register.filter('dec', dec)
register.filter('inc', inc)
register.filter('minus', minus)
register.filter('plus', plus)

