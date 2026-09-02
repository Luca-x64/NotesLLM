from datetime import datetime as date

dateformat = "%Y-%m-%d %H:%M:%S"

class Note:
    def __init__(self,ID,title,body):
        self.ID = ID
        self.title = title
        self.body = body
        self.date = date.now().strftime(dateformat)

    def update(self,new_title, new_body):
        if (self.title != new_title) or (self.body != new_body):  
            self.title = new_title
            self.body = new_body
            self.date = date.now().strftime(dateformat)

    def __str__(self):
        return f"ID: {self.ID}\nTitle: {self.title}\nBody: {self.body}\nDate: {self.date}"
