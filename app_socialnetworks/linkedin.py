from __init__ import *
from oauthclient import *


class LinkedInClient(OauthClient):

	CONSUMER_KEY    = setting('LINKEDIN_CONSUMER_KEY')
	CONSUMER_SECRET = setting('LINKEDIN_CONSUMER_SECRET')

	def __init__(self, user_auth):
		self.user_auth = user_auth
		super(LinkedInClient, self).__init__(self.CONSUMER_KEY, self.CONSUMER_SECRET)


	def request_token(self, consumer):
		# Retrieve connected accounts
		connected_accounts = self.user_auth.social_auth.filter(user=self.user_auth.id).filter(provider="linkedin")
		if len(connected_accounts) == 0:
			raise NotConnectedException('Not Connected to LinkedIn')

		# Retrieve access_token from socialauth
		access_token       = connected_accounts[0].extra_data['access_token']
		access_token       = urlparse.parse_qs(access_token)
		oauth_token        = access_token['oauth_token'][0]
		oauth_token_secret = access_token['oauth_token_secret'][0]

		return oauth_token, oauth_token_secret


	def get_consumer_key(self):
		return self.CONSUMER_KEY


	def _query(self, fields):
		url = "http://api.linkedin.com/v1/people/~%s?format=json" % (fields, )
		try:
			resp, content = self.client.request(url, "GET")
			return json.loads(content)
		except:
			return None 


	# def basic_info(self):
	# 	return self._query(":(headline,industry,summary,public-profile-url)")

	# def positions(self):
	# 	return self._query(":(positions:(company:(name),title,summary,start-date,end-date))")['positions']['values']


	def get_employment_data(self):
		# Get Headline and Industry
		generic = self._query(":(headline,industry)")
		headline = generic['headline']
		industry = generic['industry']

		# Get Company and Title
		try:
			positions = self._query(":(three-current-positions)")['threeCurrentPositions']['values']
			current_position = positions[0]
			company = current_position['company']['name']
			title   = current_position['title']
		except:
			company = None
			title   = None
		

		# Result
		data = {'headline': headline, 'industry': industry, 
				'company': company, 'title': title}

		return data


	def skills(self):
		raw_data = self._query(":(skills:(skill:(name),proficiency:(name)))")['skills']['values']

		return [x['skill']['name'] for x in raw_data]

