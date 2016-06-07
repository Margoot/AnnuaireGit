#!/usr/bin/python

from pymysql import connect, err, sys
import pymysql.cursors

class Modele_Annuaire:
	"""
		Class Modele : Utilisation d'une base de donnée afin de pouvoir stocker les contacts. 
		Celle-ci contient les méthodes stuivantes : 
		- initialisation 
		- CreateDatabase : création d'une base de donnée
		- CreateTable : création d'une table dans la base de données 
		- GetColumns : récuperer les colonnes de notre table
		- executeCommand : définition de l'instruction d'execution afin de pouvoir executer notre requete 
					   	dans chaque fonction 
		- AddEntryToTable : fonction qui ajoute une ligne dans une table 
		- SearchInTable : recherche certains caractères dans une table 
		- SearchBar : rechercher dans le nom et le prénom (fonction pour la barre de recherche)
		- ModifyRow : modifier une ligne de la table 
		- DeleteEntry : supprimer une ligne de la table
		- ExportTable : exporter une table dans la base de donnée actuelle (celle-ci sera stockée dans le tmp)
		- ImportTable : importer une table dans la base de donnée actuelle (celle-ci pourra être importée si
						elle est enregistrée au préalable dans le tmp)
		Les attributs suivants : 
		- database : base de donnée actuelle
		- tableName : nom de la table 
		- user : nom de l'utilisateur 
		- password : mot de passe de l'utilisateur

		Du langage SQL est utilisé dans cette classe. 

	"""

	def __init__ (self,database,tableName , user, password):
		self.database = database
		self.tableName = tableName
		self.user = user
		self.password = password
		try:
			self.connexion = pymysql.connect(user = self.user, password = self.password, host = 'localhost', autocommit=True)
		except:
			print("Connection error")
		self.cursor = self.connexion.cursor()

	def CreateDatabase(self): 
		command = "USE " + self.database
		try:
			self.executeCommand("CREATE DATABASE IF NOT EXISTS %s DEFAULT CHARACTER SET 'utf8';" %self.database)
			self.executeCommand(command)
		except pymysql.MySQLError as e:
			print("Failed creating database: {}".format(e))
			self.executeCommand(command)

	def CreateTable(self):
		command = (
			" CREATE TABLE IF NOT EXISTS " + self.tableName + " ("
			" `Id` int AUTO_INCREMENT NOT NULL,"
			" `Name` varchar(20) NOT NULL,"
			" `FirstName` varchar(20) NOT NULL,"
			" `Telephone` varchar(30) NOT NULL,"
			" `Email` varchar(30),"
			" `Birthday` date,"
			" `Address` varchar(150),"
			" PRIMARY KEY (`Id`)"
			") ENGINE=InnoDB;")
		self.executeCommand(command)

	def GetColumns(self):
		return self.executeCommand("SELECT Name, FirstName FROM %s WHERE Name IS NOT NULL;" % (self.tableName))

	def executeCommand(self, command):
		print ("RUNNING COMMAND: " + command)

		try:
			self.cursor.execute(command)
		except pymysql.MySQLError as e:
			print (e)
		try:
			mess = self.cursor.fetchall()
			print (mess)
		except:
			mess = self.cursor.fetchone()
			print (mess)
		return mess

	def AddEntryToTable(self, name, firstname, tel, email, birthday, address,):
		command = " INSERT INTO " + self.tableName + " (Name,FirstName,Telephone,Email,Birthday,Address)"
		command += " VALUES ('%s', '%s', '%s', '%s', '%s', '%s' );" % (name,firstname,tel,email,birthday,address)
		self.executeCommand(command)

	def SearchInTable(self, name, firstname):
		command = "SELECT * FROM " + self.tableName + " WHERE Name LIKE '%%%s%%' OR FirstName LIKE '%%%s%%';" %(name, firstname)
		return self.executeCommand(command)

	def SearchBar(self, string):
		command = "SELECT Name, FirstName FROM " +self.tableName+ " WHERE Name LIKE '%%%s%%' OR FirstName LIKE '%%%s%%';" %(string, string)
		return self.executeCommand(command)

	def ModifyRow(self, nameChange, firstnameChange, telChange, emailChange, birthdayChange, addressChange, name, firstname):
		command = "UPDATE "+ self.tableName+ " SET Name='%s', FirstName='%s', Telephone='%s', Email='%s',Birthday='%s',Address='%s' WHERE Name='%s' AND FirstName='%s';" %(nameChange,firstnameChange, telChange, emailChange, birthdayChange, addressChange,name,firstname)
		self.executeCommand(command)

	def DeleteEntry(self, name, firstname ):
		command = "DELETE FROM " + self.tableName + " WHERE Name='%s' AND FirstName='%s';" %(name,firstname)  
		self.executeCommand(command)

	def ExportTable(self):
		command1 = ("GRANT FILE ON *.* TO 'root'@'localhost';")
		self.executeCommand(command1)
		command2 = (
			"SELECT * FROM " + self.tableName + " INTO OUTFILE '/tmp/tableDeBase.txt' FIELDS TERMINATED BY ';' ENCLOSED BY ':' LINES TERMINATED BY '$';")
		self.executeCommand(command2)

	def ImportTable(self,pathname):
		command =("LOAD DATA INFILE '%s' INTO TABLE %s FIELDS TERMINATED BY ';' ENCLOSED BY ':' LINES TERMINATED BY '$';") %(pathname,self.tableName)
		self.executeCommand(command)
 
	def __del__(self):
		"""
			fonction de cloture de la base de donnée à la fermeture du programme
 		"""
		self.cursor.close()
		self.connexion.close()
