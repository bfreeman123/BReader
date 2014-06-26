var BReader = {};

BReader.templateEngine = function(tpl, data) {
  var re = /<%([^%>]+)?%>/g;
  while(match = re.exec(tpl)) {
    tpl = tpl.replace(match[0], data[match[1]])
  }
  return tpl;
}

BReader.render = function(story){
  template = '\
<a id="a_<%guid%>" name="a_<%guid%>" class="anchor"></a>\
<div class="panel panel-default" id="s_<%guid%>">\
<div class="panel-heading">\
  <h3 class="panel-title" style="font-size:20px;margin-bottom:20px;"><a href="<%link%>"><%title%></a></h3>\
  <span class="pull-left" style="margin-top:-15px;"><a href="<%feed_url%>" style="color:inherit;"><%feed_name%></a></span>\
  <span class="pull-right" style="margin-top:-15px;"><%date%></span>\
</div>\
<div class="panel-body" style="overflow:auto;"><%content%></div>\
</div>';
  html = BReader.templateEngine(template, {
    guid: story.key,
    title: story.title,
    link: story.link,
    content: story.description,
    feed_url: story.feed_url,
    feed_name: story.feed_name,
    date: story.pub_date,
  });
  return html;
}
