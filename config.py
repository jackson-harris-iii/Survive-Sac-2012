import os

debug = os.environ.get('SERVER_SOFTWARE', '').startswith('Dev')
config = {}

config['webapp2'] = {

	# Basic Config Values
	#'server_name': 'localhost:8080' if debug == True else 'spi.wirestone.staging.ext.providenceclarity.com',

	'apps_installed':[
		'tmd.survivesac' ## The FCM frontend responsible for making that data accessible and useful
	],

}
config['webapp2_extras.sessions'] = {

	'secret_key':'FOVBOIUB@#(*&#G@(*GBDOUGD&GEWOUOUHVoruho8108gvo#*G(G)))',
    'default_backend': 'datastore',
    'cookie_name':     'tmdsession',
    'session_max_age': None,
    'cookie_args': {
        'max_age':     86400,
        #'domain':      '*',
        'path':        '/',
        'secure':      False,
        'httponly':    False,
    }	

}
config['webapp2_extras.jinja2'] = {

	'template_path': 'templates', ## Root directory for template storage
	'compiled_path': None, ##  Compiled templates directory
	'force_compiled': False, ## Force Jinja to use compiled templates, even on the Dev server

	'environment_args': { ## Jinja constructor arguments
		'optimized': True,	## 
	    'autoescape': True, ## Global Autoescape. BE CAREFUL WITH THIS.
	    'extensions': ['jinja2.ext.autoescape', 'jinja2.ext.with_'],
	},

}


## SITE CONFIG ##
config['google.checkout'] = {

	'mid': '819057174593550',
	'mkey': 'GgYn-iuIrXO5w0Do9nggdg',
	'sandbox': False,
	'sandbox_mid': '720119283319381',
	'sandbox_mkey': 'UDNa8lG42dJ5g8YCaDojTg',

}