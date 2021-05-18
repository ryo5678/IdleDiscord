import discord
from discord.ext import commands
from discord.ext.commands import bot
import random
import mysql.connector
import math

idleDB = mysql.connector.connect(
  host="localhost",
  user="discordbot",
  password="t8jks0/63tn",
  database="idleplayerstats"
)

mc = idleDB.cursor(buffered=True)

intents = discord.Intents.default()
intents.members = True

bot = commands.Bot(command_prefix="!", activity=discord.Game(name="Work In Progress"), status=discord.Status.online)

# Method for cooldown timer code
def cooldown(ctx,timer):
	# Grab time when command was LAST used
	sql = "SELECT {0} FROM timers WHERE user_id='{1.author}'".format(timer,ctx)
	for y in exe(sql):
		otime = y
	if otime == None: return 99999
	# Grab current time
	sql = "SELECT CURRENT_TIMESTAMP"
	for x in exe(sql):
		ctime = x
	sql = "SELECT TIMESTAMPDIFF(SECOND,'{0}','{1}')".format(ctime,otime)
	for x in exe(sql):
		dtime = x
	dtime = -1 * dtime
	return dtime
		
# Method for cooldown reset code
def resetcooldown(ctx,timer):
		# Grab current time
		sql = "SELECT CURRENT_TIMESTAMP"
		for x in exe(sql):
			time = x
		sql = "UPDATE timers SET {0} = '{1}' WHERE user_id='{2.author}'".format(timer,time,ctx)
		com(sql)	

# Method to choose cooldown response
def cooldown_response(dtime):
	# Check if hours left
	if dtime > 3600:
		hours = math.floor(dtime/3600)
		minutes = math.floor((dtime%3600)/60)
		seconds = (dtime%3600)%60
		return ("Please wait {0} hours {1} minutes and {2} seconds before trying again.\n".format(hours,minutes,seconds))
	else:
		# Check if minutes left
		if dtime > 60:
			minutes = math.floor(dtime/60)
			seconds = dtime%60
			return ("Please wait {0} minutes and {1} seconds before trying again.\n".format(minutes,seconds))
		else:
			# Check if seconds left
			return ("Please wait {0} seconds before trying again.\n".format(dtime))
	
# Method to run execute commands and save space
def exe(sql):
	mc.execute(sql)
	mr = mc.fetchone()
	return mr

# Method to run database commits and save space
def com(sql):
	mc.execute(sql)
	idleDB.commit()
	
# Method to calculate stat points given on levelup
def stat_reward(plvl):
	stat = int(math.ceil((plvl * 10) / 50))
	return stat
	
# Method to calculate exp required for next level
def next_expgoal(plvl):
	goal = int((plvl * 20) ** 1.1)
	return goal
	
# Method to check if player is in database
def is_player(ctx):
	# Check if user already exists
	sql = "SELECT * FROM userstats WHERE user_id='{0.author}'".format(ctx)
	if exe(sql) == None:
		return ("{0.author} please type !idle before using this command.".format(ctx))

@bot.event
async def on_ready():
	print('We have logged in as {0.user}'.format(bot))
	
#-------------------------------------------------------------------------------
# ------------------------------ IDLE COMMAND ----------------------------------
#-------------------------------------------------------------------------------
	
# Start Adventure! Creates a new user row in SQL
@bot.command(pass_context = True)
async def idle(ctx):
		# Check if user already exists
		sql = "SELECT * FROM userstats WHERE user_id='{0.author}'".format(ctx)
		if exe(sql) == None:
			# Add user to database
			sql = "INSERT INTO userstats (user_id) VALUES ('{0.author}')".format(ctx)
			com(sql)
			sql = "INSERT INTO timers (user_id) VALUES ('{0.author}')".format(ctx)
			com(sql)
			await ctx.send('Your adventure begins!\n')
			await ctx.message.delete()
		else:
			await ctx.send('{0.author} already started their adventure.\n'.format(ctx))
			await ctx.message.delete()
		
#-------------------------------------------------------------------------------
# ------------------------------ DUEL COMMAND ----------------------------------
#-------------------------------------------------------------------------------

