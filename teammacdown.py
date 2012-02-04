''' TMD - SURVIVE SAC '''

import os
import sys
import cgi
import hmac
import base64
import urllib
import config
import random
import string
import hashlib
import slimmer
import datetime

from xml.dom import minidom

import logging

import webapp2 as webapp

try:
	import json
except ImportError:
	try:
		import simplejson as json
	except ImportError:
		from django.utils import simplejson as json

from webapp2_extras import routes
from webapp2_extras import jinja2
from webapp2_extras import sessions

from mapreduce import operation as op

from google.appengine.ext import db
from google.appengine.api import mail
from google.appengine.api import users
from google.appengine.api import channel
from google.appengine.api import urlfetch
from google.appengine.api import taskqueue
from google.appengine.ext.webapp.util import run_wsgi_app


class Player(db.Model):
	
	full_name = db.StringProperty()
	first_name = db.StringProperty()
	last_name = db.StringProperty()
	names = db.StringListProperty()
	email = db.EmailProperty()
	date = db.DateTimeProperty(auto_now_add=True)
	age = db.StringProperty()
	refer = db.StringProperty(multiline=True)
	previous_game = db.StringProperty()
	smartphone = db.StringProperty()
	gender = db.StringProperty(choices=['male', 'female'])
	fb = db.BooleanProperty(default=False)
	fb_id = db.StringProperty()
	fb_username = db.StringProperty()
	

class AdHit(db.Model):
	
	source = db.StringProperty()
	medium = db.StringProperty()
	location = db.StringProperty()
	group = db.StringProperty()


class CheckoutOrder(db.Model):
	
	order_id = db.StringProperty()
	status = db.StringProperty(choices=['queued', 'charged', 'complete'], default='queued')
	player = db.ReferenceProperty(Player, collection_name='checkout_orders')
	serial_number = db.StringProperty()


class GamePlayer(db.Model):
	
	name = db.StringProperty()
	email = db.EmailProperty()
	age = db.StringProperty()
	dt = db.DateTimeProperty(auto_now_add=True)
	previous = db.StringProperty()


class CheckIn(db.Model):
	
	player = db.StringProperty()
	checkpoint = db.StringProperty()
	dt = db.DateTimeProperty()


class PlayerStats(db.Model):

	checkins_completed = db.StringListProperty()
	checkins_completed_count = db.IntegerProperty(default=0)
	player = db.ReferenceProperty(GamePlayer, collection_name='stats')


class TMDEvent(db.Model):

	name = db.StringProperty(required=True)
	start_dt = db.DateTimeProperty(required=True)
	end_dt = db.DateTimeProperty(required=True)
	address = db.PostalAddressProperty()
	lat_long = db.GeoPtProperty()
	description = db.StringProperty(multiline=True)
	fb_link = db.LinkProperty()
	price = db.IntegerProperty()
	merch = db.StringListProperty()
	number_attending = db.IntegerProperty()


class EventSignup(db.Model):

	user = db.ReferenceProperty(Player, collection_name='events')
	event = db.ReferenceProperty(TMDEvent, collection_name='users')
	dt = db.DateTimeProperty(auto_now_add=True)
	paid = db.BooleanProperty(default=False)
	checkout_order_id = db.StringProperty()	
	
	## Merchandising !!
	ordered_map = db.BooleanProperty(default=False)
	ordered_rations = db.BooleanProperty(default=False)



class TMDHandler(webapp.RequestHandler):
	
	@webapp.cached_property
	def jinja2(self):
		return jinja2.get_jinja2(app=self.app)
		
	@webapp.cached_property
	def session(self):
		return self.session_store.get_session()
		
	def dispatch(self):
		# Resolve session store
		self.session_store = sessions.get_store(request=self.request)
		
		try:
			# Dispatch request
			webapp.RequestHandler.dispatch(self)
		finally:
			# Save session after request is dispatched
			self.session_store.save_sessions(self.response)
	
	def generateSession(self):
		character_pool = string.ascii_letters + string.digits
		self.session['sid'] = '-'.join([reduce(lambda x, y: x+y, [random.choice(character_pool) for i in range(0, 8)]) for igroup in range(0, 8)])
		self.session['token'] = hashlib.sha256(self.session['sid']+os.environ['REMOTE_ADDR']).hexdigest()
		self.session['addr'] = os.environ['REMOTE_ADDR']
		self.session['timestamp'] = datetime.datetime.now().isoformat()
		
	def render(self, template, context={}, **kwargs):
		
		baseContext = {
			
			'link': self.url_for,
			'user': {
				'is_admin': users.is_current_user_admin()
			}
		
		}
		
		if len(kwargs) > 0:
			for k, v in kwargs.items():
				context[k] = v
				
		for k, v in baseContext.items():
			context[k] = v
			
		#self.response.write(slimmer.html_slimmer(self.jinja2.render_template(template, **context)))
		self.response.write(self.jinja2.render_template(template, **context))


