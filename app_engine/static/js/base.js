var BReader = {};

BReader.all_stories = [];
BReader.all_feed_ids = [];
BReader.current_index = -1;

BReader.moveForward = function(){
  if(BReader.current_index < (BReader.all_stories.length - 1)){
    BReader.current_index += 1;
    return true;
  } else {
    return false;
  }
}

BReader.moveBackward = function(){
  if(BReader.current_index > 0){
    BReader.current_index -= 1;
    return true;
  } else {
    return false;
  }
}

BReader.currentStoryID = function(){
  if(BReader.current_index > -1){
    return BReader.all_stories[BReader.current_index];
  }
}

BReader.currentFeedID = function(){
  if(BReader.current_index > -1){
    return BReader.all_feed_ids[BReader.current_index];
  }
}

BReader.jumpToStory = function(id, mobile){
  if(mobile == true){
    // for some reason, chrome on android won't jump to anchor tags
    // so I had to use a jquery work-a-round
    $('html, body').animate({scrollTop: $(id).offset().top}, 10);
  } else {
    document.location.replace(id);
  }
}

BReader.removeStory = function(){
  BReader.all_stories.splice(BReader.current_index, 1);
  if(BReader.current_index > 0){
    BReader.current_index -= 1;
  }
}

BReader.shouldFetchMoreStories = function(){
  return (BReader.all_stories.length - BReader.current_index) < 10;
}

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

BReader.appendResults = function(stories){
  for (var i=0; i<stories.length; i++){
    story = stories[i];
    BReader.all_stories.push(story.key.toString());
    BReader.all_feed_ids.push(story.feed_guid);
    html = BReader.render(story);
    $('#maintable').append(html);
  }
  // force all external links to open in new tab
  $("a[href^='http']").attr('target','_blank');
}

BReader.nothingAvailable = '<div class="jumbotron"><div class="media"><img class="media-object pull-left" src="/static/wiggum.gif"><div class="media-body"><h1>Nothing to see here!</h1><p>Move along . . .</p></div></div></div>';