# Duel! User duels another user!	
@bot.command(pass_context = True)
async def duel(ctx, user: discord.Member = None):
	if user:
		# Check if first time using command
		a = "duel"
		# Check for cooldown
		dtime = cooldown(ctx,a)
		if dtime <= 14400:
			dtime = 14400 - dtime
			await ctx.send(cooldown_response(dtime))
			await ctx.message.delete()
		else:
			# Set new time for cooldown
			resetcooldown(ctx,a)
			# Grab attackers damage stat
			sql = "SELECT damage FROM userstats WHERE user_id='{0.author}'".format(ctx)
			for x in exe(sql):
				atk = x
			# Grab defeners defense stat
			sql = "SELECT defense FROM userstats WHERE user_id='{0}'".format(user)
			for y in exe(sql):
				dfen = y
			# Assign the damage outcome
			dmg = random.randint(1,10) + atk - dfen
			if dmg < 0:
				await ctx.send("{0.mention}'s defense is too much for you!\n Get stronger before challenging them again.\n".format(user))
			else:
				# Update defenders health value
				sql = "UPDATE userstats SET health = health - {0} WHERE user_id='{1}'".format(dmg,user)
				com(sql)
				# Grab defenders new health value
				sql = "SELECT health FROM userstats WHERE user_id='{0}'".format(user)
				for z in exe(sql):
					hp = z
				if hp <= 0:
					# Reset defenders health to 100
					sql = "UPDATE userstats SET health = 100 WHERE user_id='{0}'".format(user)
					com(sql)
					gold = random.randint(1,20)
					# Give gold to attacker
					sql = "UPDATE userstats SET gold = gold + {0} WHERE user_id='{1.author}'".format(gold,ctx)
					com(sql)
					await ctx.send('You defeated {0.mention}! You gain {1} gold.\n'.format(user,gold))
					await ctx.message.delete()
				else:
					# Post battle result
					await ctx.send('{0.author} slapped {1.mention} for {2} damage!\n They have {3} health remaining.\n'.format(ctx,user,dmg,hp))
					await ctx.message.delete()
	else:
		await ctx.send('Please tag a valid user.\n')
		await ctx.message.delete()
@duel.error
async def duel_error(ctx, error):
	if isinstance(error, discord.ext.commands.CommandInvokeError):
		await ctx.send(is_player(ctx))
		await ctx.message.delete()
	if isinstance(error, discord.ext.commands.BadArgument):
		await ctx.send('Could not recognize username.\n')
		await ctx.message.delete()

#-------------------------------------------------------------------------------
# ------------------------------ GOLD COMMAND ----------------------------------
#-------------------------------------------------------------------------------
		
# Check gold value
@bot.command()
async def gold(ctx):
	a = "gold"
	# Check for cooldown
	dtime = cooldown(ctx,a)
	if dtime <= 60:
		dtime = 60 - dtime
		await ctx.send(cooldown_response(dtime))
		await ctx.message.delete()
	else:
		# Set new time for cooldown
		resetcooldown(ctx,a)
		# Grab player gold value
		sql = "SELECT gold FROM userstats WHERE user_id='{0.author}'".format(ctx)
		for x in exe(sql):
			gold = x
		await ctx.send('You have {0} gold in your pockets.\n'.format(gold))
		await ctx.message.delete()
@gold.error
async def gold_error(ctx, error):
	if isinstance(error, discord.ext.commands.CommandInvokeError):
		await ctx.send(is_player(ctx))
		await ctx.message.delete()
	
#-------------------------------------------------------------------------------
# ------------------------------ EXP COMMAND ----------------------------------
#-------------------------------------------------------------------------------
		
# Check exp value
@bot.command()
async def exp(ctx):
	# Check if first time using command
	a = "exp"
    # Check for cooldown
	dtime = cooldown(ctx,a)
	if dtime <= 60:
		dtime = 60 - dtime
		await ctx.send(cooldown_response(dtime))
		await ctx.message.delete()
	else:
		# Set new time for cooldown
		resetcooldown(ctx,a)
		# Get current exp value
		sql = "SELECT currentexp FROM userstats WHERE user_id='{0.author}'".format(ctx)
		for x in exe(sql):
			cexp = x
		# Get exp left to level up
		sql = "SELECT exptolvl FROM userstats WHERE user_id='{0.author}'".format(ctx)
		for x in exe(sql):
			lexp = x
		# Post exp info to player
		lexp = lexp - cexp
		await ctx.send("{0.author} currently has {1} exp.\n Remaining exp to level up: {2}.\n".format(ctx,cexp,lexp))
@exp.error
async def exp_error(ctx, error):
	if isinstance(error, discord.ext.commands.CommandInvokeError):
		await ctx.send(is_player(ctx))
		await ctx.message.delete()
#-------------------------------------------------------------------------------
# ------------------------------ FIGHT COMMAND ---------------------------------
#-------------------------------------------------------------------------------
	