class MainPage(TMDHandler):

	def get(self):

		if 'sid' not in self.session:
			self.generateSession()
		
		# Error messaging
		fail = self.request.get('fail', False)
		success = self.request.get('success', False)

		alert = False
		alert_type = False

		if any([fail, success]):

			if fail:
				alert_type = 'fail'
			else:
				alert_type = 'success'
				
			if fail is not False:
				fail = self.request.get('reason')
				if fail == 'unknown':
					alert = 'An unknown error occurred. Please try again later.'
				elif fail == 'paypal_invalid':
					alert = 'The PayPal verification you provided was invalid. Please try again.'
			elif success is not False:
				alert = 'Success! You have been registered.'
		
		
		# Hit tracker for guerilla marketing campaign	
		s = self.request.get('cm_source', False)
		m = self.request.get('cm_medium', False)
		l = self.request.get('cm_location', False)
		g = self.request.get('cm_group', False)
		
		if any([s, m, l, g]):
			
			h = AdHit()
			h.source = s
			h.medium = m
			h.location = l
			h.group = g
			
			h_key = h.put()
			
			logging.info('NEW HIT: '+str(h_key))
		
		# Check if dev for Checkout
		checkout_cfg = config.config.get('google.checkout')
		if checkout_cfg['sandbox'] == True:
			sandbox = 'true'
			mid = checkout_cfg['sandbox_mid']
		else:
			sandbox = 'false'
			mid = checkout_cfg['mid']
		
		session_id = urllib.quote(str(base64.b64encode(self.session['sid'])))
		session_token = self.session['token']
		session_csrf = hashlib.sha512(self.session['sid']+self.session['token']).hexdigest()

		self.render('registration.html', alert=alert, alert_type=alert_type, step=1, sandbox=sandbox, checkout_mid=mid, sid=session_id, token=session_token, csrf=session_csrf, environ=os.environ, source=s, medium=m, location=l, group=g)
		
	def post(self):
		logging.info('POST RECEIVED AT LANDING: '+str(self.request))
		self.get()
		


class RegisterPlayerAJAX(TMDHandler):

	def post(self):

		sid = self.request.get('sid')
		token = self.request.get('token')
		csrf = self.request.get('csrf')
		email = self.request.get('email')
		age = self.request.get('age')
		fb_profile = self.request.get('fb_profile')
		event = self.request.get('event')

		# Name search ninja magic
		full_name = str(self.request.get('full_name'))
		names = full_name.split(' ') # String list of all names
		last_name = names[-1]
		first_name = names[0]
		
		# check for FB
		if fb_profile == 'true':
			fb = json.loads(self.request.get('fb'))
		else:
			fb = None
		
		# First, the new Player (user, not game player!!)
		p = Player(key_name=email)
		p.full_name = full_name
		p.first_name = first_name
		p.last_name = last_name
		p.names = names
		p.email = str(email)
		p.age = str(age)
		if fb_profile == 'true':
			p.fb = True
			p.fb_id = fb['id']
			p.fb_username = fb['username']
			p.gender = fb['gender']
		p.refer = self.request.get('refer')
		p.previous_game = self.request.get('lastgame')
		p.smartphone = self.request.get('smartphone')

		p_key = p.put()
		
		logging.info('PUT PLAYER: '+str(p_key))

		#success = {'status': 'success', 'player': {'key': str(p_key)}, 'token': self.request.get('token')}
		#logging.info('RETURNING SUCCESS: '+json.dumps(success))

		# Second, create the event signup marker
		ev = db.get(str(event))
		es = EventSignup(ev, key_name=str(p_key))
		es.user = p
		es.event = ev

		es_key = es.put()

		logging.info('PUT EVENT SIGNUP: '+str(es_key))

		# Third, queue a task to send a confirmation email
		send_confirmation = taskqueue.Task(method='GET', url='/_confirmRegistration', params={'p_key': str(p_key)})
		t_key = send_confirmation.add('mail')
		logging.info('ENQUEUING TASK: '+str(t_key))

		# Fourth and last, render the callback page
		self.render('confirmation2.html', first_name=str(first_name).upper(), email=email)
		

