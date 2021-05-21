import discord
from discord.ext import commands
from discord.ext.commands import bot
import random
import mysql.connector
import math
import asyncio

idleDB = mysql.connector.connect(
  host="idlediscordbot.c5ezahjgi1hi.us-east-2.rds.amazonaws.com",
  port="3306",
  user="discordbot",
  password="t8jks0/63tn",
  database="IdleDiscord"
)

owner_id = 138752093308583936

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
		
# Method to assign a stat point
def assign_stat(ctx,sstat):
	sstat = sstat.lower()
	if sstat == "attack":
		sql = "UPDATE userstats SET damage = damage + 1 WHERE user_id='{0.author}'".format(ctx)
		com(sql)
		return ("You have increased your attack by 1 point.\n")
	else:
		if sstat == "defense":
			sql = "UPDATE userstats SET defense = defense + 1 WHERE user_id='{0.author}'".format(ctx)
			com(sql)
			return ("You have increased your defense by 1 point.\n")
		else:
			if sstat == "health":
				sql = "UPDATE userstats SET maxhp = maxhp + 5 WHERE user_id='{0.author}'".format(ctx)
				com(sql)
				return ("You have increased your maximum health by 5 points.\n")
			else:
				if sstat == "regeneration":
					sql = "UPDATE userstats SET regenhp = regenhp + 1 WHERE user_id='{0.author}'".format(ctx)
					com(sql)
					return ("You have increased your regeneration by 1 point.\n")
				else:
					return ("Please try again and select a correct stat point.\n")

# Method to fetch item_list for !shop
def get_items(ctx):
	# Current master list of items
	item_list = ["Wood Shield","Wood Sword","Wood Armor","Wood Ring","Stone Shield","Stone Sword","Stone Armor","Stone Ring",
	"Bronze Shield","Bronze Sword","Bronze Armor","Bronze Ring"]
	# Check if items are purchased
	sql = "SELECT * FROM purchased_items WHERE user_id='{0.author}'".format(ctx)
	items = exe(sql)
	# Grab all item prices
	sql = "SELECT * FROM shop_prices"
	prices = exe(sql)
	# Grab all item benefits
	sql = "SELECT * FROM shop_benefits"
	ben = exe(sql)
	# Loop to set values
	i = 1
	max = len(items)
	value_list = [""] * max
	while i <= max - 1:
		x = i-1
		value_list[x] = "Costs " + str(prices[x]) + " gold. Grants +" + ben[x] + "."
		i += 1
	# Loop through purchase history
	i = 1
	while i <= max - 1:
		x = i-1
		if items[i] == 1:
			item_list[x] = "~~" + item_list[i-1] + "~~"
			value_list[x] = "You have already purchased this item."
		i += 1
	return item_list, value_list
	
    
#-------------------------------------------------------------------------------
#------------------------------ ON READY EVENT ---------------------------------
#-------------------------------------------------------------------------------		

@bot.event
async def on_ready():
	print('We have logged in as {0.user}'.format(bot))
	
#-------------------------------------------------------------------------------
#------------------------------- IDLE COMMAND ----------------------------------
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
			sql = "INSERT INTO purchased_items (user_id) VALUES ('{0.author}')".format(ctx)
			com(sql)
			await ctx.send("{0.author.name}'s adventure begins!\n".format(ctx))
			await ctx.message.delete()
		else:
			await ctx.send('{0.author} already started their adventure.\n'.format(ctx))
			await ctx.message.delete()
		
#-------------------------------------------------------------------------------
#------------------------------- DUEL COMMAND ----------------------------------
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
#------------------------------- GOLD COMMAND ----------------------------------
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
#------------------------------- EXP COMMAND -----------------------------------
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
		await ctx.send("{0.author.name} currently has {1} exp.\n Remaining exp to level up: {2}.\n".format(ctx,cexp,lexp))
		await ctx.message.delete()
@exp.error
async def exp_error(ctx, error):
	if isinstance(error, discord.ext.commands.CommandInvokeError):
		await ctx.send(is_player(ctx))
		await ctx.message.delete()
		
#-------------------------------------------------------------------------------
#------------------------------- FIGHT COMMAND ---------------------------------
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
#------------------------------- HEAL COMMAND ----------------------------------
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
#--------------------------- SPEND TRAIT POINTS COMMAND ------------------------
#-------------------------------------------------------------------------------