# Fight! Begin the next level battle!	
@bot.command()
async def fight(ctx):
		a = "fight"
		# Check for cooldown
		dtime = cooldown(ctx,a)
		if dtime <= 10:
			dtime = 10 - dtime
			await ctx.send(cooldown_response(dtime))
			await ctx.message.delete()
		else:
			# Set new time for cooldown
			resetcooldown(ctx,a)
			# Grab attackers damage stat
			sql = "SELECT damage FROM userstats WHERE user_id='{0.author}'".format(ctx)
			for x in exe(sql):
				atk = x
			# Grab the player's current opponent
			sql = "SELECT level FROM userstats WHERE user_id='{0.author}'".format(ctx)
			for x in exe(sql):
				lvl = x	
			# Grab opponent attack value
			sql = "SELECT atk FROM levels WHERE levelnum ='{0}'".format(lvl)
			for y in exe(sql):
				latk = y
			# Grab defeners defense stat
			sql = "SELECT def FROM levels WHERE levelnum='{0}'".format(lvl)
			for y in exe(sql):
				ldfen = y
			# Grab player's defense stat
			sql = "SELECT defense FROM userstats WHERE user_id='{0.author}'".format(ctx)
			for y in exe(sql):
				dfen = y
			# Assign damage to player
			ldmg = random.randint(1,5) + latk - dfen
			# Assign damage to level
			dmg = random.randint(1,10) + atk - ldfen
			if dmg <= 0:
				await ctx.send("Level {0}'s defense is too much for you!\n Get stronger before challenging it again.\n".format(lvl))
			else:
				# Grab player's health
				sql = "SELECT health FROM userstats WHERE user_id='{0.author}'".format(ctx)
				for x in exe(sql):
					php = x
				if php - ldmg <= 0:
					# Update player's health value
					sql = "UPDATE userstats SET health = 0 WHERE user_id='{0.author}'".format(ctx)
					com(sql)
					await ctx.send("You received {0} damage. {1.author} has died!\n".format(ldmg,ctx))
				else:
					# Update player's health value
					sql = "UPDATE userstats SET health = health - {0} WHERE user_id='{1.author}'".format(ldmg,ctx)
					com(sql)
					# Update defenders health value
					sql = "UPDATE userstats SET levelhp = levelhp - {0} WHERE user_id='{1.author}'".format(dmg,ctx)
					com(sql)
					# Grab defenders new health value
					sql = "SELECT levelhp FROM userstats WHERE user_id='{0.author}'".format(ctx)
					for z in exe(sql):
						lhp = z
					
					############## Defeat Opponent Section #################
					
					if lhp <= 0:
						rhp =  0
						# Reset levelhp to 0
						sql = "UPDATE userstats SET levelhp = {0} WHERE user_id='{1.author}'".format(rhp,ctx)
						com(sql)
						# Get the gold value from defeating opponent
						sql = "SELECT reward FROM levels WHERE levelnum='{0}'".format(lvl)
						for x in exe(sql):
							gold = x
						# Give gold to attacker
						sql = "UPDATE userstats SET gold = gold + {0} WHERE user_id='{1.author}'".format(gold,ctx)
						com(sql)
						# Get the exp reward from defeating opponent
						sql = "SELECT expreward FROM levels WHERE levelnum='{0}'".format(lvl)
						for x in exe(sql):
							rexp = x
						# Get current exp value from attacker
						sql = "SELECT currentexp FROM userstats WHERE user_id='{0.author}'".format(ctx)
						for x in exe(sql):
							cexp = x
						# Get exp to level
						sql = "SELECT exptolvl FROM userstats WHERE user_id='{0.author}'".format(ctx)
						for x in exe(sql):
							mexp = x
						# Post battle results
						await ctx.send('{0.author} received {1} damage and dealt {2} damage.\n {3.author} has defeated level {4}! They gain {5} gold.\n'.format(ctx,ldmg,dmg,ctx,lvl,gold))
						await ctx.message.delete()
						# Set the player's next opponent
						lvl = lvl + 1
						sql = "UPDATE userstats SET level = {0} WHERE user_id='{1.author}'".format(lvl,ctx)
						com(sql)
						# Set the player's next opponent health value
						sql = "SELECT hp FROM levels WHERE levelnum='{0}'".format(lvl)
						for x in exe(sql):
							temphp = x
						sql = "UPDATE userstats SET levelhp = {0} WHERE user_id='{1.author}'".format(temphp,ctx)
						com(sql)
						
						############ Level up conditional #############
						# Check if player is leveling up
						if (cexp + rexp) >= mexp:
							# Grab player current level
							sql = "SELECT playerlvl FROM userstats WHERE user_id='{0.author}'".format(ctx)
							for x in exe(sql):
								plvl = x
							# Set exp progress towards next level
							cexp = (cexp + rexp) - mexp
							# Give exp to player
							sql = "UPDATE userstats SET currentexp = {0} WHERE user_id='{1.author}'".format(cexp,ctx)
							com(sql)
							# Set exp required for next level
							mexp = next_expgoal(plvl)
							sql = "UPDATE userstats SET exptolvl = {0} WHERE user_id='{1.author}'".format(mexp,ctx)
							com(sql)
							# Get stat reward for level up
							stat = stat_reward(plvl)
							sql = "UPDATE userstats SET freestats = freestats + {0} WHERE user_id='{1.author}'".format(stat,ctx)
							com(sql)
							# Update player lvl
							plvl = plvl + 1
							sql = "UPDATE userstats SET playerlvl = {0} WHERE user_id='{1.author}'".format(plvl,ctx)
							com(sql)
							await ctx.send("Level up! {0.author} is now level {1}.\n Stat point(s) gained: {2}\n".format(ctx,plvl,stat))
						else:
							# Give exp to player
							sql = "UPDATE userstats SET currentexp = currentexp + {0} WHERE user_id='{1.author}'".format(rexp,ctx)
							com(sql)
							# Get exp remaining to levelup
							lexp = mexp - (cexp + rexp)
							await ctx.send("{0.author} received {1} exp.\n Exp remaining to level up: {2}\n".format(ctx,rexp,lexp))
					else:
						# Grab player's health
						sql = "SELECT health FROM userstats WHERE user_id='{0.author}'".format(ctx)
						for x in exe(sql):
							php = x
						# Post damage result when not defeating level
						await ctx.send('{0.author} traded blows with level {1} for {2} damage!\n Level {1} has {3} health remaining.\n {0.author} received {4} damage and has {5} health remaining.\n'.format(ctx,lvl,dmg,lhp,ldmg,php))
						await ctx.message.delete()
