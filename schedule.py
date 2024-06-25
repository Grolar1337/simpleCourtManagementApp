from sanic import Blueprint, json
from tortoise.exceptions import DoesNotExist
from datetime import datetime
from tortoise.expressions import Q
import pytz

from models import *
from utils import *

schedule = Blueprint("schedule", url_prefix="/schedule")

#@authorized("user")
@schedule.get("/")
async def GetBooking(request):
    year= int(request.args.get("year"))
    month= int(request.args.get("month"))

    start_date = datetime(year, month, 1)
    if month == 12:
        end_date = datetime(year + 1, 1, 1)
    else:
        end_date = datetime(year, month + 1, 1)
    print(str(start_date)+" - "+str(end_date))

    #bookings = await Booking.filter(s_time__gte=start_date, s_time__lt=end_date).all().prefetch_related("court")
    bookings= await Booking.filter(Q(join_type="AND"), Q(s_time__gte=start_date), Q(e_time__lte=end_date)).all()
    courts= await Court.all()
    

    return json({"courts": [court.name for court in courts], "bookings": [{"s_time": str(booking.s_time.isoformat()), "e_time": str(booking.e_time.isoformat()), "note": booking.note} for booking in bookings]})
 
#@authorized("user")
@schedule.post("/")
async def CreateBooking(request):
    date= request.json["date"]
    s_time= request.json["startTime"]
    e_time= request.json["endTime"]
    note= request.json["note"]
    court= request.json["court"]
    

    #print(datetime(int(date["year"]), int(date["month"]), int(date["day"]), int(s_time.split(":")[0]), int(s_time.split(":")[1]), tzinfo=pytz.timezone('Turkey')))
    start_time= datetime(int(date["year"]), int(date["month"])+1, int(date["day"]), int(s_time.split(":")[0]), int(s_time.split(":")[1]), tzinfo= pytz.UTC) - timedelta(hours = 3)
    end_time= datetime(int(date["year"]), int(date["month"])+1, int(date["day"]), int(e_time.split(":")[0]), int(e_time.split(":")[1]), tzinfo= pytz.UTC) - timedelta(hours = 3)

    #bookings= await Booking.filter(s_time__day=start_time.day, s_time__month=start_time.month, s_time__year=start_time.year).all()
    #feature isnt usable with sqlite  

    bookings= await Booking.all()

    for booking in bookings:        
        print(type(start_time))
        print(type(booking.s_time))
        latest_start = max(start_time, booking.s_time)
        earliest_end = min(end_time, booking.e_time)
        overlap = latest_start < earliest_end 
        if overlap: return json({"status":"error", "message": "Bu saatte kort kullanimda. Eger kiralmak isterseniz once digerini silmek icin yonetici ile konusun."}) 

    court_object= await Court.get(name=court)
    await Booking.create(s_time= start_time, e_time= end_time, court=court_object, note=note)
    
    return json({"status":"ok", "message": "Kort kiralandi."})
    

@schedule.delete("/<bookingID:str>")
@authorized("admin")
async def DeleteBooking(request, bookingID):
    booking= await Booking.get(id=bookingID)
    await booking.delete()
    return json({"status":"ok", "message": "Kiralama silindi."})

#@authorized("admin")
@schedule.post("/court")
async def CreateCourt(request):#, token):
    await Court.create(name=request.json["name"])
    return json({"status":"ok", "message": "Kort olusturuldu."})

@schedule.delete("/court/<courtID:str>")
@authorized("admin")
async def DeleteCourt(request, token, courtID):
    court= await Court.get(id=courtID)
    await court.delete()
    return json({"status":"ok", "message": "Kort silindi."})