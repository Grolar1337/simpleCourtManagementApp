from sanic import Blueprint, json
from tortoise.exceptions import DoesNotExist

from models import *
from utils import *

schedule = Blueprint("schedule", url_prefix="/schedule")


@schedule.get("/")
@authorized("user")
async def GetBooking(request):
    year= request.get("year")
    month= request.get("month")

    start_date = datetime(year, month, 1)
    if month == 12:
        end_date = datetime(year + 1, 1, 1)
    else:
        end_date = datetime(year, month + 1, 1)

    bookings = await Booking.filter(s_time__gte=start_date, s_time__lt=end_date).all().prefetch_related("court")
    return json({"bookings": [{"s_time": booking.s_time, "e_time": booking.e_time, "note": booking.note} for booking in bookings]})
 

@schedule.post("/")
@authorized("user")
async def CreateBooking(request):
    overlapping_events = await Booking.filter((Q(start_time__lte=request.json["e_time"]) & Q(end_time__gte=request.json["s_time"]))).all()
    if len(overlapping_events) == 0:
        await Booking.create(**request.json)
        return json({"status":"ok", "message": "Kort kiralandi."})
    return json({"status":"error", "message": "Bu saatte kort kullanimda. Eger kiralmak isterseniz once digerini silmek icin yonetici ile konusun."})

@schedule.delete("/<bookingID:str>")
@authorized("admin")
async def DeleteBooking(request, bookingID):
    booking= await Booking.get(id=bookingID)
    await booking.delete()
    return json({"status":"ok", "message": "Kiralama silindi."})


@schedule.post("/court")
@authorized("admin")
async def CreateCourt(request):
    await Court.create(name=request.json["name"])
    return json({"status":"ok", "message": "Kort olusturuldu."})

@schedule.delete("/court/<courtID:str>")
@authorized("admin")
async def DeleteCourt(request, courtID):
    court= await Court.get(id=courtID)
    await court.delete()
    return json({"status":"ok", "message": "Kort silindi."})