class Checkout(TMDHandler):
	
	def post(self):

		logging.info('PREPARE CHECKOUT REQUEST!')

		rations_package = self.request.get('rations_package', 'false')
		game_map = self.request.get('game_map', 'false')
		user_key = self.request.get('user_key')
		
		logging.info('USERKEY: '+str(user_key))
		
		context = {}
		
		subtotal = 5
		if rations_package == 'true':
			subtotal += 5
			context['rations_package'] = True
		if game_map == 'true':
			subtotal += 3
			context['game_map'] = True
			
		if config.debug:
			continue_baseurl = 'http://localhost:8080/success?'
		else:
			continue_baseurl = 'https://survive-sac.appspot.com/success?'
			
		context['sid'] = base64.b64encode(self.session['sid'])
		context['token'] = self.session['token']
		context['user_key'] = user_key
			
		context['continue_url'] = continue_baseurl+urllib.urlencode({'tmd_session': json.dumps({'sid': base64.b64encode(self.session['sid']), 'token': self.session['token'], 'u': user_key})})
		api_request = self.jinja2.render_template('snippets/checkout_api_request.xml', **context)
		
		logging.info('GENERATED API REQUEST: '+str(api_request))
		
		if config.config['google.checkout']['sandbox'] is True:
			hmac_sig = hmac.new(config.config['google.checkout']['sandbox_mkey'], api_request, hashlib.sha1)
		else:
			hmac_sig = hmac.new(config.config['google.checkout']['mkey'], api_request, hashlib.sha1)
			
		b64_hmac_sig = base64.b64encode(hmac_sig.digest())
		b64_api_request = base64.b64encode(api_request)
		checkout_request = {'hmac': str(b64_hmac_sig), 'request': str(b64_api_request)}
		
		self.response.write(json.dumps(checkout_request))
		
	
			
class CheckoutCallback(TMDHandler):
	
	def post(self):
		
		m = minidom.parseString(self.request.body)

		# Get Session ID, Token, & User Key
		session_id = m.getElementsByTagName('session-id')[0].childNodes[0].data
		session_token = m.getElementsByTagName('session-token')[0].childNodes[0].data
		user_key = m.getElementsByTagName('user-key')[0].childNodes[0].data
		order_num = m.getElementsByTagName('google-order-number')[0].childNodes[0].data
		
		k = db.Key(user_key)
		player = db.get(k)
		player.paid = True
		p_key = player.put()
		
		o = CheckoutOrder(player, key_name=order_num)
		o.order_id = order_num
		o.status = 'queued'
		o.player = player
		o_key = o.put()
		
		notify_page = taskqueue.Task(method='GET', url='/_notifySuccess', params={'token': str(session_token)}, countdown=5)
		notify_page.add('notify')
		
		confirmation_email = taskqueue.Task(name=hashlib.md5(player.email).hexdigest(), method='GET', url='/_sendConfirmationEmail', params={'ukey': str(p_key), 'okey': str(o_key)})
		confirmation_email.add('mail')
		
		self.response.out.write('OK')


class Success(TMDHandler):

	def get(self):



		self.render('confirmation2.html')
		
		
class NotifyClientOfSuccess(TMDHandler):
	
	def get(self):
		session_token = self.request.get('token')
		logging.info('Session token: '+str(session_token))
		channel.send_message(session_token, json.dumps({'status': 'success', 'activated': True}))
		
		
class SendSuccessEmail(TMDHandler):
	
	def get(self):
		
		user_key = self.request.get('ukey')
		order_key = self.request.get('okey')
		
		try:
			user = db.get(db.Key(user_key))
			order = db.get(db.Key(order_key))
		except Exception, e:
			logging.error('Error pulling user or order: '+str(e))
			raise
		
		else:
			logging.info('EMAIL NOTIFICATION')
			logging.info('user: '+str(user)+' at key '+str(user_key))
			logging.info('order: '+str(order)+' at key '+str(order_key))
		
			confirmation_email = mail.EmailMessage(
			
				to=user.full_name+' <'+user.email+'>',
				sender='Notifier Kitteh <robot.kitty@providenceclarity.com>',
				subject='Confirming your SurviveSac ticket order',
				html=self.jinja2.render_template('snippets/confirmation_email.html', **{'user': user, 'order': order})
		
			)
		
			logging.info('confirmation_email: '+str(confirmation_email))
			
			try:
				confirmation_email.send()
			except Exception, e:
				logging.error('Error sending confirmation email: '+str(e))
				raise


