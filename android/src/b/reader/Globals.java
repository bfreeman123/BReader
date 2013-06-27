package b.reader;

import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStream;
import java.io.InputStreamReader;
import java.io.UnsupportedEncodingException;
import java.util.ArrayList;
import java.util.List;
import java.util.Map;
import org.apache.http.HttpResponse;
import org.apache.http.NameValuePair;
import org.apache.http.client.ClientProtocolException;
import org.apache.http.client.entity.UrlEncodedFormEntity;
import org.apache.http.client.methods.HttpPost;
import org.apache.http.impl.client.DefaultHttpClient;
import org.apache.http.message.BasicNameValuePair;
import org.json.JSONException;
import org.json.JSONObject;

import android.app.Application;
import android.content.Context;
import android.net.ConnectivityManager;
import android.net.NetworkInfo;
import android.util.Log;
import android.widget.Toast;

public class Globals extends Application {
	// global instance to persist cookies between requests
	private DefaultHttpClient httpClient;

	// our temporary auth_token
	String auth_token = null;
	
	// our API endpoint
	private final String HOST = "https://fill-me-in.appspot.com";
	
	// our Log tag
	private final String LOG = "BReader";
	
	// our API KEY
	private final String API_KEY = "fill-me-in";

	public void onCreate() {
		httpClient = new DefaultHttpClient();
		super.onCreate();
	}
	
	public String getApiKey(){
		return API_KEY;
	}
	
	public boolean isOnline() {
		try {
			ConnectivityManager connMgr = (ConnectivityManager) this.getSystemService(Context.CONNECTIVITY_SERVICE);
			NetworkInfo networkInfo = connMgr.getActiveNetworkInfo();
			return (networkInfo != null && networkInfo.isConnected());
		} catch (Exception e) {
			e.printStackTrace();
		}
		return false;
	}
	
	public UrlEncodedFormEntity formatArgs(Map<String, String> args){
		List<NameValuePair> results = new ArrayList<NameValuePair>();
		for (Map.Entry<String, String> entry : args.entrySet()) {
			results.add(new BasicNameValuePair(entry.getKey(), entry.getValue()));
		}
		UrlEncodedFormEntity ret = null;
		try {
			ret = new UrlEncodedFormEntity(results);
		} catch (UnsupportedEncodingException e) {
			e.printStackTrace();
		}
		return ret;
	}
	
	public JSONObject doPostSingle(String path, Map<String, String> params){
		Log.i(LOG, "doPostSingle for " + path + " with " + params);
		if(isOnline()){
			HttpPost httpPost = new HttpPost(HOST + path);
			UrlEncodedFormEntity p = formatArgs(params);
			httpPost.setEntity(p);
			HttpResponse httpResponse;
			try {
				httpResponse = httpClient.execute(httpPost);
				InputStream inputStream;
				inputStream = httpResponse.getEntity().getContent();
				InputStreamReader inputStreamReader = new InputStreamReader(inputStream);
				BufferedReader bufferedReader = new BufferedReader(inputStreamReader);
				StringBuilder stringBuilder = new StringBuilder();
				String bufferedStrChunk = null;
				while((bufferedStrChunk = bufferedReader.readLine()) != null){
					stringBuilder.append(bufferedStrChunk);
				}
				String result = stringBuilder.toString();
				Log.i(LOG, "doPostSingle got result: " + result);
				JSONObject jObject = new JSONObject(result);
				Log.i(LOG, "parsed json as: " + jObject);
				return jObject;
			} catch (ClientProtocolException e) {
				e.printStackTrace();
			} catch (IOException e) {
				e.printStackTrace();
			}
			catch (IllegalStateException e) {
				e.printStackTrace();
			} catch (JSONException e) {
				e.printStackTrace();
			}
		} else{
			Toast.makeText(this, "Cannot connect to network", Toast.LENGTH_LONG).show();
		}
		return null;
	}
}
