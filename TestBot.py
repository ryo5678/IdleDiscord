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


@bot.event
async def on_ready():
	print('We have logged in as {0.user}'.format(bot))
	
#-------------------------------------------------------------------------------
# ------------------------------ IDLE COMMAND ----------------------------------
#-------------------------------------------------------------------------------
	
# Start Adventure! Creates a new user row in SQL
@bot.command(pass_context = True)
async def idle(ctx):
	sql = "SELECT * FROM userstats WHERE user_id='{0.author}'".format(ctx)
	if exe(sql) == None:
		sql = "INSERT INTO userstats (user_id) VALUES ('{0.author}')".format(ctx)
		com(sql)
		await ctx.send('Your adventure begins!')
		await ctx.message.delete()
	else:
		await ctx.send('{0.author} already started their adventure.'.format(ctx))
		await ctx.message.delete()
		
#-------------------------------------------------------------------------------
# ------------------------------ DUEL COMMAND ----------------------------------
#-------------------------------------------------------------------------------

# Duel! User duels another user!	
@bot.command(pass_context = True)
async def duel(ctx, user: discord.Member = None):
	if user:
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
			await ctx.send("{0.mention}'s defense is too much for you! Get stronger before challenging them again.".format(user))
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
				await ctx.send('You defeated {0.mention}! You gain {1} gold.'.format(user,gold))
				await ctx.message.delete()
			else:
			# Post battle result
				await ctx.send('{0.author} slapped {1.mention} for {2} damage! They have {3} health remaining.'.format(ctx,user,dmg,hp))
				await ctx.message.delete()
	else:
		await ctx.send('Please tag a valid user')
		await ctx.message.delete()
@duel.error
async def duel_error(ctx, error):
	if isinstance(error, discord.ext.commands.BadArgument):
		await ctx.send('Could not recognize username')

#-------------------------------------------------------------------------------
# ------------------------------ GOLD COMMAND ----------------------------------
#-------------------------------------------------------------------------------
		
# Check gold value
@bot.command()
async def gold(ctx):
	sql = "SELECT gold FROM userstats WHERE user_id='{0.author}'".format(ctx)
	for x in exe(sql):
		gold = x
	await ctx.send('You have {0} gold in your pockets.'.format(gold))
	
#-------------------------------------------------------------------------------
# ------------------------------ EXP COMMAND ----------------------------------
#-------------------------------------------------------------------------------
		
# Check gold value
@bot.command()
async def exp(ctx):
	sql = "SELECT currentexp FROM userstats WHERE user_id='{0.author}'".format(ctx)
	for x in exe(sql):
		cexp = x
	sql = "SELECT exptolvl FROM userstats WHERE user_id='{0.author}'".format(ctx)
	for x in exe(sql):
		lexp = x
	lexp = lexp - cexp
	await ctx.send("{0.author} currently has {1} exp.'\n' Remaining exp to level up: {2}.".format(ctx,cexp,lexp))

#-------------------------------------------------------------------------------
# ------------------------------ FIGHT COMMAND ---------------------------------
#-------------------------------------------------------------------------------
	
# Fight! Begin the next level battle!	
@bot.command()
async def fight(ctx):
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
			await ctx.send("Level {0}'s defense is too much for you! Get stronger before challenging it again.".format(lvl))
		else:
			# Grab player's health
			sql = "SELECT health FROM userstats WHERE user_id='{0.author}'".format(ctx)
			for x in exe(sql):
				php = x
			if php - ldmg <= 0:
				# Update player's health value
				sql = "UPDATE userstats SET health = 0 WHERE user_id='{0.author}'".format(ctx)
				com(sql)
				await ctx.send("You received {0} damage. {1.author} has died!".format(ldmg,ctx))
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
					await ctx.send('{0.author} received {1} damage and dealt {2} damage. {3.author} has defeated level {4}! They gain {5} gold.'.format(ctx,ldmg,dmg,ctx,lvl,gold))
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
						await ctx.send("Level up! {0.author} is now level {1}. Stat point(s) gained: {2}".format(ctx,plvl,stat))
					else:
						# Give exp to player
						sql = "UPDATE userstats SET currentexp = currentexp + {0} WHERE user_id='{1.author}'".format(rexp,ctx)
						com(sql)
						# Get exp remaining to levelup
						lexp = mexp - (cexp + rexp)
						await ctx.send("{0.author} received {1} exp. Exp remaining to level up: {2}".format(ctx,rexp,lexp))
				else:
					# Grab player's health
					sql = "SELECT health FROM userstats WHERE user_id='{0.author}'".format(ctx)
					for x in exe(sql):
						php = x
					# Post damage result when not defeating level
					await ctx.send('{0.author} traded blows with level {1} for {2} damage! Level {1} has {3} health remaining. {0.author} received {4} damage and has {5} health remaining.'.format(ctx,lvl,dmg,lhp,ldmg,php))
					await ctx.message.delete()
	
#-------------------------------------------------------------------------------
# ------------------------------ HEAL COMMAND ----------------------------------
#-------------------------------------------------------------------------------

# Heal the player
@bot.command()
async def heal(ctx):
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
			await ctx.send("Your health is now full at {0}.".format(heal))
		else:
			# Heal player for regen amount
			sql = "UPDATE userstats SET health = {0} WHERE user_id='{1.author}'".format(heal,ctx)
			com(sql)
			await ctx.send("You healed for {0}. Your health is now at {1}.".format(rhp,heal))
	# Health is already full statement		
	else:
		await ctx.send("Your health is already full. Go take some damage first.")
			
	
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