class ConfirmRegistration(TMDHandler):

	def get(self):

		p_key = self.request.get('p_key')

		try:
			player = db.get(db.Key(p_key))
		except Exception, e:
			logging.error('Error registering player: '+str(e))
			raise
		
		else:
			logging.info('EMAIL NOTIFICATION')
			logging.info('player: '+str(player.full_name)+' at key '+str(p_key))
			logging.info('email: '+str(player.email))

			confirmation_email = mail.EmailMessage(
				
				to=player.full_name+' <'+player.email+'>',
				sender='Notifier Kitteh <robot.kitty@providenceclarity.com>',
				subject='Confirming your survive.sac registration',
				html=self.jinja2.render_template('snippets/confirmation_email.html', **{'user': player})

			)

			logging.info('confirmation_email: '+str(confirmation_email))

			try:
				confirmation_email.send()
			except Exception, e:
				logging.error('Error sending confirmation email: '+str(e))
				raise
			
		
class Info(TMDHandler):
	
	def get(self):
		
		self.render('info.html')
		
		
class FBPageTab(TMDHandler):
	
	def get(self):
		return None
		
		
class FBApp(TMDHandler):
	
	def get(self):
		return None


class GamedayReg(TMDHandler):
	
	def get(self):
		return self.register_player_or_form()

	def post(self):
		return self.register_player_or_form()
	
	def register_player_or_form(self):

		if 'name' in self.request.params:

			p = GamePlayer()
			p.name = self.request.get('name')
			p.email = self.request.get('email')
			p.age = self.request.get('age')
			p.previous = self.request.get('previous')
			
			p_key = p.put()
			p_id = p_key.id()
			
			if isinstance(p_key, db.Key):
				
				self.render('gdreg.html', register='true', player_number=p_id)
			
			else:
				
				self.render('gdreg.html', fail='true')
		
		else:
			self.render('gdreg.html')


class GamedayCheckIn(TMDHandler):
	
	def get(self):
		return self.checkin_player_or_form()
	
	def post(self):
		return self.checkin_player_or_form()
	
	def checkin_player_or_form(self):
		
		if 'player_number' in self.request.params:

			pNum = self.request.get('player_number', False)
			cPt = self.request.get('checkpoint', False)
			
			c = CheckIn()
			c.player = pNum
			c.checkpoint = cPt
			c_key = c.put()
		
			if isinstance(c_key, db.Key):
				
				self.render('checkin.html', checkin='true', player_number=pNum, checkpoint=cPt)
							
			else:
				
				self.render('checkin.html', fail='true')

		else:
			self.render('checkin.html')



class LookupPlayer(TMDHandler):

	def get(self):

		player_num = self.request.get('pid', None)

		if player_num is not None:
			try:
				player = GamePlayer.get_by_id(int(player_num))
				assert player != None
			except ValueError, e:
				self.render('stats.html', player=False, notice=True, error='Please input a number only.')
			except AssertionError, e:
				self.render('stats.html', player=False, notice=True, error='No player found at ID "%s".' % str(player_num))
			else:
				self.render('stats.html', player=player, notice=False)
		else:
			self.render('stats.html', player=False, notice=False)


class Admin(TMDHandler):
	
	def get(self):
		
		self.render('admin.html')


class WorkingPage(TMDHandler):

	def get(self):

		self.render('working.html')


class CreateEvent(TMDHandler):

	def get(self):

		self.render('eventify.html')

	def post(self):

		name = self.request.get('name')
		start = datetime.datetime.strptime(self.request.get('start'), "%m/%d/%Y %H:%M")
		end = datetime.datetime.strptime(self.request.get('end'), "%m/%d/%Y %H:%M")

		ev_kn = str(slugify(name))
		logging.info("SLUGIFED KEYNAME: "+str(ev_kn))

		ev = TMDEvent(key_name=ev_kn, name=name, start_dt=start, end_dt=end)
		#ev.address = self.request.get('address', None)
		ev.description = self.request.get('desc', None)
		ev.fb_link = db.Link(str(self.request.get('fb_link')))
		#ev.price = self.request.get('price', None)
		#ev.merch = self.request.get('merch', None)
		#ev.image = self.request.get('image', None)
		#ev.lat_long = self.request.get('lat_long', None)

		ev_key = ev.put()
		logging.info("NEW EVENT CREATED: "+str(name)+" WITH KEY "+str(ev_key))

		self.render('eventify.html', success=True, e_name=name, e_start=start, e_end=end)