# Spend trait points
@bot.command(pass_context = True)
async def stp(ctx, choice):
	# Check if player has a free stat to spend
	sql = "SELECT freestats FROM userstats WHERE user_id='{0.author}'".format(ctx)
	for x in exe(sql):
		cstat = x
	if cstat == 0:
		await ctx.send("Sorry {0.author}, you do not have any free stat points to spend.".format(ctx))
	else:
		# Check if first time using command
		a = "stp"
		# Check for cooldown
		dtime = cooldown(ctx,a)
		if dtime <= 1800:
			dtime = 1800 - dtime
			await ctx.send(cooldown_response(dtime))
			await ctx.message.delete()
		else:
			# Set new time for cooldown
			resetcooldown(ctx,a)
			sstat = choice
			await ctx.send(assign_stat(ctx,sstat))
			await ctx.message.delete()
@stp.error
async def stp_error(ctx, error):
	if isinstance(error, discord.ext.commands.CommandInvokeError):
		await ctx.send(is_player(ctx))
		await ctx.message.delete()	
	else:
		if isinstance(error, discord.ext.commands.MissingRequiredArgument):
			await ctx.send("Please specifiy a valid stat after !stp and try again.\nAttack, Defense, Health, Regeneration")
			await ctx.message.delete()

#-------------------------------------------------------------------------------
#----------------------------- UPGRADE SHOP COMMAND ----------------------------
#-------------------------------------------------------------------------------

# Purchase upgrades
@bot.command()
async def shop(ctx):
	# Check if first time using command
	a = "shop"
	# Check for cooldown
	dtime = cooldown(ctx,a)
	if dtime <= 180:
		dtime = 180 - dtime
		await ctx.send(cooldown_response(dtime))
		await ctx.message.delete()
	else:
		# Set new time for cooldown
		resetcooldown(ctx,a)
		# Clear command from chat
		await ctx.message.delete()
		# Initialize shop pages
		page_count = 0
		cpage = 1
	
		item_list, value_list = get_items(ctx)
		
		shop = discord.Embed(title="Items Shop", description="Purchase your upgrades here!", color=0xa81207)
		shop.add_field(name=item_list[0], value=value_list[0], inline=False)
		shop.add_field(name=item_list[1], value=value_list[1], inline=False)
		shop.add_field(name=item_list[2], value=value_list[2], inline=False)
		shop.add_field(name=item_list[3], value=value_list[3], inline=False)
		shop.add_field(name="\u200b",value='\nPage 1/3', inline=False)
		
		shop2 = discord.Embed(title="Items Shop", description="Purchase your upgrades here!", color=0xa81207)
		shop2.add_field(name=item_list[4], value=value_list[4], inline=False)
		shop2.add_field(name=item_list[5], value=value_list[5], inline=False)
		shop2.add_field(name=item_list[6], value=value_list[6], inline=False)
		shop2.add_field(name=item_list[7], value=value_list[7], inline=False)
		shop2.add_field(name="\u200b",value='\nPage {0}/{1}'.format(cpage,page_count), inline=False)
		
		shop3 = discord.Embed(title="Items Shop", description="Purchase your upgrades here!", color=0xa81207)
		shop3.add_field(name=item_list[8], value=value_list[8], inline=False)
		shop3.add_field(name=item_list[9], value=value_list[9], inline=False)
		shop3.add_field(name=item_list[10], value=value_list[10], inline=False)
		shop3.add_field(name=item_list[11], value=value_list[11], inline=False)
		shop3.add_field(name="\u200b",value='\nPage {0}/{1}'.format(cpage,page_count), inline=False)
		
		contents = [shop,shop2,shop3]
		page_count = len(contents)
	
		message = await ctx.send(embed=contents[cpage-1])
		# Add reactions for changing pages
		await message.add_reaction("\u2B05")
		await message.add_reaction("\u27A1")
		# Method for locking multi page bot messages to command caller
		def check(reaction,user):
			return user == ctx.author and str(reaction.emoji) in ["\u2B05", "\u27A1"]
		# Loop to keep shop open
		while True:
			try:
				# Timer and lock for shop
				reaction, user = await bot.wait_for("reaction_add", timeout=30, check=check)
				# Check for next page
				if str(reaction.emoji) == "\u27A1" and cpage != page_count:
					cpage += 1
					contents[cpage-1].set_field_at(4,name="\u200b",value='\nPage {0}/{1}'.format(cpage,page_count), inline=False)
					await message.edit(embed=contents[cpage-1])
					await message.remove_reaction(reaction, user)
				else:
					# Check for previous page
					if str(reaction.emoji) == "\u2B05" and cpage > 1:
						cpage -= 1
						contents[cpage-1].set_field_at(4,name="\u200b",value='\nPage {0}/{1}'.format(cpage,page_count), inline=False)
						await message.edit(embed=contents[cpage-1])
						await message.remove_reaction(reaction, user)
					else:
						# Prevent going past page limits
						await message.remove_reaction(reaction, user)
			# Conclude timer if player ignores or is done with shop
			except asyncio.TimeoutError:
				await message.delete()
				break
