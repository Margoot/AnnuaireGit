#!/usr/bin/python

import modele_Annuaire, sys
from ui_Annuaire import Ui_Annuaire
from modele_Annuaire import Modele_Annuaire
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import QStringListModel

class Controller_Annuaire(QtWidgets.QMainWindow):
	"""Class Control = 
		Classe qui fait le lien entre la View et le Model. 
		Cette classe contient les méthodes suivantes : 
		- modifyContact : modifier les données d'un contact lorsqu'on clique sur le bouton modifier 
		- showDialog : afficher une boite de dialogue lorsque l'utilisateur veut créer un nouveau contact
		- mandatoryFields : champs obligatoire lorsque l'utilisateur veut entrer un contact. Il doit imperativement
					entrer le nom et le prénom afin de pouvoir cliquer sur le bouton "ok". 
		- showContact : afficher les contacts dans la QListWidget en permanance 
		- getData : obtenir les données d'un contact et enlever le "tuple d'un tuple"
		- update : clear la QListWidget et ré afficher les contacts avec les mises à jour de faites
		- delContact : supprimer un contact de la base de données.Cette action sera générée si l'utilisateur
		   appuie sur le bouton supprimer.
		- showDetail : afficher les détails de chaque contact sur le côté droit dans chaque champs respectif
		- searchContact : rechercher des contacts dans la barre de recherche. La recherche peut être validé en 
				  cliquant sur la loupe ou en appuyant sur la barre espace 
		- createContact : créer un nouveau contact dans la table. La boite de dialogue apparait si l'utilisateur
				  appuie sur le bouton nouveau contact
		- Import : importer une table dans la base de donnée actuelle (celle-ci pourra être importée si
		   elle est enregistrée au préalable dans le tmp). Cette action sera générée si l'utilisateur
		   appuie sur le bouton importer
		- Export : exporter une table dans la base de donnée actuelle (celle-ci sera stockée dans le tmp). Cette action sera générée si l'utilisateur appuie sur le bouton export
	"""
	
	def __init__(self, database, tableName, user, password):
		super(Controller_Annuaire, self).__init__()
		self.window = QtWidgets.QMainWindow()
		self.ui = Ui_Annuaire()
		self.ui.setupUi(self)
		self.dba = Modele_Annuaire(database, tableName, user, password)
		self.dba.CreateDatabase()
		self.dba.CreateTable()
		self.ui.searchBar.selectionChanged.connect(self.ui.searchBar.clear)
		self.ui.modifyContact.triggered['bool'].connect(self.ui.editMail.setEnabled)
		self.ui.modifyContact.triggered['bool'].connect(self.ui.editBirthday.setEnabled)
		self.ui.modifyContact.triggered['bool'].connect(self.ui.editName.setEnabled)
		self.ui.modifyContact.triggered['bool'].connect(self.ui.editFirstname.setEnabled)
		self.ui.modifyContact.triggered['bool'].connect(self.ui.editPhone.setEnabled)
		self.ui.modifyContact.triggered['bool'].connect(self.ui.editAddress.setEnabled)
		self.ui.modifyContact.triggered['bool'].connect(self.ui.tickButton.setVisible)
		self.ui.deleteContact.triggered['bool'].connect(self.ui.modifyContact.setChecked)
		self.ui.newContact.triggered['bool'].connect(self.ui.modifyContact.setChecked)
		self.ui.tickButton.clicked.connect(self.ui.modifyContact.trigger)
		self.ui.buttonBox.accepted.connect(self.ui.DialogCreateContact.accept)
		self.ui.buttonBox.rejected.connect(self.ui.DialogCreateContact.reject)
		QtCore.QMetaObject.connectSlotsByName(self.ui.DialogCreateContact)
		self.ui.newContact.triggered.connect(self.showDialog)
		self.ui.listContact.itemClicked.connect(self.getData)
		self.ui.listContact.itemClicked.connect(self.showDetail)
		self.ui.buttonBox.accepted.connect(self.createContact)
		self.mandatoryFields()
		self.ui.eName.textChanged.connect(self.mandatoryFields)
		self.ui.eFirstname.textChanged.connect(self.mandatoryFields)
		self.ui.deleteContact.triggered['bool'].connect(self.delContact)
		self.ui.searchButton.clicked.connect(self.searchContact)
		self.ui.searchBar.textChanged.connect(self.searchContact)
		self.ui.tickButton.clicked.connect(self.modifContact)
		self.ui.exportList.triggered.connect(self.Export)
		self.ui.importList.triggered.connect(self.Import)
		self.ui.utilisation.triggered.connect(self.information)

	def modifContact(self):
		nameCh = self.ui.editName.text()
		firstNameCh = self.ui.editFirstname.text()
		telCh = self.ui.editPhone.text()
		emailCh = self.ui.editMail.text()
		birthdayCh = self.ui.editBirthday.date().toString("yyyy-MM-dd")
		addressCh = self.ui.editAddress.toPlainText()
		self.dba.ModifyRow(nameCh,firstNameCh,telCh, emailCh, birthdayCh, addressCh, self.name, self.firstName)
		self.update()

	def showDialog(self):
		self.ui.eName.clear()
		self.ui.eFirstname.clear()
		self.ui.eTel.clear()
		self.ui.eMail.clear()
		self.ui.eBirthday.setDateTime(QtCore.QDateTime.currentDateTime())
		self.ui.eAddress.clear()

		self.ui.editName.setDisabled(True)
		self.ui.editFirstname.setDisabled(True)
		self.ui.editPhone.setDisabled(True)
		self.ui.editMail.setDisabled(True)
		self.ui.editBirthday.setDisabled(True)
		self.ui.editAddress.setDisabled(True)
		self.ui.tickButton.setHidden(True)

		self.ui.DialogCreateContact.show()

	def mandatoryFields(self):
		if ((self.ui.eName.text() == '') or (self.ui.eFirstname.text() == '')):
			self.ui.buttonBox.button(QtWidgets.QDialogButtonBox.Ok).setEnabled(False)
		else:
			self.ui.buttonBox.button(QtWidgets.QDialogButtonBox.Ok).setEnabled(True)
		
	def showContact(self):
	    data = self.dba.GetColumns()
	    namesList = []
	    listProv = []
	    for item in data:
	    	listProv.append(list(item))
	    for item in listProv:
	    	string = "\t".join(item)
	    	namesList.append(string)

	    for items in namesList:
	    	row = self.ui.listContact.currentRow()
	    	self.ui.listContact.insertItem(row, items)
	    self.ui.listContact.sortItems()
	    
	def getData(self):
		item = self.ui.listContact.selectedItems()
		itemList = []
		for i in list(item):
			itemList.append(str(i.text()))
		itemList = itemList[0].split("\t")
		self.name = itemList[0]
		self.firstName = itemList[1]

	def update(self):
		self.ui.listContact.clear()
		self.showContact()

	def delContact(self):
		self.dba.DeleteEntry(self.name,self.firstName)
		self.ui.editName.setDisabled(True)
		self.ui.editFirstname.setDisabled(True)
		self.ui.editPhone.setDisabled(True)
		self.ui.editMail.setDisabled(True)
		self.ui.editBirthday.setDisabled(True)
		self.ui.editAddress.setDisabled(True)
		self.ui.tickButton.setHidden(True)
		self.ui.editName.clear()
		self.ui.editFirstname.clear()
		self.ui.editPhone.clear()
		self.ui.editMail.clear()
		self.ui.editBirthday.setHidden(True)
		self.ui.editAddress.clear()
		self.update()

	def searchContact(self):
		searchList=[]
		listProv=[]
		text=self.ui.searchBar.toPlainText()
		data=self.dba.SearchBar(text)
		for item in data:
			listProv.append(list(item))
		self.ui.listContact.clear()
		for item in listProv:
			string = "\t".join(item)
			searchList.append(string)
		for item in searchList:
			row=self.ui.listContact.currentRow()
			self.ui.listContact.insertItem(row,item)
		self.ui.listContact.sortItems()

	def showDetail(self):
		data = self.dba.SearchInTable(self.name, self.firstName)
		listProv = []
		for i in data:
			listProv.append(list(i))

		mainList = []
		for i in listProv:
			for j in i:
				mainList.append(j)
		print(mainList)
		date = QtCore.QDate(mainList[5])
		self.ui.editName.setText(mainList[1])
		self.ui.editFirstname.setText(mainList[2])
		self.ui.editPhone.setText(mainList[3])
		self.ui.editMail.setText(mainList[4])
		self.ui.editBirthday.setDate(date)
		self.ui.editBirthday.setVisible(True)
		self.ui.editAddress.setText(mainList[6])

	def createContact(self):
		name = self.ui.eName.text()
		firstName = self.ui.eFirstname.text()
		tel = self.ui.eTel.text()
		mail = self.ui.eMail.text()
		birthday = self.ui.eBirthday.date().toString("yyyy-MM-dd")
		address = self.ui.eAddress.toPlainText()
		self.dba.AddEntryToTable(name,firstName,tel,mail,birthday, address)
		self.update()
		
	def Export(self):
		self.dba.ExportTable()

	def Import(self):
 		filename = QtWidgets.QFileDialog.getOpenFileName(self, "Ouvrir un fichier", "/tmp/")
 		path = filename[0]
 		self.dba.ImportTable(path)
 		self.update()

	def information(self):
 		QtWidgets.QMessageBox.information(self,
 		"Utilisation",
 				"- Ajouter contact\n\
				- Supprimer contact\n\
				- Modifier contact\n\
				- Exporter un annuaire (dans le dossier /tmp)\n\
				- Importer un annuaire (depuis le dossier /tmp)")

if __name__ == '__main__':
	"""Le main : 
 		Au lancement de l'application, on demande à l'utilisateur d'entrer son nom d'utilisateur, 
 		son mot de passe, le nom de la base de donnée et enfin le nom de la table. 
	"""
	app = QtWidgets.QApplication(sys.argv)
	user = input ("Veuillez entrer votre user mySQL : ")
	password = input ("Veuillez entrer votre mot de passe mySQL : ")
	database = input ("Veuillez nommer votre (nouvelle) base de données : ")
	tableName = input ("Veuillez nommer votre table : ")
	
	annuaire = Controller_Annuaire(database, tableName , user, password)
	annuaire.showContact()
	annuaire.show()
	sys.exit(app.exec_())
		


