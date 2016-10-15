# Renault-Zoe-API
A basic API for getting information about your Renault Zoe Electric Vehicle.

All these API calls can be found by using the [Renault ZE Services website](https://www.services.renault-ze.com). I am indebted to [this German blog post](http://www.aironaut.ch/my-ze-online-abfragen/) for kicking off this work.  I'd also like to thank Renault for their ["esoteric" use of JavaScript](https://www.services.renault-ze.com/js/main.js)!

## What's Available?
This API is fairly limited, here's what you can do with it:

* See battery status, range, charging status.
* Start preconditioning
* See preconditioning history
* See and set charging schedule.
* See charging history

## Getting started

First, register with [Renault ZE Services](https://www.services.renault-ze.com/).  This will give you a username and password.

Secondly, you'll need to get your VIN and API token.  This can be obtained by posting the username and password to Renault.  For example:

```
curl \
   -H "Content-Type: application/json" \
   -X POST \
   -d '{"username":"you@example.com","password":"P4ssw0rd"}' \
   https://www.services.renault-ze.com/api/user/login`
```

This will get you back some JSON with your API tokens.  Here's an example:

```
{
	"token": "AAAA",
	"refresh_token": "BBBB",
	"user": {
		"id": "CCCC",
		"locale": "en_GB",
		"country": "GB",
		"timezone": "Europe/London",
		"email": "you@example.com",
		"first_name": "Terence",
		"last_name": "Eden",
		"phone_number": "+447700900123",
		"vehicle_details": {
			"timezone": "Europe/London",
			"VIN": "VVVV",
			"activation_code": "GGGG",
			"phone_number": "+447700900123"
		},
		"scopes": ["BATTERY_CHARGE_STATUS", 
				   "BATTERY_CHARGE_HISTORY", 
				   "BATTERY_CHARGE_REMOTE_ACTIVATION", 
				   "BATTERY_CHARGE_SCHEDULING", 
				   "AC_REMOTE_CONTROL", 
				   "BATTERY_CHARGE_LOWALERT"],
		"active_account": "DDDD",
		"associated_vehicles": [{
			"VIN": "VVVV",
			"activation_code": "GGGG",
			"user_id": "XXXX"
		}],
		"gdc_uid": "YYYY"
	}
}
```

## Battery Status

Let's start with the battery.  We need to use your `token` and `VIN` from above.

```
curl \
   -H "Authorization: Bearer AAAA" \
   "https://www.services.renault-ze.com/api/vehicle/VVVV/battery"
```

This gets us:
```
{
	"charging": false,
	"plugged": true,
	"charge_level": 100,
	"remaining_range": 124.0,
	"last_update": 1476472742000,
	"charging_point": "INVALID"
}
```

A few point to note. The `remaining_range` is in Kilometres.  The `last_update` is a Unix timestamp.

## Preconditioning

The Zoe can be set to warm-up or cool down depending on the last temperate you set in the car.  It will also blast the front window de-mister.  The process takes five minutes, so you can set it shortly before you need to set off.  Preconditioning will only work when the car's battery is above 45%.

### Precondition Now

```
curl \
   -H "Authorization: Bearer AAAA" \
   "https://www.services.renault-ze.com/api/vehicle/VVVV/air-conditioning"
```

This command does **not** return any value.  There is also no way to cancel the command remotely - you have to physically enter the car and turn it off.

### Precondition Later
If you know that you want to leave at a specific time, you can set the car to precondition at a set time.

```
curl \
   -H "Authorization: Bearer AAAA" \
   -H 'Content-Type: application/json;charset=UTF-8' \
   --data-binary '{"start":"1753"}' \
   'https://www.services.renault-ze.com/api/vehicle/VVVV/air-conditioning/scheduler'
```

As far as I can tell, the `start` time is when you want the conditioning to start - not when you want it to be finished.

There is **no way** to cancel a precondition.

### Preconditioning Last Status
Want to see if the preconditioning message was received by the car correctly?
```
curl \
   -H "Authorization: Bearer AAAA" \
   "https://www.services.renault-ze.com/api/vehicle/VVVV/air-conditioning/last"
```

This returns information about who or what sent the request:

```
{
	"date": 1476538293000,
	"type": "USER_REQUEST",
	"result": "SUCCESS"
}
```

### Preconditioning History
You can also see how often your car has been preconditioned.

```
curl \
   -H "Authorization: Bearer AAAA" \
   https://www.services.renault-ze.com/api/vehicle/VVVV/air-conditioning?begin=1016&end=1016
```

```
[{
	"date": 1476165377000,
	"type": "USER_REQUEST",
	"result": "ERROR"
}, {
	"date": 1476079325000,
	"type": "CAR_NOTIFICATION",
	"result": "ERROR"
}, {
	"date": 1476079270000,
	"type": "USER_REQUEST",
	"result": "SUCCESS"
}, {
	"date": 1476079266000,
	"type": "CAR_NOTIFICATION",
	"result": "SUCCESS"
}]
```

## Start Charging

You may have set your Zoe only to charge at specific times - perhaps to take advantage of cheap rate electricity.  You can override this by issuing the charge command.

```
curl \
   -H "Authorization: Bearer AAAA" \
   https://www.services.renault-ze.com/api/vehicle/VVVV/charge
```

Again, this won't return a response.  If your battery cannot be charged, you'll be notified via email or SMS depending on the preference you set up when you registered.

### Charging History

```
curl \
   -H "Authorization: Bearer AAAA" \
   https://www.services.renault-ze.com/api/vehicle/VVVV/charge/history?begin=1016&end=1016
```

The `begin` and `end` take `MMYY` as their arguments. That is, if you want October 2016 you need to use `1016`.

This returns an array, the most recent charging session at the top.

```
[{
	"date": 1476538527000,
	"type": "START_NOTIFICATION",
	"charging_point": "SLOW",
	"charge_level": 99,
	"remaining_autonomy": 119
}, {
	"date": 1476472727000,
	"type": "END_NOTIFICATION",
	"charging_point": "INVALID",
	"charge_level": 100,
	"remaining_autonomy": 124
}, {
	"date": 1476462129000,
	"type": "START_NOTIFICATION",
	"charging_point": "ACCELERATED",
	"charge_level": 34,
	"remaining_autonomy": 42,
	"remaining_time": 10500000
}]
```

The `remaining_autonomy` is, again, the range in **Km**.  The `remaining time` is expressed in *milliseconds*.  So `10500000` is the equivalent of 2 hours and 55 minutes.



## Notifications
You can use the website to set up notifications. For example, if there is a problem with your charge, Renault will send you an SMS.  This API call lets you see what notifications you have set up.

### Set Notifications
```
curl \
   -H "Authorization: Bearer AAAA" \
   -X PUT \
   -H 'Content-Type: application/json;charset=UTF-8' \
   --data-binary '{"battery_status":"EMAIL","charge_start":"SMS","charge_end":"SMS","charge_problem":"SMS","low_battery":"SMS","low_battery_reminder":"SMS","do_not_disturb":null}' \
   'https://www.services.renault-ze.com/api/vehicle/VVVV/settings/notification'  
```

You can change any of the options with `EMAIL` or `SMS`.

You can set a "do not disturb" option.  This will suppress all notifications during specific times.  Sadly, this is a fairly blunt instrument - you can only set one time which then is enforced every day.

In the above example, change `"do_not_disturb":null` to

`"do_not_disturb":{"start":"1710","end":"1811"}}'`

This will give you peace between 5:10pm and 6:11pm.

### See Notifications
You can use the website to set up notifications. For example, if there is a problem with your charge, Renault will send you an SMS.  This API call lets you see what notifications you have set up.

```
curl \
   -H "Authorization: Bearer AAAA" \
   https://www.services.renault-ze.com/api/vehicle/VVVV/settings/notification
```

This returns:
```
{
	"battery_status": "EMAIL",
	"charge_start": "NONE",
	"charge_end": "SMS",
	"charge_problem": "SMS",
	"low_battery": "SMS",
	"low_battery_reminder": "SMS",
	"do_not_disturb": null
}
```

## Charging Times
The Zoe's charging calendar is, sadly, crap.  You can say "charge between these times" but you can only have **one schedule per day**.  So if you only want the car to charge between 0300-0700 and 1800-2200 on Mondays - you're out of luck.

It also seemed to force me to set a schedule for *every* day.

This is a multi-stage process.

### Create a schedule

In this example, I'm setting the charging to be active on Monday from 0100 for 1 hour and 15 minutes.
All other days start at different times, but last only for 15 minutes.
All `start` times **must** be at 00, 15, 30, 45 minutes.  All `duration`s **must** be in increments of 15 minutes.

```
curl \
   -H 'Authorization: Bearer AAAA' \
   -X PUT \
   --data-binary '{"optimized_charge":false,"mon":{"start":"0100","duration":"0115"},"tue":{"start":"0200","duration":"0015"},"wed":{"start":"0300","duration":"0015"},"thu":{"start":"1600","duration":"0015"},"fri":{"start":"1900","duration":"0015"},"sat":{"start":"1400","duration":"0015"},"sun":{"start":"1200","duration":"0015"}}' \
   'https://www.services.renault-ze.com/api/vehicle/VVVV/charge/scheduler/offboard'
```

### View the schedule
Let's make sure the schedule has been sent correctly
```
curl \
   -H 'Authorization: Bearer AAAA' \
   'https://www.services.renault-ze.com/api/vehicle/VVVV/charge/scheduler/onboard' 
```

Returned - hopefully! - is the schedule:

```
{
	"enabled": false,
	"schedule": {
		"mon": {
			"start": "0100",
			"duration": "0115"
		},
		"tue": {
			"start": "0200",
			"duration": "0015"
		},
		"wed": {
			"start": "0300",
			"duration": "0015"
		},
		"thu": {
			"start": "1600",
			"duration": "0015"
		},
		"fri": {
			"start": "1900",
			"duration": "0015"
		},
		"sat": {
			"start": "1400",
			"duration": "0015"
		},
		"sun": {
			"start": "1200",
			"duration": "0015"
		}
	}
}
```

### Deploy the schedule
Be default, the schedule isn't activated.  It needs to be "deployed" in order to send it to the car.
```
curl \
   -H 'Authorization: Bearer AAAA' \
   -X POST \
   'https://www.services.renault-ze.com/api/vehicle/VVVV/charge/scheduler/offboard/deploy'

```

### Deactivate the schedule
If you deactivate the schedule then the car will charge whenever it is plugged in.
```
curl \
   -H 'Authorization: Bearer AAAA' \
   -X PUT \
   --data-binary '{"enabled":false}' \
   'https://www.services.renault-ze.com/api/vehicle/VVVV/charge/scheduler/onboard'
```

## That's all folks?
There are a few other API calls - mostly around registering and removing vehicles, and updating personal details.

## What's Missing?
Sadly, the Renault API is quite poor compared to BMW's API.  Here's what I'd *love* to see:

* Vehicle status - doors locked, headlights on.
* Efficiency - last journey, total.
* Mileage.
* Physical location.

## The End Result

https://twitter.com/edent_car/status/787387100396068864