@shop.error
async def shop_error(ctx, error):
	if isinstance(error, discord.ext.commands.CommandInvokeError):
		await ctx.send(is_player(ctx))	
		await ctx.message.delete()

#-------------------------------------------------------------------------------
#------------------------------ BUY COMMAND ------------------------------------
#-------------------------------------------------------------------------------
				
# Purchase items from the shop!
@bot.command(pass_context = True)
async def buy(ctx, item1, item2):
	# Check if first time using command
	a = "buy"
	# Check for cooldown
	dtime = cooldown(ctx,a)
	if dtime <= 10:
		dtime = 10 - dtime
		await ctx.send(cooldown_response(dtime))
		await ctx.message.delete()
	else:
		# Set new time for cooldown
		resetcooldown(ctx,a)
		# Set item name
		item = item1.lower() + "_" + item2.lower()
		# Get requested item price
		sql = "SELECT {0} FROM shop_prices".format(item)
		for x in exe(sql):
			price = x
		# Get requested item benefit
		sql = "SELECT {0} FROM shop_benefits".format(item)
		for x in exe(sql):
			ben = x
		# Split benefit into stat value and type
		benefits = ben.split(' ',1)
		if benefits[1] == "max hp":
			benefits[1] = "maxhp"
		elif benefits[1] == "hp regen":
			benefits[1] = "regenhp"
		elif benefits[1] == "attack":
			benefits[1] = "damage"
		# Check if player has enough gold
		sql = "SELECT gold FROM userstats WHERE user_id='{0.author}'".format(ctx)
		for x in exe(sql):
			gold = x
		if gold - int(benefits[0]) < 0:
			await ctx.send("You do not have enough gold to purchase a {0} {1}.".format(item1,item2))
			await ctx.message.delete()
		else:
			# Update new gold value on purchase
			sql = "UPDATE userstats SET gold = gold - {0} WHERE user_id='{1.author}'".format(price,ctx)
			com(sql)
			# Update stat value
			stat = int(benefits[0])
			sql = "UPDATE userstats SET {0} = {0} + {1} WHERE user_id='{2.author}'".format(benefits[1],stat,ctx)
			com(sql)
			# Set purchase history
			sql = "UPDATE purchased_items SET {0} = 1 WHERE user_id='{1.author}'".format(item,ctx)
			com(sql)
			# Inform user
			benefits = ben.split(' ',1)
			await ctx.send("You have purchased {0} {1} and increased {2} by {3} points.\nGold remaining: {4}".format(item1,item2,benefits[1],stat,price))			
@buy.error
async def buy_error(ctx, error):
	if isinstance(error, discord.ext.commands.CommandInvokeError):
		# Check if user already exists
		sql = "SELECT * FROM userstats WHERE user_id='{0.author}'".format(ctx)
		if exe(sql) == None:
			await ctx.send("{0.author} please type !idle before using this command.".format(ctx))
			await ctx.message.delete()	
		else:
			# Invalid input message
			await ctx.send("Invalid item. Please make sure you use the command as follows:\n!buy Wood Shield or !buy wood shield")	
			await ctx.message.delete()		
	if isinstance(error, discord.ext.commands.MissingRequiredArgument):
		await ctx.send("Invalid usage. Please make sure you use the command as follows:\n!buy Wood Shield or !buy wood shield")	
		await ctx.message.delete()
		
		
		
#-------------------------------------------------------------------------------
#------------------------------ POST UPDATES COMMAND ---------------------------
#-------------------------------------------------------------------------------
				
# Future updates for bot!
@bot.command()
async def updates(ctx):
	# Check if first time using command
	a = "updates"
	# Check for cooldown
	dtime = cooldown(ctx,a)
	if dtime <= 3600:
		dtime = 3600 - dtime
		await ctx.send(cooldown_response(dtime))
		await ctx.message.delete()
	else:
		# Set new time for cooldown
		resetcooldown(ctx,a)
		with open('UpdateProgressReport.txt') as f:
			text = f.read()
		await ctx.send(text)
		await ctx.message.delete()
	
#-------------------------------------------------------------------------------
#------------------------------ SHUTDOWN COMMAND -------------------------------
#-------------------------------------------------------------------------------
				
# Shutdown the bot!
@bot.command()
@commands.is_owner()
async def shutdown(ctx):
	await ctx.message.delete()
	await ctx.send('Idle Discord is restarting. Sorry for the inconvenience.')
	await bot.change_presence(status=discord.Status.invisible)
	await bot.close()

bot.run('NjIxNTIyNTYwMzkxMDUzMzEy.XXmj_Q.IZjheAfUaPAOY-_qLZ6fTow-5cg')