class ConvertToGamePlayer(TMDHandler):

	def get(self):
		return self.convert_or_form()
	
	def post(self):
		return self.convert_or_form()
	
	def convert_or_form(self):

		if 'player_key' in self.request.params:

			email = self.request.get('email')

			player = Player.get_by_key_name(email, parent=None)

			if player is not ['None', '']:

				gP = GamePlayer()
				gP.name = player.name
				gP.age = player.age
				
				gP_key = gP.put()
				gP_id = gP_key.id()

				if isinstance(gP_key, db.Key):
				
					self.render('convertify.html', register='true', player_number=p_id)
			
				else:
					
					self.render('convertify.html', fail='true')
			
			else:
				self.render('convertify.html')


class CountDownPage(TMDHandler):

	def get(self):
		return self.countdown()

	def post(self):
		return self.countdown()

	def countdown(self):
		
		self.render('index.html')
				

def generate_player_stats(checkin):

	# Get player stats entity by player key, if there is one
	try:
		gameday_player = GamePlayer.get_by_id(int(checkin.player))

		if gameday_player is None:
			logging.warning('Gameday player at checkin key "'+str(checkin.key())+'" is invalid (referenced player ID was "'+str(checkin.player)+'".')
		
		else:
			## Pull player stats by GamePlayer key, if it already exists
			player_stats = PlayerStats.get_by_key_name(str(gameday_player.key()))
			
			if player_stats is None: ## If the playerstats entity doesn't exist yet...
				## Create the playerstats entity, with the gameday_player key as the key name
				player_stats = PlayerStats(key_name=str(gameday_player.key()))

			## Add this checkin point key to the checkins completed list
			player_stats.checkins_completed = [i for i in player_stats.checkins_completed]+[str(checkin.key())]

			## Add this checkin to the completed checkins count
			player_stats.checkins_completed_count = player_stats.checkins_completed_count + 1

			yield op.db.Put(player_stats)
	except:
		logging.error("UNKNOWN ERROR OCCURRED: "+str(sys.exc_info()[0]))


def slugify(raw_string):

	# Let's try for one line!

	import string
	bad = string.punctuation
	return (''.join(map(lambda word: filter(lambda c: c not in bad, str(word).lower()), [w+str(' ') for w in raw_string.split()]))).strip().replace(' ','-')



TMD = webapp.WSGIApplication([
	routes.HandlerPrefixRoute('teammacdown.',[
		webapp.Route('/', name='landing', handler='CountDownPage'),
		webapp.Route('/success', name='checkout_callback', handler='Success'),
		webapp.Route('/checkout', name='checkout', handler='Checkout'),
		webapp.Route('/_register', name='create_player', handler='RegisterPlayerAJAX'),		
		webapp.Route('/_callback', name='checkout_callback', handler='CheckoutCallback'),
		webapp.Route('/info', name='info', handler='Info'),
		webapp.Route('/_notifySuccess', name='notify-success', handler='NotifyClientOfSuccess'),
		webapp.Route('/_fb/pagetab', name='fb-pagetab', handler='MainPage'),
		webapp.Route('/_fb/app.*', name='fb-app', handler='MainPage'),
		webapp.Route('/_sendConfirmationEmail', name='send-confirmation', handler='SendSuccessEmail'),
		webapp.Route('/_confirmRegistration', name='confirm-registration', handler='ConfirmRegistration'),
		webapp.Route('/_createEvent', name='create-event', handler='CreateEvent'),
		webapp.Route('/checkin', name='checkin', handler='GamedayCheckIn'),
		webapp.Route('/TMD', name='gameday-admin', handler='Admin'),
		webapp.Route('/data/lookup_player', name='lookup-player', handler='LookupPlayer'),
		webapp.Route('/gamedayreg', name='gamedayreg', handler='GamedayReg'),
		webapp.Route('/gdr_callback', name='player_callback', handler='GDRCallback'), 
		webapp.Route('/gdr_convert', name='convert-player', handler='ConvertToGamePlayer')
	])
], debug=True, config=config.config)
	
	
def main():
	run_wsgi_app(TMD)

if __name__ == '__main__':
	main()