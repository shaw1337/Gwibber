"""

Gwibber Client Interface Library
SegPhault (Ryan Paul) - 05/26/2007

"""

from . import gintegration, resources
import webkit, gtk
import urllib2, hashlib, os, simplejson
from mako.template import Template
import Image

# i18n magic
import gettext

_ = gettext.lgettext

DEFAULT_UPDATE_INTERVAL = 1000 * 60 * 5
IMG_CACHE_DIR = os.path.join(resources.CACHE_BASE_DIR, "gwibber", "images")
DEFAULT_AVATAR = 'http://digg.com/img/udl.png'

class MapView(webkit.WebView):
  def __init__(self):
    webkit.WebView.__init__(self)
    self.message_store = []
    self.data_retrieval_handler = None
    self.open("file://%s" % resources.get_ui_asset(map.html))

  def load_theme(self, theme):
    self.theme = theme

  def load_messages(self, message_store = None):
    msgs = message_store or self.message_store
    self.execute_script("LoadMap(%s, %s)" % (msgs[0].location_latitude, msgs[0].location_longitude))
    for m in (message_store or self.message_store):
      self.execute_script("AddPin(%s, %s, '%s', '%s', '%s')" % (m.location_latitude, m.location_longitude, m.sender, m.location_fullname, m.image_small))

  def load_preferences(self, preferences):
    pass

class MessageView(webkit.WebView):
  def __init__(self, theme):
    webkit.WebView.__init__(self)
    self.load_externally = True
    self.connect("navigation-requested", self.on_click_link)
    self.load_theme(theme)
    self.message_store = []
    self.data_retrieval_handler = None

  def load_theme(self, theme):
    self.theme = theme

  def load_messages(self, account_prefs=None, theme_prefs=None, message_store = None):
    # Translators: this string appears when somebody reply to a message
    # like '3 minutes ago in reply to angelina'
    reply_string = " " + _("in reply to") + " "
    # Translators: this string indicates where the message arrived from
    # like 'from api', 'from Gwibber' 
    from_string = " " + _("from") + " "
    # Done that way so translators don't have to handle white/empty spaces
    # and there's no need to handle them in the html too
    ui_dict = {"reply": reply_string, "from": from_string}
    
    for n, m in enumerate(self.message_store):
      m.message_index = n

      if m.account[m.bgcolor]:
        c = gtk.gdk.color_parse(m.account[m.bgcolor])
        m.bgcolor_rgb = {"red": c.red//255, "green": c.green//255, "blue": c.blue//255}

    template_path = os.path.join(resources.get_theme_path(self.theme), "template.mako")
    content = Template(open(template_path).read()).render(
      message_store=self.message_store,
      account_prefs=account_prefs,
      theme_prefs=theme_prefs)

    self.load_html_string(content, "file://%s/" % resources.get_theme_path(self.theme))

  def on_click_link(self, view, frame, req):
    uri = req.get_uri()
    if uri.startswith("file:///"): return False
    
    if not self.link_handler(uri, self) and self.load_externally:
      gintegration.load_url(uri)
    return self.load_externally

  def link_handler(self, uri):
    pass

class UserView(MessageView):
  def load_messages(self, message_store = None): # override
    if (self.message_store and len(self.message_store) > 0):
      # use info from first message to create user header
      msg = simplejson.dumps(dict(self.message_store[0].__dict__, message_index=0), sort_keys=True, indent=4, default=str)
      self.execute_script("addUserHeader(%s)" % msg)
      # display other messages as normal
      MessageView.load_messages(self, message_store)

def image_cache(url, cache_dir = IMG_CACHE_DIR):
  if not os.path.exists(cache_dir): os.makedirs(cache_dir)
  encoded_url = hashlib.sha1(url).hexdigest()
  if len(encoded_url) > 200: encoded_url = encoded_url[::-1][:200]
  fmt = url.split('.')[-1] # jpg/png etc.
  img_path = os.path.join(cache_dir, encoded_url + '.' + fmt).replace("\n", "")

  if not os.path.exists(img_path):
    output = open(img_path, "w+")
    try:
      output.write(urllib2.urlopen(url).read())
      output.close()
      try:
        image = Image.open(img_path)
        (x, y) = image.size
        if x != 48 or y != 48:
          if image.mode == 'P': # need to upsample limited palette images before resizing
            image = image.convert('RGBA') 
          image = image.resize((48, 48), Image.ANTIALIAS)
          image.save(img_path)
      except Exception, e:
        from traceback import format_exc
        print(format_exc())
    except IOError, e:
      if hasattr(e, 'reason'): # URLError
        print('image_cache URL Error: %s whilst fetching %s' % (e.reason, url))
      elif hasattr(e, 'code') and hasattr(e, 'msg') and hasattr(e, 'url'): # HTTPError
        print('image_cache HTTP Error %s: %s whilst fetching %s' % (e.code, e.msg, e.url))
      else:
        print(e)
      # if there were any problems getting the avatar img replace it with default
      output.write(urllib2.urlopen(DEFAULT_AVATAR).read())
    finally:
      output.close()

  return img_path