@fight.error
async def fight_error(ctx, error):
	if isinstance(error, discord.ext.commands.CommandInvokeError):
		await ctx.send(is_player(ctx))	
		await ctx.message.delete()
#-------------------------------------------------------------------------------
# ------------------------------ HEAL COMMAND ----------------------------------
#-------------------------------------------------------------------------------

# Heal the player
@bot.command()
async def heal(ctx):
	# Check if first time using command
	a = "heal"
	# Check for cooldown
	dtime = cooldown(ctx,a)
	if dtime <= 3600:
		dtime = 3600 - dtime
		await ctx.send(cooldown_response(dtime))
		await ctx.message.delete()
	else:
		# Set new time for cooldown
		resetcooldown(ctx,a)
		# Grab player's health value
		sql = "SELECT health FROM userstats WHERE user_id='{0.author}'".format(ctx)
		for x in exe(sql):
			chp = x
		# Grab player's health value
		sql = "SELECT maxhp FROM userstats WHERE user_id='{0.author}'".format(ctx)
		for y in exe(sql):
			mhp = y
		# Grab player's regen value
		sql = "SELECT regenhp FROM userstats WHERE user_id='{0.author}'".format(ctx)
		for z in exe(sql):
			rhp = z
		# Check if health is full
		if chp != mhp:
			heal = chp + rhp
			# Check if heal goes over max health
			if heal > mhp:
				# Set health to maximum
				heal = mhp
				sql = "UPDATE userstats SET health = {0} WHERE user_id='{1.author}'".format(heal,ctx)
				com(sql)
				await ctx.send('Your health is now full at {0}.\n'.format(heal))
				await ctx.message.delete()
			else:
				# Heal player for regen amount
				sql = "UPDATE userstats SET health = {0} WHERE user_id='{1.author}'".format(heal,ctx)
				com(sql)
				await ctx.send('You healed for {0}. Your health is now at {1}.\n'.format(rhp,heal))
				await ctx.message.delete()
		# Health is already full statement		
		else:
			await ctx.send('Your health is already full. Go take some damage first.\n')
			await ctx.message.delete()
@heal.error
async def heal_error(ctx, error):
	if isinstance(error, discord.ext.commands.CommandInvokeError):
		await ctx.send(is_player(ctx))	
		await ctx.message.delete()
	
#-------------------------------------------------------------------------------
# ----------------------------- SHUTDOWN COMMAND -------------------------------
#-------------------------------------------------------------------------------
					
# Shutdown the bot!
@bot.command()
@commands.has_permissions(administrator=True)
async def shutdown(ctx):
	await ctx.send('Bot is shutting down')
	await bot.change_presence(status=discord.Status.invisible)
	await bot.close()
	
bot.run('NjIxNTIyNTYwMzkxMDUzMzEy.XXmj_Q.IZjheAfUaPAOY-_qLZ6fTow-5cg')
