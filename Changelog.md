Changelog for version 0.5
- Modify shop view to only show non-purchased items
	- Create database of purchase history 
	- Create arrays to support all shop items
	- Modify shop to use the arrays to show items
	- Modify arrays to grab data from database
	- Modify shop view to display purchase history
	- Modify shop item descriptions to grab from database	
- Create !buy command to purchase shop items
	- Create the command base 
	- Link command to database
	- Create error handling
- Minor improvements to other commands

Changelog for version 0.4
- Updated shutdown permissions
- Bot now recovers automatically after crash or shutdown
- Added !stp command for spending trait points
- Added !shop command for spending gold (Shop pages not yet populated)
- Added method to lock any multi-page bot messages to command caller
- Added stat assignment method to simplify !stp command

Changelog for version 0.3:
- Created AWS server host for hosting bot 24/7
- Created AWS RDS for hosting MySQL database 24/7
- Updated code for new login infomation
- Created <a href="https://top.gg/bot/621522560391053312">top.gg page</a>

Changelog for version 0.2:
- Added cooldown timer system
- Added new database for cooldownshttps://github.com/ryo5678/IdleDiscord/blob/main/TestBot.py
- Added message.delete() to heal command
- Added method to handle invocation errors when users have not been added to the database
