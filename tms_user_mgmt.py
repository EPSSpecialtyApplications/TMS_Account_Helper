import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from config import TMS_PRD_CONNECT as CNXN
from mappy.client import Client
from datetime import datetime
from tms_data_config import TMSDefaults
import pyodbc
import logging

COLBY_KING = 1311
RECORD_DEFAULTS = {
    'DateCreated': datetime.now(),
    'DateUpdated': datetime.now(),
    'IDUserCreated': COLBY_KING,
    'IDUserUpdated':  COLBY_KING,
}
CREATED_DEFAULTS = {
    'DateCreated': datetime.now(),
    'DateUpdated': datetime.now()	
}

class TMSUserMGMTApp(object):

	def __init__(self):
		self.__window = tk.Tk()
		self.__cnxn_str = CNXN
		self.mappy = Client(self.__cnxn_str)
		self.__window.title('TMS User Management')
		self.__top = tk.Frame(self.__window)
		self.__bottom =tk.Frame(self.__window)
		self.__top_frame = tk.Frame(self.__top)
		self.__left_frame = tk.Frame(self.__top)
		self.__right_frame = tk.Frame(self.__top)
		self.__bottom_frame = tk.Frame(self.__bottom)
		self.__top_frame.pack(side=tk.TOP)
		self.__left_frame.pack(side=tk.LEFT)
		self.__right_frame.pack(side=tk.LEFT)
		self.__bottom_frame.pack(side=tk.LEFT)
		self.__top.pack()
		self.__bottom.pack()

		self.FORM_FIELDS = (
			'Segment',
			'Resource #',
			'Email',
			'PagerEmail',
			'FirstName',
			'LastName'
		)

		self.FORM_DROPDOWN_FIELDS = (
			'TMSUserGroup',
			'UserSkill',
			'UserAccount',
			'MobileProfileWOQuery',
			'MobileProfileAssetQuery'
		)

		self.CHECK_BOXES = (
			'Resource',
			'Mobile Profile'
		)

		self.BUTTONS = (
			'Submit',
			'Exit',
			'Clear'
		)

		logging.basicConfig(filename='TMS User Management.log', filemode='a', level=logging.DEBUG)
		self.__app_logger = logging.getLogger('TMS User Management')

		self.__values_lookup = {}

		self.__forms = self.build_input_forms(self.__left_frame)
		self.__dropdowns = self.build_dropdowns(self.__right_frame)
		self.__checkboxes = self.build_checkboxes(self.__right_frame)
		self.__buttons = self.build_buttons(self.__bottom_frame)


	def start(self):
		tk.mainloop()

	def lookup_segment_id(self, segment):
		segment = segment.strip()
		if segment.isnumeric():
			segment = int(segment)
			if segment in TMSDefaults.SEGMENT_IDS:
				return segment
		else:
			segment = segment.upper()
			try:
				segment = TMSDefaults.SEGMENTS[segment]
				return segment
			except KeyError:
				pass
		return None

	def update_with_segment_data(self, sv):
		try:
			segment = sv.get()
			segment_id = self.lookup_segment_id(segment)
			if segment_id:
				try:
					self._filter_user_groups(segment_id)
					self._filter_skills(segment_id)
					self.__filter_accounts(segment_id)
					self.__filter_wo_query(segment_id)
					self.__filter_asset_query(segment_id)
				except pyodbc.Error as e:
					messagebox.showerror("Error", "An error occured while getting form data")
					print(e)

		except tk.TclError:
			pass

	def __filter_asset_query(self, segment_id):
		queries_data = self.mappy.query(
			"""SELECT TOP 10 SQ.Name, MP.IDAssetQuery, COUNT(*)
				FROM tblTMSMobileProfiles MP
					JOIN tblStoredQuery SQ ON MP.IDAssetQuery = SQ.IDStoredQuery
				WHERE MP.IDSegment = ?
				GROUP BY SQ.Name,
						 MP.IDAssetQuery
				ORDER BY COUNT(*) DESC""",
			segment_id
		)
		queries = [record['Name'] for record in queries_data]
		self.__dropdowns['MobileProfileAssetQuery']['values'] = queries
		self.__dropdowns['MobileProfileAssetQuery'].delete(0, 'end')
		self.__values_lookup['MobileProfileAssetQuery'] = {record['Name']: record for record in queries_data}

	def __filter_wo_query(self, segment_id):
		queries_data = self.mappy.query(
			"""SELECT TOP 10 SQ.Name, MP.IDWOQuery, COUNT(*)
				FROM tblTMSMobileProfiles MP
					JOIN tblStoredQuery SQ ON MP.IDWOQuery = SQ.IDStoredQuery
				WHERE MP.IDSegment = ?
				GROUP BY SQ.Name,
						 MP.IDWOQuery
				ORDER BY COUNT(*) DESC""",
			segment_id
		)
		queries = [record['Name'] for record in queries_data]
		self.__dropdowns['MobileProfileWOQuery']['values'] = queries
		self.__dropdowns['MobileProfileWOQuery'].delete(0, 'end')
		self.__values_lookup['MobileProfileWOQuery'] = {record['Name']: record for record in queries_data}

	def _filter_user_groups(self, segment_id):
		groups = self.mappy.query(
			"""SELECT GroupName, IDTMSGroup 
			   FROM tblTMSGroups 
			   WHERE IDSegment = ?""", 
			segment_id
		)
		groups = [record['GroupName'] for record in groups]
		groups.sort()
		self.__dropdowns['TMSUserGroup']['values'] = groups
		self.__dropdowns['TMSUserGroup'].delete(0, 'end')

	def _filter_user_groups(self, segment_id):
		groups_data = self.mappy.query(
			"""SELECT GroupName, IDTMSGroup 
			   FROM tblTMSGroups 
			   WHERE IDSegment = ?""", 
			segment_id
		)
		
		groups = [record['GroupName'] for record in groups_data]
		groups.sort()
		self.__dropdowns['TMSUserGroup']['values'] = groups
		self.__dropdowns['TMSUserGroup'].delete(0, 'end')
		self.__values_lookup['TMSUserGroup'] = {record['GroupName']: record for record in groups_data}

	def _filter_skills(self, segment_id):
		skills_data = self.mappy.query(
			"""SELECT IDSkill, Description 
			   FROM tblSkillCodes 
			   WHERE IDSegment = ? AND Show = 1 AND ShowInQuery = 1""", 
			segment_id
		)
		
		skills = [record['Description'] for record in skills_data]
		skills.sort()
		self.__dropdowns['UserSkill']['values'] = skills
		self.__dropdowns['UserSkill'].delete(0, 'end')
		self.__values_lookup['UserSkill'] = {record['Description']: record for record in skills_data}

	def __filter_accounts(self, segment_id):
		acct_data = self.mappy.query(
			"""SELECT TOP 10 R.IDAccount, ACCT.Description, COUNT(*) AS ct
				FROM tblResources R
					JOIN tblAccountCodes ACCT ON R.IDAccount = ACCT.IDAccount
				WHERE IDStatus = 10 AND R.IDSegment = ?
				GROUP BY R.IDAccount, ACCT.Description
				ORDER BY COUNT(*) DESC""", 
			segment_id
		)
		
		accounts = [record['Description'] for record in acct_data]
		self.__dropdowns['UserAccount']['values'] = accounts
		self.__dropdowns['UserAccount'].delete(0, 'end')
		self.__values_lookup['UserAccount'] = {record['Description']: record for record in acct_data}

	def build_input_forms(self, frame):
		entries = {}

		for field in self.FORM_FIELDS:
			row = tk.Frame(frame)
			label = tk.Label(row, width=22, text=field, anchor='w')
			sv = None
			if field == 'Segment':
				sv = tk.StringVar()
				sv.trace('w', lambda name, index, mode, sv=sv: self.update_with_segment_data(sv))
			entry = tk.Entry(row, width=45, textvariable=sv)
			entry.insert(0, '0')
			row.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)
			label.pack(side=tk.LEFT)
			entry.pack(side=tk.RIGHT, expand=tk.YES, fill=tk.X)
			entries[field] = entry

		return entries

	def build_dropdowns(self, parent):

		dropdowns = {}
		for field in self.FORM_DROPDOWN_FIELDS:
			row = tk.Frame(parent)
			label = tk.Label(row, width=22, text=field, anchor='w')
			dropdown = ttk.Combobox(row, width=45, textvariable=tk.StringVar()) 
			label.pack()
			label.grid(column=0, row=0)
			dropdown.grid(column=1, row=0)
			row.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)
			dropdowns[field] = dropdown
		
		return dropdowns

	def build_checkboxes(self, parent):
		checks = {}
		for field in self.CHECK_BOXES:
			row = tk.Frame(parent)
			label = tk.Label(row, width=22, text=field, anchor='w')
			var = tk.IntVar()
			cb = tk.Checkbutton(row, text=field, variable=var, onvalue=1, offvalue=0)
			label.grid(row=0, column=0)
			cb.grid(row=0, column=1)
			checks[field] = var
			row.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)

		return checks

	def quit_command(self):
		self.__window.destroy()

	def __create_resource(self, data):
		resource = {
			'IDSegment': data['IDSegment'],
			'ResourceNumber': data['ResourceNumber'],
			'IDType': 58,
			'FirstName': data['FirstName'].upper(),
			'LastName': data['LastName'].upper(),
			'IDAccount': data['IDAccount'],
			'IDSkill': data['IDSkill'],
			'StartDate': datetime.now(),
			'ChargeRate': 0.0,
			'IDStatus': 10,
			'Email': data['Email'],
			'PagerEmail': data['PagerEmail'],
		}
		resource.update(RECORD_DEFAULTS)
		tblResources = self.mappy.get_table('tblResources')
		print('Creating Resource...')
		print(resource)
		tblResources.add(**resource)
		tblResources.execute()
		return tblResources.get_last_insert_id()


	def __create_user_account(self, data, resource_id=None, tms_group_id=None):
		user = {
			'IDSegment': 0,
			'UserName': (data['LastName'].lower().capitalize() + ', ' + data['FirstName'].lower().capitalize()),
			'UserIdent': (data['FirstName'].lower().capitalize() + ' ' + data['LastName'].lower().capitalize()),
			'IDTMSGroup': None,
			'Disabled': 0,
			'IDResource': resource_id,
			'MustChangePassword': 0,
			'NoChangePassword': 0,
			'NeverExpirePassword': 0,
			'DefaultResource': 1,
			'AssignResource': 1
		}
		user.update(CREATED_DEFAULTS)
		tblTMSUsers = self.mappy.get_table('tblTMSUsers')
		tblTMSUsers.add(**user)
		tblTMSUsers.execute()
		user_id = tblTMSUsers.get_last_insert_id()

		tblTMSGroupUsers = self.mappy.get_table('tblTMSGroupUsers')
		tblTMSGroupUsers.add(IDUser=user_id, IDTMSGroup=tms_group_id, **CREATED_DEFAULTS)
		tblTMSGroupUsers.execute()

		self.mappy.execute_sql(
			"UPDATE tblTMSUsers SET IDTMSGroup = ? WHERE IDUser = ?",
			tms_group_id,
			user_id
		)
		return user_id


	def __create_mobile_profile(self, data, user_id, resource_id):
		"""Creates Mobile Profile record in tmsenterprise.TMSMobileProfiles"""
		mp_data = {
			'IDSegment': data['IDSegment'],
			'Name': (data['LastName'].lower().capitalize() + ', ' + data['FirstName'].lower().capitalize()),
			'IDUser': user_id,
			'IDResource': resource_id,
			'IDWOQuery': data['IDWOQuery'],
			'IDAssetQuery': data['IDAssetQuery'],
		}
		mp_data.update(TMSDefaults.MOBILE_PROFILE_DEFAULTS)
		tblTMSMobileProfiles = self.mappy.get_table('tblTMSMobileProfiles')
		tblTMSMobileProfiles.add(**mp_data)
		tblTMSMobileProfiles.execute()
		mp_id = tblTMSMobileProfiles.get_last_insert_id()
		return mp_id

	def clear_input_forms(self):
		for name, form in self.__forms.items():
			form.delete(0, 'end')

	def __submit_user(self, data, make_resource, make_mobile_profile):
		resource_id = None
		user_id = None
		mp_id = None

		try:
			if make_resource:
				resource_id = self.__create_resource(data)
				self.__app_logger.info('{}: Created resource: {}'.format(data['Email'], resource_id))

			user_id = self.__create_user_account(data, resource_id, data['IDTMSGroup'])
			self.__app_logger.info('{}: Created User: {}'.format(data['Email'], user_id))

			if make_mobile_profile:
				mp_id = self.__create_mobile_profile(data, user_id, resource_id)
				self.__app_logger.info('{}: Created resource: {}'.format(data['Email'], mp_id))
		except pyodbc.Error as e:
			messagebox.showerror("Error", "A database error occured while trying to create the user")
			print(e)

		self.clear_input_forms()





	def submit_command(self):
		""" Code that runs after hitting the submit button"""

		data = {}
		make_resource = self.__checkboxes['Resource'].get()
		make_mobile_profile = self.__checkboxes['Mobile Profile'].get()
		submit_error = False
		
		# Gather data to create user
		try:
			data['IDSegment'] = self.lookup_segment_id(self.__forms['Segment'].get())
			data['FirstName'] = self.__forms['FirstName'].get()
			data['LastName'] = self.__forms['LastName'].get()
			data['IDTMSGroup'] = self.__values_lookup['TMSUserGroup'][self.__dropdowns['TMSUserGroup'].get()]['IDTMSGroup']
			data['Email'] = self.__forms['Email'].get()
			if not data['IDSegment']:
				messagebox.showerror('Error', 'Invalid segment')
				return

		except KeyError as e:
			print(e)
			messagebox.showerror('Error', 'Can''t Create user without a Segment, name and group')
			return

		# Gather data to create resource
		try:
			data['ResourceNumber'] = self.__forms['Resource #'].get()
			data['PagerEmail'] = self.__forms['PagerEmail'].get()			
			data['IDAccount'] = self.__values_lookup['UserAccount'][self.__dropdowns['UserAccount'].get()]['IDAccount']
			data['IDSkill'] = self.__values_lookup['UserSkill'][self.__dropdowns['UserSkill'].get()]['IDSkill']
		except ValueError as e:		
			messagebox.showerror('Error', 'Cant create a resource without Resource #, email, pager, account, and skill')
			return

		# Gather data to create mobile profile 
		try:
			data['IDWOQuery'] = self.__values_lookup['MobileProfileWOQuery'][self.__dropdowns['MobileProfileWOQuery'].get()]['IDWOQuery']
			data['IDAssetQuery'] = self.__values_lookup['MobileProfileAssetQuery'][self.__dropdowns['MobileProfileAssetQuery'].get()]['IDAssetQuery']
		except ValueError as e:
			messagebox.showerror('Error', 'Cant create a mobile profile without WOQuery and Asset forms')
			return

		self.__submit_user(data, make_resource, make_mobile_profile)


	def build_buttons(self, parent):
		row = tk.Frame(parent)
		quit_btn = tk.Button(row, text='Quit', command=self.quit_command)
		submit_btn = tk.Button(row, text='Submit', command=self.submit_command)
		submit_btn.grid(row=0, column=1)
		quit_btn.grid(row=0, column=0)
		row.pack()


	def build_input_component(self, container, input_label, input_type):
		"""Build the top frames of the window for being able to enter data."""
		label = tk.Label(container, text=input_label, width=15, anchor=tk.W)
		input_widget = tk.Entry(container, textvariable=input_type, width=30)
		label.pack(side='left')
		input_widget.pack(side='left')

def main():
	app = TMSUserMGMTApp()
	app.start()

if __name__ == '__main__':
	main()