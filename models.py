from tortoise import Model, fields
from datetime import datetime
from tortoise.signals import post_save
import bcrypt
import random
import string

salt= "j/1Ui5ToT+-scaI)kT.L(nLi"

class User(Model):
    # fields are null = False by default but i specified it for clarity
    id= fields.UUIDField(pk = True) 
    username= fields.CharField(max_length = 75, unique = True)
    email= fields.CharField(max_length = 200, null = False, unique = True)
    admin= fields.BooleanField()
    password= fields.CharField(max_length=100, null=False)
    invitation= fields.CharField(max_length= 32, null=True)


class Booking(Model):
    id= fields.UUIDField(pk= True)
    note= fields.TextField()
    s_time= fields.DatetimeField(null=False)
    e_time= fields.DatetimeField(null=False)
    court= fields.ForeignKeyField('models.Court', related_name='court', unique=False, null=False )

class Court(Model):
    id= fields.UUIDField(pk= True)
    name= fields.CharField(max_length= 75)

@post_save(User)
async def post_user_save(cls, instance, created, *args, **kwargs):
    if created:
        instance.password= bcrypt.hashpw(instance.password, salt)
        if instance.admin == True: 
            instance.invitation= ''.join(random.choices(string.ascii_uppercase + string.digits, k=16))