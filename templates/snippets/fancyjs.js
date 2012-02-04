<script type="text/javascript">
/*
	function fillFacebookResponse(response)
	{
		console.log('facebook response', response);
		$('#facebookLogin').addClass('hidden');
		
		$('#fb_fullname').html(response.name);
		$('#facebookUser').removeClass('hidden');
		
		$('#name').attr('value', response.name).addClass('hidden');
		$('#email').attr('value', response.email).addClass('hidden');

		$('#fb_profile_username').val(response.username);
		$('#fb_profile_id').val(response.id);
		$('#fb_profile_gender').val(response.gender);
		$('#fb_profile').val('true');
	}
	
	function getRegistrantData()
	{
		if (Modernizr.localstorage)
		{
			var localstorage = window.localStorage || window.webkitLocalStorage || window.mozLocalStorage || window.oLocalStorage;
			var fields = null;
			try
			{
				fields = JSON.parse(localstorage.getItem('input_fields'));
			}
			catch (error)
			{
				fields = null;
			}
			
			var registrant = {};
			for (field_i in fields)
			{
				field = fields[field_i];
				registrant[field] = JSON.parse(localstorage.getItem('input:'+field.id));
			}
			return registrant;
		}
	}

	function advanceForm(event)
	{
		event.preventDefault();
		
		$('#registrationInput input, #registrationInput textarea').attr('disabled', 'disabled').addClass('disabled');
		$('#registerSubmit').removeClass('enabled').attr('value', 'SUBMITTING...').attr('disabled', 'disabled');
		
		$.ajax({
			
			url: 'http://{{ environ.SERVER_NAME }}:{{ environ.SERVER_PORT }}/_register',
			async: true,
			dataType: 'json',
			type: 'post',
			
			data: {
				sid: '{{ sid }}',
				token: '{{ token }}',
				csrf: '{{ csrf }}',
				name: $('#name').attr('value'),
				age: $('#age').attr('value'),
				email: $('#email').attr('value'),
				fb_profile: $('#fb_profile').val(),
				fb: JSON.stringify({
					id: $('#fb_profile_id').val(),
					username: $('#fb_profile_username').val(),
					gender: $('#fb_profile_gender').val()
				}),
				auth: false
			},
			
			success: function receiveRegisteredUser(response)
			{
				console.log('response', response);
				if (response.status == 'success')
				{
					//$('#step1').addClass('completed').removeClass('current').children('span').removeClass('arrowbox').addClass('checkbox');
					//$('#step2').addClass('current').animate({width: 120}).children('span').animate({opacity: 1}).addClass('iconbox arrowbox');
					
					//$('#next_trigger').click();
					//$('#paymentStep').animate({opacity: 1});
					
					window.redirect('/success');
					
					if (Modernizr.localstorage)
					{
						var localstorage = window.localStorage || window.webkitLocalStorage || window.mozLocalStorage || window.oLocalStorage;
						localstorage.setItem('userkey', response.player.key);
						$('#userKey').attr('value', response.player.key);
					}					
				}
				else
				{
					if (response.error.code == 'player_already_exists')
					{
						*/
						/*
						$('#email').attr('data-error', response.error.message).tipsy({
							
							delayIn: 400,
							fade: true,
							gravity: 'w',
							trigger: 'manual',
							title: 'data-error'
							
						}).tipsy('show');*/
						
						/*
						$('#registerSubmit').attr('value', 'NEXT ->');
						$('#email').animate({border: '1px solid red !important'}).removeAttr('disabled').removeClass('disabled').change(function enableButton()
						{
							$('#registerSubmit').removeAttr('disabled').removeClass('disabled').addClass('enabled');
						});
					}
				}
			},

			error: function registerUserAJAXError(error)
			{
				alert('error');
			}
			
		});
	}
	
	function shareEvent()
	{
		FB.ui(
		  {
		    method: 'send',
			name: 'Survive.Sacramento - Real life zombie survival!',
			link: 'http://tmd.labs.momentum.io'
		  },
		  function(response) {
		    if (response && response.post_id) {
		      alert('Post was published.');
		    } else {
		      alert('Post was not published.');
		    }
		  }
		);
	}
		
	function deauthorize()
	{
		FB.logout();
		$('#facebookUser').addClass('hidden').children('span');
		$('#facebookLogin').removeClass('hidden');
	}
	
	function initFB()
	{
		FB.init({
		   appId:'242878385764668', cookie:true, 
		   status:true, xfbml:true 
		});

		FB.Event.subscribe('auth.login', function(response) {
		        if (response.session) {
					FB.api('/me', function(response) {
						fillFacebookResponse(response);
					});			
		        }
	    });
	}
*/
	function initPage() {
			/*	
		$('#facebookLoginButton').click(function doLoginEvent()
		{
			FB.init({
			   appId:'242878385764668', cookie:true, 
			   status:true, xfbml:true 
			});

			FB.Event.subscribe('auth.login', function(response) {
			        if (response.session) {
						FB.api('/me', function(response) {
							fillFacebookResponse(response);
						});			
			        }
		    });
			try
			{
				FB.api('/me', function(user) {
					console.log('/me', user);
					if(user != null)
					{
						if(user.error == undefined)
						{
							fillFacebookResponse(user);					
						}
						else
						{
							FB.login(function (response){ console.log('FBLogin', response); }, {scope: 'email,sms,rsvp_event'});
						}
					}
					else
					{
						FB.login(function (response){ console.log('FBLogin', response); }, {scope: 'email,sms,rsvp_event'});
					}
				
				});
			}
			catch (error)
			{
				FB.login(function (response){ console.log('FBLogin', response); }, {scope: 'email,sms,rsvp_event'});
			}
		})
		*/
		$('input').focus(function clearIfDefault(){
			if($(this).attr('type') != 'submit')
			{
				$(this).val('');				
			}
		});
		
		$('input').change(function saveFormItem(){
			
			if(Modernizr.localstorage)
			{
				var itemkey = "input:"+$(this).attr('id');
				localstorage = window.localStorage || window.webkitLocalStorage || window.mozLocalStorage || window.oLocalStorage;

				var itemindex = null;
				localstorage.setItem(itemkey, JSON.stringify({id: $(this).attr('id'), name: $(this).attr('name'), value: $(this).val()}));
				
				try
				{
					itemindex = JSON.parse(localstorage.getItem('input_fields'));					
				}
				catch (error)
				{
					itemindex = null;
				}
				
				if (itemindex == null)
				{
					itemindex = [itemkey];
				}
				else
				{
					itemindex.push(itemkey);					
				}
				
				localstorage.setItem('input_fields', JSON.stringify(itemindex));
			}
			
		})
		
		$('textarea').focus(function clearIfDefault(){
			$(this).val('');
		});
		/*
		itemsInCart = [];
		cartSubtotal = 5.0;
		$('.addToCart').click(function addItemToCart()
		{
			$(this).animate({opacity: 0}, function showAdded()
			{
				$(this).addClass('hidden');
				$(this).parent().children('input').val('true');
				$(this).parent().children('.added').css({opacity: 0}).removeClass('hidden').animate({opacity: 1});
			})
			
			title = $(this).parent().attr('data-title');
			price = parseInt($(this).parent().attr('data-price'));
			cartSubtotal += price;
			$('#subtotal').animate({opacity: 0}, function ()
			{
				$('#subtotal').text(cartSubtotal).animate({opacity: 1});
			});
			itemsInCart.push({title: title, price: price});
			
		})
				
		*/
		
		$('#regFormAction input').change(function checkFormValid()
		{
			var valid = true;
			$('#regFormAction input').each(function doValidCheck(){

				input = $(this);
				if(input.attr('data-required') == 'true')
				{
					if(input.val() == input.attr('placeholder'))
					{
						valid = false;
					}					
				}					
				
			});
			
			if(valid != false)
			{
				$('#registerSubmit').removeAttr('disabled').removeClass('disabled').addClass('enabled');
			}
		});
		/*
		$('#cartSubmit').click(function submitCart(event)
		{
			event.preventDefault();
			$.ajax({
			
				url: $(this).parent().attr('action'),
				async: true,
				dataType: 'json',
				type: 'post',

				data: {
					game_map: $('#game_map').val(),
					rations_package: $('#rations_package').val(),
					user_key: $('#userKey').val(),
					sid: '{{ sid }}',
					csrf: '{{ csrf }}',
					token: '{{ token }}'
				},
				
				success: function cartForwardToCheckout(response)
				{
					console.log('cart response', response);
					$('#cart_encoded').val(response.request);
					$('#signature_encoded').val(response.hmac);
					$('#cartSubmit').addClass('hidden');
					$('#checkoutForm').removeClass('hidden');
				}
				
			});
		})*/
	}	
		
</script>