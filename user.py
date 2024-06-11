from sanic import Blueprint, json, html
import bcrypt
import random
import string

from models import User, salt
from utils import *

user = Blueprint("user", url_prefix="")




@user.post('/login')
async def Login(request):
    email= request.json.get("email")
    password= request.json.get("password")
    
    user= User.get_or_none(email=email)

    if not user: return json({"status":"error", "message": "Email bulunamadı"})

    if bcrypt.checkpw(password.encode(), user.password):
        r = html('''
                                        <!DOCTYPE html>
                                            <html>
                                            <body>
                                            <h2>Using JavaScript to redirect a webpage after 5 seconds </h2>
                                            <p id = "result"></p>
                                            <button onclick = "redirect()">Click to Redirect to Tutorials Point</button>
                                            <script>
                                                function redirect () {
                                                    setTimeout(myURL, 5000);
                                                    var result = document.getElementById("result");
                                                    result.innerHTML = "<b> The page will redirect after delay of 5 seconds";
                                                }

                                                function myURL() {
                                                    document.location.href = "https://app.basecoll.link/";
                                                }
                                            </script>
                                            </body>
                                        </html>
                                  ''')
        expiration=525000 #(minutes) 1~ year 
        r.add_cookie(
            "jwt",
            encodeJWT({"id": str(user.id), "email": user.email, "admin": user.admin},expiration),
            domain="api.basecoll.link",
            httponly=True,
            samesite="none"
        )
        return json(r)


@user.post("/register")
async def Register(request):
    email= request.json.get("email")
    password= request.json.get("password")
    username= request.json.get("username")
    invitation= request.json.get("invitation")

    user= await User.get_or_none(email=email)
    if user: return json({"status":"error", "message": "Email bir hesaba kayitli."})

    validator = Validator(email, username, password)
    result = validator.validate()
    if not result['username']: return json({"status":"error", "message": "Isminiz sadece harf ve sayi icerebilir."})
    if not result['email']: return json({"status":"error", "message": "Gecersiz e-posta adresi girdiniz."})
    if not result['password']: return json({"status":"error", "message": "Şifreniz en az 8 karakter uzunluğunda olmali ve en az bir harf ile bir rakam içermeli."})

    if user.config.ADMIN_CODE == invitation:
        await User.create(email=email, username=username, password=password)
        return json({"status":"ok", "message": "Başarıyla admin olarak kayit oldunuz."})

    user= await User.get_or_none(invitation=invitation)
    if not user: return json({"status":"error", "message": "Davet kodunuz gecersiz."})
    else: await user(invitation=''.join(random.choices(string.ascii_uppercase + string.digits, k=16))).save()

    await User.create(email=email, username=username, password=password)

    return json({"status":"ok", "message": "Başarıyla kayit oldunuz"})



@user.put("/user/<userID:str>")
@authorized("user")
async def Update(request, token, userID):
    
    if userID==token["id"] or token["admin"]: user = await User.get_or_none(id=userID)

    if user:
        if "password" in request.json.keys():
            if bcrypt.checkpw(request.json["old password"].encode(), user.password): 
                request.json["password"] == bcrypt.hashpw(request.json["password"], salt) 
            else:
                return json({"status": "error", "message": "Eski sifre hatali"}, status=404)        
        await user.update_from_dict(request.json).save()
        
        return json({"status": "ok", "message": "Bilgiler basariyla guncellendi"})
    else:
        return json({"status": "error", "message": "Problem yasandi"}, status=404)
