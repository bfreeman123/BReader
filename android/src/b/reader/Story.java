package b.reader;

import org.json.JSONException;
import org.json.JSONObject;

public class Story {
	String key;
	String feed_name;
	String feed_url;
	String title;
	String link;
	String description;
	String pub_date;

	public Story(JSONObject o) {
		try {
			this.key = o.getString("key");
			this.feed_name = o.getString("feed_name");
			this.feed_url = o.getString("feed_url");
			this.title = o.getString("title");
			this.link = o.getString("link");
			this.description = o.getString("description");
			this.pub_date = o.getString("pub_date");
		} catch (JSONException e) {
			this.key = null;
			this.feed_name = null;
			this.feed_url = null;
			this.title = null;
			this.link = null;
			this.description = null;
			this.pub_date = null;
			e.printStackTrace();
		}
	}

}
