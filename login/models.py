from django.db import models

# Create your models here.
class Login(models.Model):
    userid = models.EmailField(primary_key=True)
    category=models.CharField(max_length=50)
    def __str__(self):
        return self.userid+' - '+self.category

class Hall(models.Model):
    hall_incharge_id = models.EmailField()
    hall_incharge_name=models.CharField(max_length=50)
    hall_id=models.CharField(max_length=50,primary_key=True)
    hall_name = models.CharField(max_length=50)
    college=models.CharField(max_length=50)
    def __str__(self):
        return self.hall_id+' - '+self.hall_name+' - '+self.college+' - '+self.hall_incharge_id

class Staff(models.Model):
    userid = models.EmailField(primary_key=True)
    name = models.CharField(max_length=50)
    department = models.CharField(max_length=50)
    college = models.CharField(max_length=50)
    def __str__(self):
        return self.userid+' - '+self.name+' - '+self.department+' - '+self.college

class Hod_Dean(models.Model):
    userid = models.EmailField(primary_key=True)
    name = models.CharField(max_length=50)
    department = models.CharField(max_length=50)
    college = models.CharField(max_length=50)
    position=models.CharField(max_length=50)
    def __str__(self):
        return self.userid+' - '+self.name+'['+self.position+']'+' - '+self.department+' - '+self.college

class Principal(models.Model):
    userid = models.EmailField(primary_key=True)
    name = models.CharField(max_length=50)
    college = models.CharField(max_length=50)
    def __str__(self):
        return self.userid+' - '+self.name+' - '+self.college

class Request(models.Model):
    request_id=models.AutoField(primary_key=True)
    userid= models.EmailField()
    user_name=models.CharField(max_length=50)
    user_designation=models.CharField(max_length=50)
    user_mobile=models.CharField(max_length=10)
    hall_id=models.CharField(max_length=50)
    total_stage=models.CharField(max_length=10)
    current_stage=models.CharField(max_length=10)
    user_dept=models.CharField(max_length=50)
    user_clg=models.CharField(max_length=50)
    booking_date=models.DateField(auto_now=False,auto_now_add=False,default=None)
    date=models.DateField(auto_now=False, auto_now_add=False)
    start_time=models.TimeField(auto_now=False, auto_now_add=False)
    end_time=models.TimeField(auto_now=False, auto_now_add=False)
    function_nature=models.TextField()
    additional_requirements=models.TextField()
    hall_incharge_id = models.EmailField()
    generator_incharge_id = models.EmailField()
    hall_name = models.CharField(max_length=50)
    chief_guest_name=models.CharField(max_length=50,default='unknown')
    chief_guest_detail = models.TextField(default='unknown')
    generator_needed=models.BooleanField(default=False)
    generator_text=models.TextField(default='nothing')
    generator_stage=models.CharField(max_length=50,default='0')
    hod_notes = models.TextField(default='no notes')
    hod_reason = models.TextField(default='no reason')
    dean_notes = models.TextField(default='no notes')
    dean_reason = models.TextField(default='no reason')
    hall_incharge_notes = models.TextField(default='no notes')
    hall_incharge_reason = models.TextField(default='no reason')
    principal_notes = models.TextField(default='no notes')
    principal_reason = models.TextField(default='no reason')
    generator_incharge_notes = models.TextField(default='no notes')
    generator_incharge_reason = models.TextField(default='no reason')
    def __str__(self):
        return str(self.request_id)+' - '+self.userid+' - '+self.hall_id

class Booked(models.Model):
    booking_id=models.AutoField(primary_key=True,default=None)
    request_id=models.PositiveIntegerField()
    userid= models.EmailField()
    user_name=models.CharField(max_length=50)
    user_designation=models.CharField(max_length=50)
    user_mobile=models.CharField(max_length=10)
    hall_id=models.CharField(max_length=50)
    user_dept=models.CharField(max_length=50)
    user_clg=models.CharField(max_length=50)
    booking_date = models.DateField(auto_now=False,auto_now_add=False,default=None)
    date=models.DateField(auto_now=False, auto_now_add=False)
    start_time=models.TimeField(auto_now=False, auto_now_add=False)
    end_time=models.TimeField(auto_now=False, auto_now_add=False)
    function_nature=models.TextField()
    additional_requirements=models.TextField()
    hall_incharge_id = models.EmailField()
    generator_incharge_id=models.EmailField(default=None)
    hall_name = models.CharField(max_length=50,default=None)
    chief_guest_name = models.CharField(max_length=50,default='unknown')
    chief_guest_detail = models.TextField(default='unknown')
    generator_needed = models.BooleanField(default=False)
    generator_text = models.TextField(default='nothing')
    generator_stage = models.CharField(max_length=50,default='0')
    hod_notes = models.TextField(default='no notes')
    hod_reason = models.TextField(default='no reason')
    dean_notes = models.TextField(default='no notes')
    dean_reason = models.TextField(default='no reason')
    hall_incharge_notes = models.TextField(default='no notes')
    hall_incharge_reason = models.TextField(default='no reason')
    principal_notes = models.TextField(default='no notes')
    principal_reason = models.TextField(default='no reason')
    generator_incharge_notes = models.TextField(default='no notes')
    generator_incharge_reason = models.TextField(default='no reason')
    def __str__(self):
        return str(self.booking_id)+' - '+self.userid+' - '+self.hall_id

class Generator_Incharge(models.Model):
    hall_id = models.CharField(max_length=50, primary_key=True)
    hall_name = models.CharField(max_length=50)
    college = models.CharField(max_length=50)
    generator_incharge_id = models.EmailField(default=None)
    generator_incharge_name = models.CharField(max_length=50)
    def __str__(self):
        return self.generator_incharge_id+' - '+self.generator_incharge_name+' - '+self.hall_id

